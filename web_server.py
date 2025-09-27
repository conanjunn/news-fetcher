#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, send_from_directory, jsonify, abort
import os
import re
import subprocess
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from werkzeug.security import safe_join
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

app = Flask(__name__)

# 配置静态文件目录
STATIC_DIR = os.path.abspath('.')
NEWS_DIR = os.path.abspath('news')
NEWS_SCRIPT = os.path.join(STATIC_DIR, 'news.py')

# 配置日志
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    # 按天切割的文件处理器
    file_handler = TimedRotatingFileHandler(
        'logs/web_server.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 错误日志文件处理器
    error_handler = TimedRotatingFileHandler(
        'logs/web_server_error.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)

    return logger

# 创建logs目录
os.makedirs('logs', exist_ok=True)
logger = setup_logger()

# 创建调度器
scheduler = BackgroundScheduler()
try:
    scheduler.start()
    logger.info("定时调度器启动成功")
except Exception as e:
    logger.error(f"定时调度器启动失败: {e}")
    raise

def run_news_script():
    """执行news.py脚本"""
    try:
        logger.info("开始执行新闻抓取任务...")

        # 检查脚本文件是否存在
        if not os.path.exists(NEWS_SCRIPT):
            logger.error(f"新闻脚本不存在: {NEWS_SCRIPT}")
            return

        # 执行脚本
        result = subprocess.run(
            ['python3', NEWS_SCRIPT],
            cwd=STATIC_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            logger.info("新闻抓取任务执行成功")
            if result.stdout:
                logger.info(f"脚本输出: {result.stdout}")
        else:
            logger.error(f"新闻抓取任务执行失败，返回码: {result.returncode}")
            if result.stderr:
                logger.error(f"错误信息: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("新闻抓取任务执行超时")
    except Exception as e:
        logger.error(f"执行新闻抓取任务时发生错误: {str(e)}")

def is_safe_path(path):
    """检查路径是否安全，防止目录遍历攻击"""
    # 检查路径是否包含危险字符
    if '..' in path or '~' in path:
        return False

    # 检查是否包含绝对路径
    if os.path.isabs(path):
        return False

    # 检查路径格式：应该是 YYYYMMDD/HH-MM-SS 格式
    pattern = r'^(\d{8})/(\d{2}-\d{2}-\d{2})$'
    if not re.match(pattern, path):
        return False

    return True

@app.route('/')
def index():
    """提供index.html文件"""
    try:
        logger.info("访问首页")
        return send_from_directory(STATIC_DIR, 'index.html')
    except FileNotFoundError:
        logger.error("index.html 文件不存在")
        return "index.html 文件不存在", 404
    except Exception as e:
        logger.error(f"访问首页时发生错误: {e}")
        return "服务器内部错误", 500

@app.route('/news/<path:news_path>')
def get_news(news_path):
    """
    安全地提供新闻文件内容
    路径格式: /news/20250927/18-02-58
    """
    logger.info(f"请求新闻文件: {news_path}")
    try:
        # 验证路径安全性
        if not is_safe_path(news_path):
            logger.warning(f"检测到非法文件路径访问: {news_path}")
            abort(400, description="非法的文件路径")

        # 添加.md扩展名
        if not news_path.endswith('.md'):
            news_path += '.md'

        # 使用safe_join确保路径安全
        safe_path = safe_join(NEWS_DIR, news_path)
        if safe_path is None:
            abort(400, description="非法的文件路径")

        # 检查文件是否存在
        if not os.path.exists(safe_path):
            abort(404, description="文件不存在")

        # 确保文件在news目录下
        if not safe_path.startswith(NEWS_DIR):
            abort(403, description="禁止访问该目录")

        # 读取文件内容
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"成功读取新闻文件: {safe_path}")
        return jsonify({
            'success': True,
            'path': news_path,
            'content': content
        })

    except FileNotFoundError:
        logger.warning(f"请求的文件不存在: {news_path}")
        abort(404, description="文件不存在")
    except PermissionError:
        logger.error(f"没有权限访问文件: {news_path}")
        abort(403, description="没有权限访问该文件")
    except Exception as e:
        logger.error(f"获取新闻文件时发生错误: {e}, 路径: {news_path}")
        abort(500, description=f"服务器内部错误: {str(e)}")

@app.route('/news/list')
def list_news():
    """列出所有可用的新闻文件"""
    logger.info("请求新闻文件列表")
    try:
        news_files = []

        if not os.path.exists(NEWS_DIR):
            logger.warning(f"新闻目录不存在: {NEWS_DIR}")
            return jsonify({'success': True, 'files': []})

        # 遍历news目录
        for date_dir in os.listdir(NEWS_DIR):
            date_path = os.path.join(NEWS_DIR, date_dir)

            # 检查是否是目录且符合日期格式
            if os.path.isdir(date_path) and re.match(r'^\d{8}$', date_dir):
                # 遍历日期目录下的文件
                for filename in os.listdir(date_path):
                    if filename.endswith('.md'):
                        # 移除.md扩展名
                        time_part = filename[:-3]
                        news_files.append(f"{date_dir}/{time_part}")

        # 按时间排序（最新的在前）
        news_files.sort(reverse=True)

        logger.info(f"成功获取新闻文件列表，共 {len(news_files)} 个文件")
        return jsonify({
            'success': True,
            'files': news_files
        })

    except Exception as e:
        logger.error(f"获取新闻文件列表时发生错误: {e}")
        abort(500, description=f"服务器内部错误: {str(e)}")

@app.route('/scheduler/status')
def scheduler_status():
    """获取调度器状态"""
    logger.info("请求调度器状态")
    try:
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })

        logger.info(f"调度器状态: 运行中={scheduler.running}, 任务数={len(jobs)}")
        return jsonify({
            'success': True,
            'scheduler_running': scheduler.running,
            'jobs': jobs
        })
    except Exception as e:
        logger.error(f"获取调度器状态时发生错误: {e}")
        abort(500, description=f"服务器内部错误: {str(e)}")

@app.route('/scheduler/run-now')
def run_news_now():
    """手动执行一次新闻抓取"""
    logger.info("收到手动执行新闻抓取请求")
    try:
        job_id = f'manual_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        # 在后台执行任务
        scheduler.add_job(
            func=run_news_script,
            trigger='date',
            run_date=datetime.now(),
            id=job_id
        )

        logger.info(f"手动执行任务已添加到队列，任务ID: {job_id}")
        return jsonify({
            'success': True,
            'message': '手动执行任务已添加到队列',
            'job_id': job_id
        })
    except Exception as e:
        logger.error(f"添加手动执行任务时发生错误: {e}")
        abort(500, description=f"服务器内部错误: {str(e)}")

@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"400错误: {error.description}")
    return jsonify({'success': False, 'error': str(error.description)}), 400

