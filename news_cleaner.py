#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新闻文件清理模块
自动删除超过24小时的新闻文件
"""

import os
import re
from datetime import datetime, timedelta
from logger_config import get_logger

logger = get_logger('news_cleaner')


def clean_old_news(hours_threshold=24):
    """
    清理超过指定小时数的新闻文件

    Args:
        hours_threshold (int): 超过多少小时的文件将被删除，默认24小时

    Returns:
        dict: 清理结果统计
    """
    logger.info(f"开始清理超过 {hours_threshold} 小时的新闻文件")

    news_dir = "news"
    if not os.path.exists(news_dir):
        logger.warning(f"新闻目录不存在: {news_dir}")
        return {
            'success': False,
            'error': '新闻目录不存在',
            'deleted_files': 0,
            'deleted_dirs': 0
        }

    # 计算截止时间
    cutoff_time = datetime.now() - timedelta(hours=hours_threshold)
    logger.info(f"删除截止时间: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")

    deleted_files = 0
    deleted_dirs = 0

    try:
        # 遍历日期目录
        for date_dir in os.listdir(news_dir):
            date_path = os.path.join(news_dir, date_dir)

            # 检查是否是目录且符合日期格式 YYYYMMDD
            if not os.path.isdir(date_path) or not re.match(r'^\d{8}$', date_dir):
                continue

            logger.debug(f"检查日期目录: {date_dir}")

            # 遍历该日期目录下的文件
            files_in_dir = []
            try:
                files_in_dir = os.listdir(date_path)
            except OSError as e:
                logger.error(f"无法读取目录 {date_path}: {e}")
                continue

            for filename in files_in_dir:
                if not filename.endswith('.md'):
                    continue

                file_path = os.path.join(date_path, filename)

                # 解析文件时间 HH-MM-SS.md
                time_match = re.match(r'^(\d{2})-(\d{2})-(\d{2})\.md$', filename)
                if not time_match:
                    logger.warning(f"文件名格式不正确，跳过: {filename}")
                    continue

                hour, minute, second = time_match.groups()

                try:
                    # 构造完整的文件时间
                    file_datetime = datetime.strptime(
                        f"{date_dir} {hour}:{minute}:{second}",
                        "%Y%m%d %H:%M:%S"
                    )

                    # 检查是否超过阈值时间
                    if file_datetime < cutoff_time:
                        logger.info(f"删除过期文件: {file_path}")
                        os.remove(file_path)
                        deleted_files += 1
                    else:
                        logger.debug(f"文件未过期，保留: {file_path}")

                except ValueError as e:
                    logger.error(f"解析文件时间失败 {filename}: {e}")
                    continue

            # 检查目录是否为空，如果为空则删除
            try:
                remaining_files = [f for f in os.listdir(date_path) if f.endswith('.md')]
                if not remaining_files:
                    logger.info(f"删除空目录: {date_path}")
                    os.rmdir(date_path)
                    deleted_dirs += 1
                else:
                    logger.debug(f"目录非空，保留: {date_path} (剩余 {len(remaining_files)} 个文件)")
            except OSError as e:
                logger.error(f"删除目录失败 {date_path}: {e}")

    except Exception as e:
        logger.error(f"清理过程中发生错误: {e}")
        return {
            'success': False,
            'error': str(e),
            'deleted_files': deleted_files,
            'deleted_dirs': deleted_dirs
        }

    logger.info(f"清理完成: 删除了 {deleted_files} 个文件, {deleted_dirs} 个目录")

    return {
        'success': True,
        'deleted_files': deleted_files,
        'deleted_dirs': deleted_dirs,
        'cutoff_time': cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
    }


def main():
    """主函数，用于命令行执行"""
    logger.info("=" * 50)
    logger.info("开始执行新闻文件清理任务")

    result = clean_old_news()

    if result['success']:
        print(f"✅ 清理完成:")
        print(f"   删除文件: {result['deleted_files']} 个")
        print(f"   删除目录: {result['deleted_dirs']} 个")
        print(f"   截止时间: {result['cutoff_time']}")
    else:
        print(f"❌ 清理失败: {result['error']}")
        print(f"   已删除文件: {result['deleted_files']} 个")
        print(f"   已删除目录: {result['deleted_dirs']} 个")

    logger.info("新闻文件清理任务结束")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()