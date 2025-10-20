"""
配置文件 - 存储API密钥和其他配置信息
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-apikey")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 其他配置
MAX_RETRIES = 2
MAX_TOKENS = 1000
TEMPERATURE = 0.1
