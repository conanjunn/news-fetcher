#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新闻抓取模块
负责执行新闻抓取脚本
"""

import subprocess
from typing import Tuple, Optional

from config import config
from logger_config import get_logger

logger = get_logger('news_fetcher')


class NewsFetcher:
    """新闻抓取器"""

    def __init__(self):
        self.script_path = config.NEWS_SCRIPT_PATH
        self.timeout = config.NEWS_SCRIPT_TIMEOUT

    def run_news_script(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        执行新闻抓取脚本

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (成功状态, 输出, 错误信息)
        """
        try:
            logger.info("开始执行新闻抓取任务...")

            # 检查脚本文件是否存在
            if not self._check_script_exists():
                return False, None, f"新闻脚本不存在: {self.script_path}"

            # 执行脚本
            result = subprocess.run(
                ['python3', self.script_path],
                cwd=config.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                logger.info("新闻抓取任务执行成功")
                if result.stdout:
                    logger.info(f"脚本输出: {result.stdout.strip()}")
                return True, result.stdout, None
            else:
                error_msg = f"新闻抓取任务执行失败，返回码: {result.returncode}"
                if result.stderr:
                    error_msg += f", 错误信息: {result.stderr.strip()}"
                logger.error(error_msg)
                return False, result.stdout, error_msg

        except subprocess.TimeoutExpired:
            error_msg = f"新闻抓取任务执行超时({self.timeout}秒)"
            logger.error(error_msg)
            return False, None, error_msg

        except Exception as e:
            error_msg = f"执行新闻抓取任务时发生错误: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def _check_script_exists(self) -> bool:
        """检查脚本文件是否存在"""
        import os
        exists = os.path.exists(self.script_path)
        if not exists:
            logger.error(f"新闻脚本不存在: {self.script_path}")
        return exists


# 全局新闻抓取器实例
news_fetcher = NewsFetcher()