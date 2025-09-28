#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调度器管理模块
负责定时任务的管理和执行
"""

from datetime import datetime
from typing import List, Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config
from logger_config import get_logger
from news_fetcher import news_fetcher

logger = get_logger('scheduler')


class SchedulerManager:
    """调度器管理器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._is_started = False

    def start(self) -> None:
        """启动调度器"""
        try:
            if not self._is_started:
                self.scheduler.start()
                self._is_started = True
                logger.info("定时调度器启动成功")
            else:
                logger.warning("调度器已经启动")
        except Exception as e:
            logger.error(f"定时调度器启动失败: {e}")
            raise

    def shutdown(self) -> None:
        """关闭调度器"""
        try:
            if self._is_started:
                logger.info("正在关闭定时调度器...")
                self.scheduler.shutdown()
                self._is_started = False
                logger.info("定时调度器已关闭")
            else:
                logger.warning("调度器未启动")
        except Exception as e:
            logger.error(f"关闭调度器时发生错误: {e}")

    def add_hourly_news_job(self) -> None:
        """添加每小时新闻抓取任务"""
        try:
            self.scheduler.add_job(
                func=self._run_news_task,
                trigger=CronTrigger(minute=config.CRON_MINUTE),
                id='hourly_news_fetch',
                name='每小时新闻抓取任务',
                replace_existing=True
            )
            logger.info("定时任务配置成功：每小时整点执行news.py")
        except Exception as e:
            logger.error(f"添加定时任务失败: {e}")
            raise

    def add_daily_cleanup_job(self):
        """添加每日新闻清理任务"""
        try:
            self.scheduler.add_job(
                func=self._run_cleanup_script,
                trigger=CronTrigger(hour=2, minute=0),  # 每天凌晨2点执行
                id='daily_news_cleanup',
                name='每日新闻清理任务',
                replace_existing=True
            )
            logger.info("定时任务配置成功：每天凌晨2点执行新闻清理")
        except Exception as e:
            logger.error(f"添加清理任务失败: {e}")
            raise

    def _run_cleanup_script(self):
        """执行新闻清理脚本"""
        try:
            logger.info("开始执行新闻清理任务")
            from news_cleaner import clean_old_news
            result = clean_old_news()
            if result['success']:
                logger.info(f"新闻清理成功：删除 {result['deleted_files']} 个文件，{result['deleted_dirs']} 个目录")
            else:
                logger.error(f"新闻清理失败：{result['error']}")
        except Exception as e:
            logger.error(f"执行新闻清理脚本失败: {e}")

    def add_manual_job(self) -> str:
        """
        添加手动执行任务

        Returns:
            str: 任务ID
        """
        try:
            job_id = f'manual_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            self.scheduler.add_job(
                func=self._run_news_task,
                trigger='date',
                run_date=datetime.now(),
                id=job_id
            )
            logger.info(f"手动执行任务已添加到队列，任务ID: {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"添加手动执行任务时发生错误: {e}")
            raise

    def get_jobs_info(self) -> List[Dict[str, Any]]:
        """
        获取所有任务信息

        Returns:
            List[Dict[str, Any]]: 任务信息列表
        """
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            logger.info(f"获取任务信息，共 {len(jobs)} 个任务")
            return jobs
        except Exception as e:
            logger.error(f"获取任务信息时发生错误: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """
        获取调度器状态

        Returns:
            Dict[str, Any]: 调度器状态信息
        """
        try:
            jobs = self.get_jobs_info()
            status = {
                'scheduler_running': self.is_running(),
                'jobs_count': len(jobs),
                'jobs': jobs
            }
            logger.info(f"调度器状态: 运行中={status['scheduler_running']}, 任务数={status['jobs_count']}")
            return status
        except Exception as e:
            logger.error(f"获取调度器状态时发生错误: {e}")
            return {
                'scheduler_running': False,
                'jobs_count': 0,
                'jobs': [],
                'error': str(e)
            }

    def is_running(self) -> bool:
        """检查调度器是否运行中"""
        return self._is_started and self.scheduler.running

    def _run_news_task(self) -> None:
        """执行新闻抓取任务"""
        try:
            success, output, error = news_fetcher.run_news_script()
            if success:
                logger.info("定时新闻抓取任务执行成功")
            else:
                logger.error(f"定时新闻抓取任务执行失败: {error}")
        except Exception as e:
            logger.error(f"执行新闻抓取任务时发生未预期错误: {e}")


# 全局调度器管理器实例
scheduler_manager = SchedulerManager()