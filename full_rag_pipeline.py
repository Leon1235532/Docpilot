from langchain_community.document_loaders import TextLoader
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from typing import List
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import os
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import JsonOutputParser
from pprint import pprint

load_dotenv()
class Response_limit(BaseModel):
    symptoms : List[str]
    high_risk_factors : List[str]
    preventions : List[str]

llm = ChatOpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = os.getenv("DEEPSEEK_BASE_URL"),
    model = "deepseek-v4-flash"
)

parser = JsonOutputParser(pydantic_object=Response_limit)
prompt = ChatPromptTemplate([
    ("system","你是一个极其严谨的医学提取助手。你必须严格遵守以下格式要求：\n{format_instructions}"),
    ("human","这是知识库的参考资料：{content}\n请回答问题:{question}")
])

Text_Loader = TextLoader(file_path= "./delirium_material.txt",encoding="utf-8")
text = Text_Loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 300,
    chunk_overlap = 50,
)
docs = text_splitter.split_documents(text)

my_embedding = OpenAIEmbeddings(
    api_key = os.getenv("ZHIPU_API_KEY"),
    base_url = os.getenv("ZHIPU_BASE_URL"),
    model = "Embedding-3"
)

db = Chroma.from_documents(
    documents = docs,
    embedding = my_embedding,
    persist_directory = "./chroma/chroma_2"
)
retriever = db.as_retriever(
    search_type = "mmr",
    search_kwargs = {
        "fetch_k":5
    }
)
ret_query = retriever.invoke("患者发作时的具体表现;包含易感人群的特征;包含具体的护理预防措施")
chain = prompt | llm | parser
output = chain.invoke({
    "format_instructions" : parser.get_format_instructions(),
    "content": ret_query,
    "question" : "请根据文档，总结心脏术后谵妄的临床表现、哪些人容易得，以及应该怎么预防？"
})
pprint(output)