@app.errorhandler(403)
def forbidden(error):
    logger.warning(f"403错误: {error.description}")
    return jsonify({'success': False, 'error': str(error.description)}), 403

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404错误: {error.description}")
    return jsonify({'success': False, 'error': str(error.description)}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500错误: {error.description}")
    return jsonify({'success': False, 'error': str(error.description)}), 500

if __name__ == '__main__':
    logger.info("开始启动Web服务器和定时任务调度器")

    try:
        # 添加定时任务：每小时的0分执行
        scheduler.add_job(
            func=run_news_script,
            trigger=CronTrigger(minute=0),  # 每小时的0分执行
            id='hourly_news_fetch',
            name='每小时新闻抓取任务',
            replace_existing=True
        )
        logger.info("定时任务配置成功：每小时整点执行news.py")

        print("="*50)
        print("📰 新闻抓取Web服务器")
        print("="*50)
        print("🔄 定时任务已配置：每小时整点执行news.py")
        print("🌐 访问地址:")
        print("   - 主页: http://localhost:5000/")
        print("   - 新闻列表: http://localhost:5000/news/list")
        print("   - 新闻内容: http://localhost:5000/news/20250927/18-02-58")
        print("   - 调度器状态: http://localhost:5000/scheduler/status")
        print("   - 手动执行: http://localhost:5000/scheduler/run-now")
        print("📝 日志文件:")
        print("   - 普通日志: logs/web_server.log")
        print("   - 错误日志: logs/web_server_error.log")
        print("="*50)

        logger.info("Web服务器和定时任务调度器已启动")
        logger.info("服务启动完成，等待请求...")

        app.run(host='0.0.0.0', port=5000, debug=False)

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise
    finally:
        logger.info("正在关闭定时调度器...")
        scheduler.shutdown()
        logger.info("服务器已完全关闭")