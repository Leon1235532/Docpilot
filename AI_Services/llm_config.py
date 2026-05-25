from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI,OpenAIEmbeddings

load_dotenv()
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    model="deepseek-v4-flash"
)

my_embedding = OpenAIEmbeddings(
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url=os.getenv("ZHIPU_BASE_URL"),
        model="Embedding-3"
    )
