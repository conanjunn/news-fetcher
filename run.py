#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用启动脚本
负责启动Web服务器和定时任务调度器
"""

import signal
import sys
from contextlib import contextmanager

from config import config
from logger_config import get_logger
from scheduler_manager import scheduler_manager
from app import create_app

logger = get_logger('main')


@contextmanager
def graceful_shutdown():
    """优雅关闭上下文管理器"""
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在优雅关闭...")
        scheduler_manager.shutdown()
        sys.exit(0)

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        yield
    finally:
        scheduler_manager.shutdown()


def print_startup_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("📰 新闻抓取Web服务器")
    print("=" * 60)
    print("🔄 定时任务已配置：")
    print("   - 每小时整点执行新闻抓取")
    print("   - 每天凌晨2点清理超过24小时的新闻")
    print("🌐 访问地址:")
    print(f"   - 主页: http://localhost:{config.PORT}/")
    print(f"   - 新闻列表: http://localhost:{config.PORT}/news/list")
    print(f"   - 新闻内容: http://localhost:{config.PORT}/news/20250927/18-02-58")
    print(f"   - 调度器状态: http://localhost:{config.PORT}/scheduler/status")
    print(f"   - 手动抓取: http://localhost:{config.PORT}/scheduler/run-now")
    print(f"   - 手动清理: http://localhost:{config.PORT}/scheduler/cleanup-now")
    print("📝 日志文件:")
    print(f"   - 应用日志: {config.LOGS_DIR}/app.log")
    print(f"   - 调度器日志: {config.LOGS_DIR}/scheduler.log")
    print(f"   - 新闻抓取日志: {config.LOGS_DIR}/news_fetcher.log")
    print(f"   - 安全日志: {config.LOGS_DIR}/security.log")
    print(f"   - 错误日志: {config.LOGS_DIR}/*_error.log")
    print("=" * 60)


def initialize_scheduler():
    """初始化调度器"""
    try:
        logger.info("初始化调度器...")
        scheduler_manager.start()
        scheduler_manager.add_hourly_news_job()
        scheduler_manager.add_daily_cleanup_job()
        logger.info("调度器初始化完成")
    except Exception as e:
        logger.error(f"调度器初始化失败: {e}")
        raise


def main():
    """主函数"""
    logger.info("开始启动新闻抓取Web服务器")

    try:
        with graceful_shutdown():
            # 初始化调度器
            initialize_scheduler()

            # 创建Flask应用
            app = create_app()

            # 打印启动信息
            print_startup_banner()

            logger.info("Web服务器和定时任务调度器已启动")
            logger.info(f"服务启动完成，监听 {config.HOST}:{config.PORT}")

            # 启动Flask应用
            app.run(
                host=config.HOST,
                port=config.PORT,
                debug=config.DEBUG,
                use_reloader=False  # 避免重载器与调度器冲突
            )

    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise
    finally:
        logger.info("服务器已完全关闭")


if __name__ == '__main__':
    main()