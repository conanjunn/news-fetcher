#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置模块
提供统一的日志管理功能
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from config import config


class LoggerManager:
    """日志管理器"""

    def __init__(self):
        self._loggers = {}

    def get_logger(self, name: str) -> logging.Logger:
        """获取或创建日志器"""
        if name not in self._loggers:
            self._loggers[name] = self._create_logger(name)
        return self._loggers[name]

    def _create_logger(self, name: str) -> logging.Logger:
        """创建配置好的日志器"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.LOG_LEVEL))

        # 避免重复添加处理器
        if logger.handlers:
            return logger

        # 创建格式器
        formatter = logging.Formatter(config.LOG_FORMAT)

        # 普通日志文件处理器
        file_handler = TimedRotatingFileHandler(
            f'{config.LOGS_DIR}/{name}.log',
            when='midnight',
            interval=1,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # 错误日志文件处理器
        error_handler = TimedRotatingFileHandler(
            f'{config.LOGS_DIR}/{name}_error.log',
            when='midnight',
            interval=1,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

        return logger


# 全局日志管理器实例
logger_manager = LoggerManager()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志器的便捷函数"""
    if name is None:
        name = 'app'
    return logger_manager.get_logger(name)