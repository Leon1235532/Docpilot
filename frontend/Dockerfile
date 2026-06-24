# 1. 使用极其轻量级的 Python 3.10 官方镜像作为基础环境
FROM python:3.10-slim

# 2. 在容器内部创建一个叫 /app 的工作文件夹
WORKDIR /app

# 3. 把本地的 requirements.txt 复制到容器的 /app 里
COPY requirements.txt .

# 4. 在容器里安装这些 Python 依赖包（使用清华源加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 把你本地所有的代码文件（main.py 等）全部复制到容器里
COPY . .

# 6. 声明 Streamlit 默认的对外端口
EXPOSE 8501

# 7. 容器启动时的核心执行命令
CMD ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]