# 使用官方的 python 3.9.18 镜像作为基础镜像
FROM python:3.9.18

# ARG
ARG OPENAI_API_KEY

# 設置環境變量
ENV OPENAI_API_KEY=$OPENAI_API_KEY 
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录为 /app
WORKDIR /app

# 将当前目录内容复制到容器的 /app 目录中
COPY . /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 升級 pip
RUN pip install --upgrade pip

# 使用 pip 安装 requirements.txt 中的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口8000（根據您的 CMD 命令，應該是 8000 而不是 80）
EXPOSE 8000

# 指定容器启动时执行的命令
CMD ["streamlit", "run", "ID_identification.py", "--server.address", "0.0.0.0", "--server.port", "8000", "--server.enableXsrfProtection", "false"]
