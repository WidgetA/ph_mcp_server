# Ubuntu 服务器部署指南

本指南介绍如何在 Ubuntu 服务器上部署 Product Hunt MCP Server。

## 系统要求

- Ubuntu 20.04 LTS 或更高版本
- 至少 1GB RAM
- 1 CPU 核心
- 至少 2GB 磁盘空间
- Root 或 sudo 权限

## 快速部署

### 方式 1: 自动部署（推荐）⭐

```bash
# 1. 克隆或上传项目到服务器
git clone <repository-url>
cd ph_mcp_server

# 2. 运行部署脚本
sudo bash deploy/deploy.sh

# 3. 编辑配置文件
sudo nano /opt/ph_mcp_server/.env

# 4. 启动服务
sudo systemctl start ph-mcp-server

# 5. 检查状态
sudo systemctl status ph-mcp-server
```

### 方式 2: 手动部署

#### 1. 安装系统依赖

```bash
sudo apt-get update
sudo apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    curl \
    build-essential \
    nginx
```

#### 2. 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

#### 3. 创建部署目录

```bash
sudo mkdir -p /opt/ph_mcp_server
sudo chown $USER:$USER /opt/ph_mcp_server
cd /opt/ph_mcp_server
```

#### 4. 复制项目文件

```bash
# 如果使用 git
git clone <repository-url> .

# 或者使用 rsync 从本地上传
rsync -avz --exclude .git --exclude .venv /path/to/ph_mcp_server/ user@server:/opt/ph_mcp_server/
```

#### 5. 安装 Python 依赖

```bash
cd /opt/ph_mcp_server
uv sync
```

#### 6. 配置环境变量

```bash
cp .env.example .env
nano .env
```

填入以下配置：
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PRODUCTS_TABLE=ph_products
REPORTS_TABLE=ph_daily_reports
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
```

#### 7. 测试运行

```bash
python3 server.py
```

访问 `http://your-server-ip:8080/health` 验证。按 `Ctrl+C` 停止。

#### 8. 安装 systemd 服务

```bash
# 修改服务文件中的路径和用户
sudo cp deploy/ph-mcp-server.service /etc/systemd/system/

# 重新加载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable ph-mcp-server

# 启动服务
sudo systemctl start ph-mcp-server

# 检查状态
sudo systemctl status ph-mcp-server
```

## 配置 Nginx 反向代理（可选）

### 1. 安装 Nginx

```bash
sudo apt-get install -y nginx
```

### 2. 配置站点

```bash
# 复制配置文件
sudo cp deploy/nginx.conf /etc/nginx/sites-available/ph-mcp-server

# 修改配置
sudo nano /etc/nginx/sites-available/ph-mcp-server
# 修改 server_name 为你的域名

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/ph-mcp-server /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 3. 配置 SSL（使用 Let's Encrypt）

```bash
# 安装 certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 防火墙配置

### 使用 ufw

```bash
# 启用防火墙
sudo ufw enable

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS（如果使用 Nginx）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许 MCP Server 端口（仅在不使用 Nginx 时）
sudo ufw allow 8080/tcp

# 查看状态
sudo ufw status
```

## 服务管理命令

### systemd 命令

```bash
# 启动服务
sudo systemctl start ph-mcp-server

# 停止服务
sudo systemctl stop ph-mcp-server

# 重启服务
sudo systemctl restart ph-mcp-server

# 查看状态
sudo systemctl status ph-mcp-server

# 查看日志
sudo journalctl -u ph-mcp-server -f

# 查看最近 100 行日志
sudo journalctl -u ph-mcp-server -n 100

# 查看错误日志
sudo journalctl -u ph-mcp-server -p err

# 启用开机自启
sudo systemctl enable ph-mcp-server

# 禁用开机自启
sudo systemctl disable ph-mcp-server
```

## 监控和维护

### 查看日志

```bash
# 实时日志
sudo journalctl -u ph-mcp-server -f

# 查看今天的日志
sudo journalctl -u ph-mcp-server --since today

# 查看特定时间段
sudo journalctl -u ph-mcp-server --since "2024-01-01" --until "2024-01-02"
```

### 性能监控

```bash
# 查看资源使用
systemctl status ph-mcp-server

# 使用 htop 监控
sudo apt-get install htop
htop
```

### 更新部署

```bash
# 1. 拉取最新代码
cd /opt/ph_mcp_server
git pull

# 2. 更新依赖
uv sync --upgrade

# 3. 重启服务
sudo systemctl restart ph-mcp-server

# 4. 检查状态
sudo systemctl status ph-mcp-server
```

## 备份和恢复

### 备份

```bash
# 备份配置文件
sudo cp /opt/ph_mcp_server/.env /opt/ph_mcp_server/.env.backup

# 备份整个目录
sudo tar -czf ph_mcp_server_backup_$(date +%Y%m%d).tar.gz /opt/ph_mcp_server
```

### 恢复

```bash
# 恢复配置
sudo cp /opt/ph_mcp_server/.env.backup /opt/ph_mcp_server/.env

# 恢复整个目录
sudo tar -xzf ph_mcp_server_backup_20240101.tar.gz -C /
```

## 故障排查

### 服务无法启动

```bash
# 检查日志
sudo journalctl -u ph-mcp-server -n 50

# 检查配置文件
cat /opt/ph_mcp_server/.env

# 检查端口占用
sudo netstat -tulpn | grep 8080

# 手动运行测试
cd /opt/ph_mcp_server
python3 server.py
```

### 性能问题

```bash
# 检查资源使用
top
htop

# 检查磁盘空间
df -h

# 检查内存
free -h
```

### 网络问题

```bash
# 检查端口监听
sudo netstat -tulpn | grep 8080

# 测试本地连接
curl http://localhost:8080/health

# 测试外部连接（从另一台机器）
curl http://your-server-ip:8080/health
```

## 安全建议

1. **使用非 root 用户运行服务**
   - 服务默认使用 `www-data` 用户

2. **配置防火墙**
   - 只开放必要的端口
   - 使用 ufw 或 iptables

3. **使用 HTTPS**
   - 配置 SSL 证书
   - 使用 Let's Encrypt 免费证书

4. **定期更新**
   - 更新系统包：`sudo apt-get update && sudo apt-get upgrade`
   - 更新 Python 依赖：`uv sync --upgrade`

5. **备份数据**
   - 定期备份 .env 配置
   - 备份 Supabase 数据库

6. **监控日志**
   - 定期检查错误日志
   - 设置日志轮转

## 生产环境检查清单

部署前确认：

- [ ] 系统已更新到最新
- [ ] 已安装所有依赖
- [ ] .env 文件配置正确
- [ ] 防火墙规则已配置
- [ ] systemd 服务已启用
- [ ] 日志正常输出
- [ ] 健康检查端点可访问
- [ ] Nginx 反向代理配置正确（如果使用）
- [ ] SSL 证书已配置（如果使用 HTTPS）
- [ ] 监控和告警已设置

## 获取帮助

- 📖 主文档: [README.md](../README.md)
- 🔧 开发指南: [DEVELOPMENT.md](../DEVELOPMENT.md)
- 🐛 报告问题: [GitHub Issues](<your-repo-url>/issues)
