# 快速开始指南

## 🚀 30秒部署指南

### 1. 克隆项目
```bash
git clone https://github.com/your-username/news-fetcher.git
cd news-fetcher
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置API密钥
```bash
# 复制配置模板
cp secrets.example.py secrets.py

# 编辑配置文件
nano secrets.py  # 或使用你喜欢的编辑器
```

在 `secrets.py` 中填入你的配置：
```python
OPENAI_API_KEY = "your_api_key_here"
OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-3.5-turbo"
```

### 4. 启动服务
```bash
python3 run.py
```

### 5. 访问服务
打开浏览器访问：http://localhost:5000

---

## 📋 支持的API服务

### OpenAI 官方
```python
OPENAI_API_KEY = "sk-xxx"
OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-3.5-turbo"
```

### Azure OpenAI
```python
OPENAI_API_KEY = "your_azure_key"
OPENAI_BASE_URL = "https://your-resource.openai.azure.com/"
DEFAULT_MODEL = "gpt-35-turbo"
```

### 第三方API服务
```python
OPENAI_API_KEY = "your_api_key"
OPENAI_BASE_URL = "https://api.example.com/v1"
DEFAULT_MODEL = "gpt-3.5-turbo"
```

---

## 🔧 常见配置

### 修改定时任务
编辑 `config.py`：
```python
CRON_MINUTE: int = 30  # 改为每小时30分执行
```

### 修改端口
编辑 `config.py`：
```python
PORT: int = 8080  # 改为8080端口
```

### 启用调试模式
编辑 `config.py`：
```python
DEBUG: bool = True
```

---

## ❓ 常见问题

### Q: 提示"找不到 secrets.py 配置文件"
A: 请确保已执行第3步，复制并编辑配置文件。

### Q: API调用失败
A: 检查API密钥是否正确，服务地址是否可访问。

### Q: 端口被占用
A: 修改 `config.py` 中的 PORT 配置或关闭占用端口的进程。

### Q: 权限错误
A: 确保当前用户有读写项目目录的权限。

---

## 🔍 测试配置

### 手动测试新闻抓取
```bash
python3 news.py
```

### 测试Web服务
```bash
curl http://localhost:5000/news/list
```

### 查看服务状态
```bash
curl http://localhost:5000/scheduler/status
```

---

## 📝 生产部署

### 使用systemd
1. 创建服务文件：
```bash
sudo nano /etc/systemd/system/news-fetcher.service
```

2. 添加配置：
```ini
[Unit]
Description=News Fetcher Web Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/news-fetcher
ExecStart=/usr/bin/python3 run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. 启动服务：
```bash
sudo systemctl enable news-fetcher
sudo systemctl start news-fetcher
```

### 使用Docker
```bash
# 构建镜像
docker build -t news-fetcher .

# 运行容器
docker run -d -p 5000:5000 \
  -v $(pwd)/secrets.py:/app/secrets.py \
  news-fetcher
```

---

🎉 **恭喜！你已成功部署新闻抓取服务！**

访问 http://localhost:5000 开始使用吧！