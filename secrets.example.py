#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
敏感信息配置文件示例
请复制此文件为 secrets.py 并填入正确的配置信息
"""

# OpenAI API 配置
# 请在此处填入你的API密钥
OPENAI_API_KEY = "your_api_key_here"

# 请在此处填入你的API服务地址
OPENAI_BASE_URL = "https://api.openai.com/v1"

# 模型配置
# 可选模型：gpt-3.5-turbo, gpt-4, claude-3-sonnet, GLM-4, Kimi-K2-0905 等
DEFAULT_MODEL = "gpt-3.5-turbo"

# 其他敏感配置示例（根据需要取消注释并填入）
# DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
# REDIS_URL = "redis://localhost:6379/0"
# SECRET_KEY = "your_flask_secret_key_here"
# EMAIL_PASSWORD = "your_email_password_here"
# AWS_ACCESS_KEY = "your_aws_access_key_here"
# AWS_SECRET_KEY = "your_aws_secret_key_here"