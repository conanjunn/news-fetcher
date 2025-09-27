# 新闻抓取Web服务器

一个基于Flask的新闻抓取和展示系统，支持定时抓取财联社电报新闻并通过Web界面展示。

## 🚀 功能特性

- 📰 **自动新闻抓取**: 每小时自动抓取财联社电报新闻
- 🤖 **AI智能总结**: 使用LLM对新闻进行智能分类和总结
- 🌐 **Web界面**: 响应式设计，支持PC和移动端
- 📅 **按日期组织**: 新闻文件按日期分类存储
- 🔒 **安全防护**: 路径验证、权限检查等安全措施
- 📝 **完整日志**: 按日期切割的详细日志记
- ⚡ **手动执行**: 支持手动触发新闻抓取

## 📁 项目结构

```
.
├── app.py              # Flask应用主文件
├── run.py              # 应用启动脚本
├── config.py           # 配置文件
├── logger_config.py    # 日志配置
├── scheduler_manager.py # 调度器管理
├── news_fetcher.py     # 新闻抓取模块
├── security_utils.py   # 安全验证模块
├── news.py            # 新闻抓取脚本
├── secrets.py         # 敏感信息配置（不提交到Git）
├── secrets.example.py # 配置文件模板
├── index.html         # 前端页面
├── requirements.txt   # 依赖包列表
├── .gitignore         # Git忽略规则
├── README.md          # 项目说明
├── logs/              # 日志目录
│   ├── app.log
│   ├── scheduler.log
│   └── *_error.log
└── news/              # 新闻存储目录
    └── YYYYMMDD/      # 按日期分类
        └── HH-MM-SS.md
```

## 🛠 安装和配置

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置敏感信息

复制配置模板并填入你的API信息：

```bash
cp secrets.example.py secrets.py
```

编辑 `secrets.py` 文件，填入你的API配置：

```python
# OpenAI API 配置
OPENAI_API_KEY = "your_api_key_here"
OPENAI_BASE_URL = "https://api.openai.com/v1"  # 或你的自定义API地址
DEFAULT_MODEL = "gpt-3.5-turbo"  # 或其他支持的模型
```

⚠️ **重要提醒**：
- `secrets.py` 文件包含敏感信息，已被 `.gitignore` 忽略
- 请勿将此文件提交到版本控制系统
- 如需分享项目，请确保接收方按照上述步骤配置自己的 `secrets.py`

### 4. 配置修改

编辑 `config.py` 文件根据需要调整配置：

```python
@dataclass
class Config:
    HOST: str = '0.0.0.0'      # 服务器地址
    PORT: int = 5000           # 服务器端口
    DEBUG: bool = False        # 调试模式
    CRON_MINUTE: int = 0       # 定时执行分钟（0=整点）
    # ... 其他配置
```

## 🚀 启动服务

```bash
python3 run.py
```

服务启动后会显示访问地址和日志文件位置。

**注意**：首次运行前请确保已完成第3步的敏感信息配置，否则会提示配置文件缺失。

## 🌐 API接口

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/news/list` | GET | 获取新闻文件列表 |
| `/news/{date}/{time}` | GET | 获取指定新闻内容 |
| `/scheduler/status` | GET | 查看调度器状态 |
| `/scheduler/run-now` | GET | 手动执行新闻抓取 |

### 示例

```bash
# 获取新闻列表
curl http://localhost:5000/news/list

# 获取特定新闻
curl http://localhost:5000/news/20250927/18-02-58

# 手动执行抓取
curl http://localhost:5000/scheduler/run-now
```

## 📝 日志管理

### 日志文件

- `logs/app.log` - 应用主日志
- `logs/scheduler.log` - 调度器日志
- `logs/news_fetcher.log` - 新闻抓取日志
- `logs/security.log` - 安全相关日志
- `logs/*_error.log` - 各模块错误日志

### 日志特性

- ✅ 按天自动切割
- ✅ 保留30天历史
- ✅ 多级别记录（INFO/WARNING/ERROR）
- ✅ 详细的上下文信息

### 查看日志

```bash
# 实时查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/app_error.log

# 查看调度器日志
tail -f logs/scheduler.log
```

## 🔒 安全特性

### 路径安全

- ✅ 防止目录遍历攻击
- ✅ 路径格式验证
- ✅ 文件权限检查
- ✅ 访问日志记录

### 输入验证

- ✅ 严格的路径格式检查
- ✅ 危险字符过滤
- ✅ 文件扩展名验证

## 🐛 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查端口是否被占用
   lsof -i :5000

   # 查看错误日志
   tail -f logs/app_error.log
   ```

2. **新闻抓取失败**
   ```bash
   # 检查配置文件是否存在
   ls -la secrets.py

   # 检查配置文件内容（注意保护敏感信息）
   head -n 5 secrets.py

   # 查看抓取日志
   tail -f logs/news_fetcher.log
   ```

3. **定时任务不执行**
   ```bash
   # 查看调度器状态
   curl http://localhost:5000/scheduler/status

   # 查看调度器日志
   tail -f logs/scheduler.log
   ```

### 手动测试

```bash
# 测试新闻抓取脚本
python3 news.py

# 测试Web服务
curl http://localhost:5000/news/list
```

## 🔧 开发和部署

### 开发模式

修改 `config.py` 启用调试模式：

```python
DEBUG: bool = True
```

### 生产部署

1. 确保所有配置正确
2. 使用进程管理器（如systemd、supervisor）
3. 配置反向代理（如nginx）
4. 设置日志轮转
5. 监控服务状态

### 系统服务配置示例

创建 systemd 服务文件 `/etc/systemd/system/news-server.service`：

```ini
[Unit]
Description=News Fetch Web Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/app
Environment=OPENAI_API_KEY=your_key_here
ExecStart=/usr/bin/python3 run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 性能监控

### 关键指标

- 服务响应时间
- 新闻抓取成功率
- 日志文件大小
- 系统资源使用

### 监控命令

```bash
# 查看服务状态
systemctl status news-server

# 监控日志
journalctl -u news-server -f

# 查看资源使用
top -p $(pgrep -f run.py)
```

## 🔐 安全最佳实践

### 配置管理
- ✅ 敏感信息存储在 `secrets.py` 中，不提交到版本控制
- ✅ 使用 `.gitignore` 防止敏感文件意外提交
- ✅ 提供 `secrets.example.py` 作为配置模板

### 开源贡献指南
- 📝 提交Pull Request前请确保没有包含敏感信息
- 🔍 检查代码中是否有硬编码的密钥或密码
- 🧪 确保示例配置文件使用占位符而非真实数据
- 📋 更新文档以反映配置变更

### 部署注意事项
- 🚀 生产环境请使用强密码和安全的API密钥
- 🔄 定期轮换API密钥
- 📊 监控API使用量和异常访问
- 🛡️ 设置防火墙和访问控制

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

**贡献时请注意**：
- 不要在代码中包含真实的API密钥或敏感信息
- 更新相关文档和示例
- 确保代码通过安全检查

## 📄 许可证

MIT License