# CMoney 股价预测系统 - 部署指南

本文档提供完整的部署说明，包括Docker部署、手动部署和生产环境配置。

---

## 📋 目录

- [系统要求](#系统要求)
- [快速部署（Docker）](#快速部署docker)
- [手动部署](#手动部署)
- [生产环境配置](#生产环境配置)
- [监控和维护](#监控和维护)
- [故障排查](#故障排查)

---

## 系统要求

### 最低配置

- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB 可用空间
- **操作系统**: Linux (Ubuntu 20.04+, CentOS 7+) 或 Windows/Mac with Docker

### 推荐配置（生产环境）

- **CPU**: 4核心+
- **内存**: 8GB+ RAM
- **磁盘**: 50GB+ SSD
- **网络**: 100Mbps+

---

## 快速部署（Docker）

### 1. 安装 Docker 和 Docker Compose

#### Ubuntu/Debian:
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

#### CentOS/RHEL:
```bash
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Mac:
```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Docker Desktop
brew install --cask docker
```

#### Windows:
下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/CMoney.git
cd CMoney/CMoneySystem
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 应用配置
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production
DEBUG=False

# 数据库配置
DATABASE_URL=postgresql://cmoney:your-password@db:5432/cmoney
POSTGRES_USER=cmoney
POSTGRES_PASSWORD=your-password
POSTGRES_DB=cmoney

# Redis配置
REDIS_URL=redis://redis:6379/0

# API配置
API_RATE_LIMIT=100/minute
API_TIMEOUT=30
```

### 4. 构建和启动服务

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看服务状态
docker-compose ps
```

### 5. 初始化数据库

```bash
# 运行数据库迁移
docker-compose exec app python -c "from data.storage import DataStorage; DataStorage().init_db()"

# 创建默认管理员用户
docker-compose exec app python -c "
from services.auth import global_auth_service
global_auth_service.register('admin', 'admin@example.com', 'admin123', 'admin')
"
```

### 6. 验证部署

```bash
# 健康检查
curl http://localhost:5000/api/health

# API测试
curl http://localhost:5000/api/factors

# 访问前端
open http://localhost:80
```

---

## 手动部署

### 1. 安装系统依赖

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3-pip postgresql redis-server nginx
```

#### CentOS/RHEL:
```bash
sudo yum install -y python39 python39-pip postgresql-server redis nginx
```

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置 PostgreSQL

```bash
# 初始化数据库
sudo postgresql-setup initdb

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql <<EOF
CREATE DATABASE cmoney;
CREATE USER cmoney WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE cmoney TO cmoney;
\q
EOF

# 运行迁移
source venv/bin/activate
python -c "from data.storage import DataStorage; DataStorage().init_db()"
```

### 4. 配置 Redis

```bash
# 启动 Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 5. 配置 Nginx

创建 `/etc/nginx/sites-available/cmoney`:

```nginx
upstream cmoney_backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/CMoney/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://cmoney_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持（如果需要）
    location /ws {
        proxy_pass http://cmoney_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/cmoney /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. 配置 Systemd 服务

创建 `/etc/systemd/system/cmoney.service`:

```ini
[Unit]
Description=CMoney Stock Prediction System
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/CMoney/CMoneySystem
Environment="PATH=/path/to/CMoney/CMoneySystem/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/path/to/CMoney/CMoneySystem/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start cmoney
sudo systemctl enable cmoney
```

### 7. 配置 SSL（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 生产环境配置

### 1. 性能优化

#### Gunicorn 配置

在 `gunicorn.conf.py`:

```python
import multiprocessing

# 工作进程数（建议 CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = 'sync'

# 每个工作进程的线程数
threads = 2

# 超时时间
timeout = 120
keepalive = 5

# 日志
accesslog = '/var/log/cmoney/access.log'
errorlog = '/var/log/cmoney/error.log'
loglevel = 'info'

# 最大请求数后重启工作进程
max_requests = 1000
max_requests_jitter = 50

# 预加载应用
preload_app = True
```

#### PostgreSQL 优化

编辑 `/etc/postgresql/15/main/postgresql.conf`:

```ini
# 连接设置
max_connections = 100

# 内存设置
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 16MB

# 查询优化
random_page_cost = 1.1
effective_io_concurrency = 200

# WAL设置
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 2GB
min_wal_size = 512MB

# 日志
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
```

#### Redis 优化

编辑 `/etc/redis/redis.conf`:

```ini
# 最大内存
maxmemory 1gb

# 淘汰策略
maxmemory-policy allkeys-lru

# 持久化
save 900 1
save 300 10
save 60 10000

# AOF
appendonly yes
appendfsync everysec
```

### 2. 监控配置

#### Prometheus 配置

创建 `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cmoney'
    static_configs:
      - targets: ['app:5000']
    metrics_path: '/metrics'
```

#### Grafana Dashboard

导入监控面板，监控以下指标：
- 请求速率和响应时间
- CPU和内存使用率
- 数据库连接数
- Redis命中率
- 任务队列长度

### 3. 日志管理

#### 日志轮转配置

创建 `/etc/logrotate.d/cmoney`:

```
/var/log/cmoney/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload cmoney > /dev/null 2>&1 || true
    endscript
}
```

---

## 监控和维护

### 1. 健康检查

```bash
# API健康检查
curl http://localhost:5000/api/health

# 数据库连接检查
docker-compose exec db pg_isready -U cmoney

# Redis连接检查
docker-compose exec redis redis-cli ping
```

### 2. 日志查看

```bash
# 应用日志
docker-compose logs -f app

# 所有服务日志
docker-compose logs -f

# 按级别过滤日志
docker-compose exec app tail -f /app/logs/error.log
```

### 3. 性能监控

```bash
# 容器资源使用
docker stats

# 数据库性能
docker-compose exec db psql -U cmoney -c "SELECT * FROM pg_stat_activity;"

# Redis性能
docker-compose exec redis redis-cli INFO stats
```

### 4. 备份

#### 数据库备份

```bash
# 创建备份脚本
cat > backup.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgresql"
mkdir -p $BACKUP_DIR

docker-compose exec -T db pg_dump -U cmoney cmoney | gzip > $BACKUP_DIR/cmoney_$DATE.sql.gz

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# 添加到 crontab（每天凌晨2点备份）
crontab -e
# 添加：0 2 * * * /path/to/backup.sh
```

#### Redis备份

```bash
# 创建RDB快照
docker-compose exec redis redis-cli BGSAVE

# 复制持久化文件
docker cp cmoney-redis:/data/dump.rdb /backups/redis/
```

---

## 故障排查

### 常见问题

#### 1. 容器无法启动

```bash
# 查看详细日志
docker-compose logs app

# 检查容器状态
docker-compose ps

# 重新构建
docker-compose build --no-cache app
docker-compose up -d app
```

#### 2. 数据库连接失败

```bash
# 检查数据库是否运行
docker-compose ps db

# 检查连接
docker-compose exec db psql -U cmoney -c "SELECT version();"

# 检查网络
docker network inspect cmoney_cmoney-network
```

#### 3. API响应慢

```bash
# 查看资源使用
docker stats

# 检查数据库查询
docker-compose exec db psql -U cmoney -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# 检查Redis
docker-compose exec redis redis-cli SLOWLOG GET 10
```

#### 4. 内存不足

```bash
# 查看内存使用
free -h

# 清理Docker缓存
docker system prune -a

# 限制容器内存（编辑docker-compose.yml）
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 更新部署

### 滚动更新

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 平滑重启（不停机）
docker-compose up -d --no-deps app

# 或使用滚动更新
docker-compose up -d --scale app=2
docker-compose up -d --scale app=1
```

### 数据库迁移

```bash
# 备份数据库
./backup.sh

# 运行迁移
docker-compose exec app python migrate.py

# 验证迁移
docker-compose exec app python -c "from data.storage import DataStorage; print(DataStorage().get_version())"
```

---

## 安全建议

1. **修改默认密码**
   - 数据库密码
   - Redis密码
   - 管理员账户密码

2. **配置防火墙**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

3. **定期更新**
   ```bash
   # 更新系统
   sudo apt-get update && sudo apt-get upgrade -y

   # 更新Docker镜像
   docker-compose pull
   docker-compose up -d
   ```

4. **启用审计日志**
   - 记录所有管理操作
   - 监控异常访问

---

## 支持

如有问题，请：
1. 查看日志文件
2. 检查系统状态
3. 参考本文档故障排查章节
4. 提交Issue到GitHub

---

**祝部署顺利！** 🚀
