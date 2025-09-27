#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全工具模块
提供路径验证和安全检查功能
"""

import os
import re
from typing import Optional, Tuple

from werkzeug.security import safe_join
from config import config
from logger_config import get_logger

logger = get_logger('security')


class SecurityValidator:
    """安全验证器"""

    def __init__(self):
        self.news_dir = config.NEWS_DIR
        self.allowed_pattern = config.ALLOWED_PATH_PATTERN
        self.dangerous_chars = config.DANGEROUS_CHARS

    def is_safe_path(self, path: str) -> bool:
        """
        检查路径是否安全，防止目录遍历攻击

        Args:
            path: 要检查的路径

        Returns:
            bool: 路径是否安全
        """
        try:
            # 检查路径是否包含危险字符
            if any(char in path for char in self.dangerous_chars):
                logger.warning(f"路径包含危险字符: {path}")
                return False

            # 检查是否包含绝对路径
            if os.path.isabs(path):
                logger.warning(f"不允许绝对路径: {path}")
                return False

            # 检查路径格式：应该是 YYYYMMDD/HH-MM-SS 格式
            if not re.match(self.allowed_pattern, path):
                logger.warning(f"路径格式不正确: {path}")
                return False

            return True

        except Exception as e:
            logger.error(f"路径安全检查时发生错误: {e}")
            return False

    def get_safe_file_path(self, news_path: str) -> Optional[str]:
        """
        获取安全的文件路径

        Args:
            news_path: 新闻文件路径

        Returns:
            Optional[str]: 安全的完整文件路径，如果不安全则返回None
        """
        try:
            # 验证路径安全性
            if not self.is_safe_path(news_path):
                return None

            # 添加.md扩展名
            if not news_path.endswith('.md'):
                news_path += '.md'

            # 使用safe_join确保路径安全
            safe_path = safe_join(self.news_dir, news_path)
            if safe_path is None:
                logger.warning(f"safe_join返回None: {news_path}")
                return None

            # 确保文件在news目录下
            if not safe_path.startswith(self.news_dir):
                logger.warning(f"文件不在news目录下: {safe_path}")
                return None

            return safe_path

        except Exception as e:
            logger.error(f"获取安全文件路径时发生错误: {e}")
            return None

    def validate_file_access(self, file_path: str) -> Tuple[bool, str]:
        """
        验证文件访问权限

        Args:
            file_path: 文件路径

        Returns:
            Tuple[bool, str]: (是否可访问, 错误消息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, "文件不存在"

            # 检查是否为文件
            if not os.path.isfile(file_path):
                return False, "不是有效的文件"

            # 检查读取权限
            if not os.access(file_path, os.R_OK):
                return False, "没有读取权限"

            return True, ""

        except Exception as e:
            logger.error(f"文件访问验证时发生错误: {e}")
            return False, f"验证失败: {str(e)}"


# 全局安全验证器实例
security_validator = SecurityValidator()