# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于Flask的新闻抓取和展示系统，主要功能包括：
- 自动抓取财联社电报新闻并使用LLM进行智能分类总结
- 定时任务调度（每小时整点执行）
- Web界面展示和新闻管理
- 完整的安全防护和日志系统

## 核心架构

### 应用入口
- `run.py` - 应用启动脚本，负责启动Web服务器和调度器
- `app.py` - Flask应用主文件，包含所有API路由
- `config.py` - 配置管理，使用dataclass模式

### 核心模块
- `news_fetcher.py` / `news.py` - 新闻抓取脚本，调用LLM API处理内容
- `scheduler_manager.py` - APScheduler调度器管理
- `security_utils.py` - 路径验证和安全检查
- `logger_config.py` - 分模块日志配置

### 前端
- `index.html` - 单页面应用，包含完整的JavaScript逻辑

### 数据存储
- `news/YYYYMMDD/HH-MM-SS.md` - 新闻文件按日期时间存储
- `logs/` - 各模块独立日志文件

## 常用命令

### 启动服务
```bash
python3 run.py
```

### 手动执行新闻抓取
```bash
python3 news.py
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 查看日志
```bash
# 实时查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/app_error.log

# 查看调度器日志
tail -f logs/scheduler.log

# 查看新闻抓取日志
tail -f logs/news_fetcher.log
```

### 测试API
```bash
# 获取新闻列表
curl http://localhost:5000/news/list

# 获取特定新闻
curl http://localhost:5000/news/20250927/18-02-58

# 手动执行抓取
curl http://localhost:5000/scheduler/run-now

# 查看调度器状态
curl http://localhost:5000/scheduler/status
```

## 配置管理

### 敏感信息配置
1. 复制配置模板：`cp secrets.example.py secrets.py`
2. 编辑 `secrets.py` 填入API密钥：
   - `OPENAI_API_KEY` - OpenAI API密钥
   - `OPENAI_BASE_URL` - API基础URL
   - `DEFAULT_MODEL` - 使用的模型名称

### 应用配置
修改 `config.py` 中的 `Config` 类：
- `HOST/PORT` - 服务器地址和端口
- `DEBUG` - 调试模式
- `CRON_MINUTE` - 定时执行分钟数
- `NEWS_SCRIPT_TIMEOUT` - 脚本执行超时时间

## 安全特性

### 路径安全
- 严格的路径格式验证 (`ALLOWED_PATH_PATTERN`)
- 防止目录遍历攻击
- 危险字符过滤 (`DANGEROUS_CHARS`)
- 详细的安全访问日志

### 配置安全
- `secrets.py` 已加入 `.gitignore`，不会被提交
- 提供 `secrets.example.py` 作为配置模板

## 开发注意事项

### 日志系统
- 使用分模块的logger配置
- 日志文件按天自动切割，保留30天
- 错误日志单独存储在 `*_error.log` 文件中

### 调度器管理
- 使用APScheduler进行任务调度
- 优雅关闭机制，避免任务中断
- 支持手动触发和状态查询

### Flask应用结构
- 使用工厂模式创建Flask应用
- 路由集中在 `app.py` 中
- 安全验证集成在每个路由中

### 前端架构
- 单页面应用，所有逻辑在 `index.html` 中
- 使用原生JavaScript，无外部依赖
- 支持响应式设计和移动端

## 故障排除

### 常见问题检查
1. 配置文件是否存在：`ls -la secrets.py`
2. 端口是否被占用：`lsof -i :5000`
3. 权限是否正确：检查 `news/` 和 `logs/` 目录权限
4. API密钥是否有效：查看 `logs/news_fetcher_error.log`