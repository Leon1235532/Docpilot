<a id="readme-top"></a>

<br />
<div align="center">

<h3 align="center">Docpilot</h1>

  <p align="center">
    基于 FastAPI + LLM 的 AI 文档问答平台，支持文档智能摘要与 RAG 检索增强问答
    <br />
    <a href="https://github.com/Leon1235532/Docpilot"><strong>Explore the docs »</strong></a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Docpilot 是一个面向医学文献的 AI 文档问答平台。用户上传 PDF 文档后，系统自动完成向量化入库，支持基于 RAG 的语义检索问答和 AI 结构化摘要生成。

核心流程：

1. PDF 上传 → 文档切片 → Chroma 向量化存储
2. 用户提问 → 意图识别（医学/闲聊分流）→ RAG 检索 → LLM 结构化回答
3. 多轮对话上下文压缩，支持连续追问

### Built With

![Tech Stack](https://skillicons.dev/icons?i=fastapi,python,mysql,redis,docker)

LangChain · Chroma



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.8+

### Installation

1. 克隆仓库
   ```sh
   git clone https://github.com/Leon1235532/Docpilot.git
   ```
2. 配置环境变量
   ```sh
   cp .env.example .env
   # 编辑 .env，填入 API Key 和数据库密码
   ```
3. Docker Compose 启动全部服务
   ```sh
   docker-compose up -d
   ```

项目包含 4 个容器：MySQL、Redis、FastAPI 后端、Streamlit 前端。



<!-- USAGE -->
## Usage

### 启动后访问

| 服务 | 地址 |
|------|------|
| FastAPI API | `http://localhost:8000` |
| Swagger 文档 | `http://localhost:8000/docs` |
| Streamlit 前端 | `http://localhost:8501` |

### 功能示例

- **文档上传**：上传 PDF 后自动切片并向量化存入 Chroma
- **AI 摘要**：对文档内容调用 LLM 生成结构化摘要（核心结论、关键细节、注意事项）
- **RAG 问答**：基于医学文献检索，MMR 策略平衡相关性与多样性
- **意图路由**：自动区分医学专业提问与日常闲聊，分别走不同管线

### 项目结构

```
Docpilot/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── models.py            # Tortoise ORM 模型
│   ├── schemas.py           # Pydantic 结构化输出定义
│   ├── llm_config.py        # LLM 配置
│   └── requirements.txt     # Python 依赖
├── frontend/
│   └── app.py               # Streamlit 前端
├── docker-compose.yml       # 多容器编排
├── Dockerfile               # 后端构建镜像
├── .env.example             # 环境变量模板
└── .dockerignore
```



<!-- CONTACT -->
## Contact

Leon1235532 - xzr12367@126.com

Project Link: [https://github.com/Leon1235532/Docpilot](https://github.com/Leon1235532/Docpilot)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
