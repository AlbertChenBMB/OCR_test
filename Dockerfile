# 使用官方的 python 3.9.18 镜像作为基础镜像
FROM python:3.9.18
# ARG
ARG OPENAI_API_KEY

# 切換到 root 用戶以執行需要 root 權限的命令.
USER root

# 設置環境變量
ENV OPENAI_API_KEY=$OPENAI_API_KEY 

# 设置工作目录为 /app
WORKDIR /app

# 将当前目录内容复制到容器的 /app 目录中
COPY . /app

# 使用 pip 安装 requirements.txt 中的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口80
EXPOSE 80

# 指定容器启动时执行的命令
CMD ["streamlit", "run", "ID_identification.py", "--server.address", "0.0.0.0", "--server.port", "8000"]  # 请替换为你应用的主脚本文件名
