#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import openai
import os
from datetime import datetime
import time

# 导入配置文件
try:
    from secrets import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL
except ImportError:
    print("错误：找不到 secrets.py 配置文件")
    print("请复制 secrets.example.py 为 secrets.py 并填入正确的配置信息")
    exit(1)

def get_webpage_content(url):
    """获取网页HTML内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"获取网页内容失败: {e}")
        return None

def summarize_with_llm(html_content, api_key=None):
    """使用LLM总结网页内容"""
    try:
        # 使用配置文件中的API密钥和base_url
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )

        prompt = f"""
请分析以下HTML内容，提取并总结其中的电报新闻内容。
要求：
1. 只关注新闻内容，忽略导航、广告等无关信息
3. 用markdown格式输出
4. 将每条新闻总结为一句话突出重点，最好不要超过20字
5. 按行业归类输出
6. 重点关注“人工智能”，“算力”,“央行”，“国家政策”，“政策会议”，“金融会议”，“海外投行”，这些新闻标红输出

大致输出模板：
## 行业名称
- 新闻1
- 新闻2
— <font color="red">重点关注的新闻3</font>

HTML内容：
{html_content}
"""

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的新闻总结助手，擅长从网页内容中提取和总结新闻信息。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM总结失败: {e}")
        return None

def save_to_file(content):
    """将内容保存到文件，按日期分类目录，文件名按时间命名"""
    try:
        now = datetime.now()
        date_dir = now.strftime("%Y%m%d")
        time_filename = now.strftime("%H-%M-%S.md")

        # 创建news/日期目录
        news_date_dir = os.path.join("news", date_dir)
        if not os.path.exists(news_date_dir):
            os.makedirs(news_date_dir)

        filepath = os.path.join(news_date_dir, time_filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"新闻总结已保存到: {filepath}")
        return filepath
    except Exception as e:
        print(f"保存文件失败: {e}")
        return None

def main():
    """主函数"""
    # 目标网址
    url = "https://www.cls.cn/telegraph"

    print("开始获取网页内容...")
    html_content = get_webpage_content(url)

    if not html_content:
        print("无法获取网页内容")
        return

    print("网页内容获取成功，开始LLM总结...")
    summary = summarize_with_llm(html_content)

    if not summary:
        print("LLM总结失败")
        return

    print("LLM总结完成，保存到文件...")
    filepath = save_to_file(summary)

    if filepath:
        print("脚本执行完成！")
        print(f"新闻总结已保存到: {filepath}")
    else:
        print("保存文件失败")

if __name__ == "__main__":
    main()