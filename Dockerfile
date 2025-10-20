# 使用Python 3.11 slim bookworm镜像，针对M4芯片的arm64架构优化
FROM python:3.11-slim-bookworm

# 设置工作目录
WORKDIR /app

# 安装pip-tools用于依赖管理
RUN pip install --no-cache-dir pip-tools

# 复制依赖文件并安装
COPY requirements.in requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建上传目录
RUN mkdir -p /app/uploads/papers

# 暴露端口
EXPOSE 8000

# 启动Django开发服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
