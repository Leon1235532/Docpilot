# ai_service.py
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from models import TokenLog, User

# 加载 .env 变量
load_dotenv()

# 初始化 DeepSeek 客户端
client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

# 设定单次请求的硬性限制
SINGLE_REQUEST_TOKEN_LIMIT = 50000

def estimate_tokens(text: str) -> int:
    """粗略估算 Token,汉字按 1.5 算，英文按 0.5 算"""
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return int((chinese_chars * 1.5) + (other_chars * 0.5))

async def generate_doc_summary(user: User, content: str) -> str:
    # 1. 前置拦截：预估 Token
    estimated_input = estimate_tokens(content) + 30  # 加上提示词的消耗
    if estimated_input > SINGLE_REQUEST_TOKEN_LIMIT:
        raise ValueError(f"文档过长！预估消耗 {estimated_input} Tokens,超过了系统 {SINGLE_REQUEST_TOKEN_LIMIT} 的限制。")

    # 2. 调用大模型
    response = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "你是一个专业的文档分析助手，请为用户提供准确、简洁的摘要。"},
            {"role": "user", "content": f"请为以下内容生成 100 字以内的摘要：\n\n{content}"}
        ],
        max_tokens=500,  # 强制限制 AI 的输出长度，防止 Token 爆炸
        stream=False
    )

    summary_text = response.choices[0].message.content
    usage = response.usage

    # 3. 异步记录真实消耗到数据库
    await TokenLog.create(
        user=user,
        action="summary",
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens
    )
    return summary_text