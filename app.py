#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主要Flask应用文件
提供Web API接口
"""

import os
import re
from flask import Flask, send_from_directory, jsonify, abort

from config import config
from logger_config import get_logger
from security_utils import security_validator
from scheduler_manager import scheduler_manager

# 创建Flask应用
app = Flask(__name__)
logger = get_logger('app')


# 路由处理函数
@app.route('/')
def index():
    """提供index.html文件"""
    try:
        logger.info("访问首页")
        return send_from_directory(config.STATIC_DIR, 'index.html')
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
        # 获取安全的文件路径
        safe_path = security_validator.get_safe_file_path(news_path)
        if safe_path is None:
            logger.warning(f"检测到非法文件路径访问: {news_path}")
            abort(400, description="非法的文件路径")

        # 验证文件访问权限
        can_access, error_msg = security_validator.validate_file_access(safe_path)
        if not can_access:
            if "不存在" in error_msg:
                logger.warning(f"请求的文件不存在: {news_path}")
                abort(404, description=error_msg)
            elif "权限" in error_msg:
                logger.error(f"没有权限访问文件: {news_path}")
                abort(403, description=error_msg)
            else:
                logger.error(f"文件访问验证失败: {news_path}, 错误: {error_msg}")
                abort(500, description=f"服务器内部错误: {error_msg}")

        # 读取文件内容
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"成功读取新闻文件: {safe_path}")
        return jsonify({
            'success': True,
            'path': news_path,
            'content': content
        })

    except Exception as e:
        logger.error(f"获取新闻文件时发生错误: {e}, 路径: {news_path}")
        abort(500, description=f"服务器内部错误: {str(e)}")


@app.route('/news/list')
def list_news():
    """列出所有可用的新闻文件"""
    logger.info("请求新闻文件列表")
    try:
        news_files = []

        if not os.path.exists(config.NEWS_DIR):
            logger.warning(f"新闻目录不存在: {config.NEWS_DIR}")
            return jsonify({'success': True, 'files': []})

        # 遍历news目录
        for date_dir in os.listdir(config.NEWS_DIR):
            date_path = os.path.join(config.NEWS_DIR, date_dir)

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
        status = scheduler_manager.get_status()
        return jsonify({
            'success': True,
            **status
        })
    except Exception as e:
        logger.error(f"获取调度器状态时发生错误: {e}")
        abort(500, description=f"服务器内部错误: {str(e)}")


@app.route('/scheduler/run-now')
def run_news_now():
    """手动执行一次新闻抓取"""
    logger.info("收到手动执行新闻抓取请求")
    try:
        job_id = scheduler_manager.add_manual_job()
        return jsonify({
            'success': True,
            'message': '手动执行任务已添加到队列',
            'job_id': job_id
        })
    except Exception as e:
        logger.error(f"添加手动执行任务时发生错误: {e}")
        abort(500, description=f"服务器内部错误: {str(e)}")


@app.route('/scheduler/cleanup-now')
def run_cleanup_now():
    """手动执行一次新闻清理"""
    logger.info("收到手动执行新闻清理请求")
    try:
        from news_cleaner import clean_old_news
        result = clean_old_news()

        if result['success']:
            return jsonify({
                'success': True,
                'message': '新闻清理执行成功',
                'deleted_files': result['deleted_files'],
                'deleted_dirs': result['deleted_dirs'],
                'cutoff_time': result['cutoff_time']
            })
        else:
            return jsonify({
                'success': False,
                'message': '新闻清理执行失败',
                'error': result['error'],
                'deleted_files': result['deleted_files'],
                'deleted_dirs': result['deleted_dirs']
            }), 500
    except Exception as e:
        logger.error(f"执行新闻清理时发生错误: {e}")
        abort(500, description=f"服务器内部错误: {str(e)}")


# 错误处理器
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


def create_app():
    """创建并配置Flask应用"""
    logger.info("创建Flask应用")
    return app


if __name__ == '__main__':
    # 这个文件现在主要作为模块导入使用
    # 实际启动应该使用 run.py
    logger.warning("建议使用 run.py 启动应用")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)