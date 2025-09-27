#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件模块
包含应用的所有配置项
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """应用配置类"""

    # 服务器配置
    HOST: str = '0.0.0.0'
    PORT: int = 5000
    DEBUG: bool = False

    # 目录配置
    BASE_DIR: str = os.path.abspath('.')
    STATIC_DIR: str = os.path.abspath('.')
    NEWS_DIR: str = os.path.abspath('news')
    LOGS_DIR: str = 'logs'

    # 脚本配置
    NEWS_SCRIPT: str = 'news.py'
    NEWS_SCRIPT_TIMEOUT: int = 300  # 5分钟

    # 定时任务配置
    CRON_MINUTE: int = 0  # 每小时的0分执行

    # 日志配置
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    LOG_BACKUP_COUNT: int = 30  # 保留30天日志

    # 文件路径验证配置
    ALLOWED_PATH_PATTERN: str = r'^(\d{8})/(\d{2}-\d{2}-\d{2})$'
    DANGEROUS_CHARS: tuple = ('..', '~')

    def __post_init__(self):
        """初始化后处理"""
        # 确保目录存在
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        os.makedirs(self.NEWS_DIR, exist_ok=True)

        # 生成完整的脚本路径
        self.NEWS_SCRIPT_PATH = os.path.join(self.BASE_DIR, self.NEWS_SCRIPT)


# 全局配置实例
config = Config()