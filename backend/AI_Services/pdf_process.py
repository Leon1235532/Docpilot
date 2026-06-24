from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from AI_Services.llm_config import my_embedding

# 将指定路径的pdf 加载、切分、向量化存入chroma
def process_and_store_pdf(file_path: str, filename: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    # 为了防止不同文档混淆，给每一页强行打上来源标签
    for doc in docs:
        doc.metadata["source"] = filename 

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
    )
    chunks = text_splitter.split_documents(docs)
    # 4. 存入本地 Chroma 数据库
    # 注意：这里不用 from_documents 重新建库，而是用 add_documents 追加数据！
    db = Chroma(
        persist_directory="../chroma_db", 
        embedding_function=my_embedding
    )
    db.add_documents(chunks)
    return len(chunks)