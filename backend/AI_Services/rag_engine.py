import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser,StrOutputParser
from schemas import Response_Limit
from langchain_classic.memory.summary_buffer import ConversationSummaryBufferMemory
from models import ChatHistory
from AI_Services.llm_config import llm,my_embedding

parser = JsonOutputParser(pydantic_object=Response_Limit)

# ================= 意图识别交警 =================llm输出问题类型
def check_intent(question: str) -> str:
    """
    让大模型自己判断用户的意图：是医学问题，还是日常闲聊？
    """
    intent_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个极其精准的意图识别路由。请判断用户的输入是否属于'医学/护理专业提问'或'需要查阅医学文献'。\n"
                   "如果是医学专业问题,请严格且仅输出单词:medical\n"
                   "如果是日常打招呼、闲聊、问候(如'你是谁'),请严格且仅输出单词:chat"),
        ("human", "用户输入：{question}")
    ])
    
    # 这里用普通的字符串解析器，不需要 Pydantic
    chain = intent_prompt | llm | StrOutputParser()
    result = chain.invoke({"question": question})
    return result.strip().lower()

# ================= 4. 终极问答引擎 (带记忆 + RAG) =================
# PDF已经过pdf_process函数处理存到chroma，故只需检索即可。
async def chat_with_doc(user_id: int, doc_id: int, user_question: str):  
    """接收问题，融合记忆与文献，返回最终答案并落库"""
    intent = check_intent(user_question)
    # 2. 唤醒并压缩记忆
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=1000, return_messages=True)
    records = await ChatHistory.filter(user_id=user_id, doc_id=doc_id).order_by("created_at").limit(20)

    for record in records:
        if record.role == "human":
            memory.chat_memory.add_user_message(record.content)
        elif record.role == "ai":
            memory.chat_memory.add_ai_message(record.content)
            
    processed_history = memory.load_memory_variables({}).get("history", [])     # 消息列表

    # 3. 路由分发大模型管线
    if "medical" in intent:
        # 【路线 A：医学文献 + 记忆】
        db = Chroma(persist_directory="../chroma_db", embedding_function=my_embedding)
        retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 10})
        docs = retriever.invoke(user_question)
        formatted_context = "\n\n".join([doc.page_content for doc in docs])

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个极其严谨的医学提取助手。你必须严格遵守以下格式要求：\n{format_instructions}"),
            MessagesPlaceholder(variable_name="history"), 
            ("human", "这是知识库的参考资料：\n{context}\n\n请回答问题:{question}")
        ])
        
        chain = prompt_template | llm | parser
        ai_response_dict = await chain.ainvoke({
            "format_instructions": parser.get_format_instructions(),
            "history": processed_history,
            "context": formatted_context,
            "question": user_question
        })
        # 将字典输出为json文本字符串
        ai_response_str = json.dumps(ai_response_dict, ensure_ascii=False)
        ui_type = "medical_card"
        final_data = ai_response_dict 
        
    else:
        # 【路线 B：普通闲聊 + 记忆】
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是 DocPilot 智能临床文档助手。请用友善、简短的语言回答。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])
        
        chain = chat_prompt | llm | StrOutputParser()
        ai_response_str = await chain.ainvoke({
            "history": processed_history,
            "question": user_question
        })
        
        ui_type = "normal_chat"
        final_data = ai_response_str 

    # 4. 新对话落库
    await ChatHistory.create(user_id=user_id, doc_id=doc_id, role="human", content=user_question)
    await ChatHistory.create(user_id=user_id, doc_id=doc_id, role="ai", content=ai_response_str)
    
    # 5. 返回结果
    if ui_type == "medical_card":
        return {"ui_type": "medical_card", "data": final_data}
    else:
        return {"ui_type": "normal_chat", "content": final_data}