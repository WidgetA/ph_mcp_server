# HTTPS 配置指南

本文档详细说明如何为 Product Hunt MCP Server 配置 HTTPS。

## 为什么使用 HTTPS

- 🔒 **安全性**: 加密传输数据，防止中间人攻击
- ✅ **兼容性**: 许多客户端要求使用 HTTPS
- 🌐 **SEO 友好**: 搜索引擎更青睐 HTTPS 网站
- 📱 **现代标准**: HTTPS 已成为 Web 服务的标准配置

## 前置条件

- ✅ 已部署 MCP Server 到 Ubuntu 服务器
- ✅ 拥有域名（如 example.com）
- ✅ 域名已解析到服务器 IP
- ✅ 服务器已安装 Nginx

## 快速配置（推荐）

### 步骤 1：安装 Certbot

Certbot 是 Let's Encrypt 的官方客户端，可以自动获取和续期免费 SSL 证书。

```bash
# 更新包列表
sudo apt-get update

# 安装 certbot 和 nginx 插件
sudo apt-get install -y certbot python3-certbot-nginx
```

### 步骤 2：配置 Nginx

确保你的 Nginx 配置文件已经正确设置：

```bash
# 编辑 Nginx 配置
sudo nano /etc/nginx/sites-available/ph-mcp-server

# 确保 server_name 设置为你的域名
# server_name your-domain.com;
```

基础 HTTP 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 特殊配置
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
```

测试并重启 Nginx：

```bash
# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 步骤 3：获取 SSL 证书

运行 Certbot 自动获取证书并配置 Nginx：

```bash
sudo certbot --nginx -d your-domain.com
```

Certbot 会询问以下问题：

1. **Email**: 输入你的邮箱（用于证书到期通知）
2. **同意服务条款**: 输入 `Y`
3. **是否重定向 HTTP 到 HTTPS**: 推荐选择 `2`（重定向）

### 步骤 4：验证 HTTPS

访问你的域名：

```bash
# 测试 HTTPS 连接
curl https://your-domain.com/health
```

应该返回：
```json
{
  "status": "healthy",
  "service": "Product Hunt MCP Server",
  "version": "1.0.0"
}
```

## 配置 MCP 客户端

### Claude Desktop 配置

编辑配置文件（根据你的操作系统）：

```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "https://your-domain.com/sse"
    }
  }
}
```

重启 Claude Desktop 即可。

## SSL 证书管理

### 自动续期

Let's Encrypt 证书有效期为 90 天，但 Certbot 已自动配置续期任务。

查看续期任务：

```bash
# 检查 certbot 定时任务
sudo systemctl list-timers | grep certbot

# 或查看 cron 任务
sudo cat /etc/cron.d/certbot
```

测试续期（不会实际续期）：

```bash
sudo certbot renew --dry-run
```

### 手动续期

如果需要手动续期：

```bash
# 续期所有证书
sudo certbot renew

# 续期后重启 Nginx
sudo systemctl restart nginx
```

### 查看证书信息

```bash
# 查看所有证书
sudo certbot certificates

# 查看证书详情
sudo openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout
```

## 高级配置

### 完整的 Nginx HTTPS 配置

Certbot 会自动生成配置，但你也可以手动优化：

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS（可选但推荐）
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 其他安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 访问日志
    access_log /var/log/nginx/ph-mcp-server-ssl-access.log;
    error_log /var/log/nginx/ph-mcp-server-ssl-error.log;

    # MCP Server 反向代理
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;

        # WebSocket/SSE 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 代理头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 特殊配置
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;  # 24小时

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
    }

    # 健康检查端点
    location /health {
        proxy_pass http://localhost:8080/health;
        access_log off;
    }
}
```

应用配置：

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 使用通配符证书

如果你有多个子域名：

```bash
# 获取通配符证书（需要 DNS 验证）
sudo certbot certonly --manual --preferred-challenges dns -d '*.your-domain.com' -d your-domain.com
```

### 使用自定义端口

如果 MCP Server 使用非标准端口（如 8443）：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # ... SSL 配置 ...

    location / {
        proxy_pass http://localhost:8080;  # 后端仍然是 HTTP
        # ... 其他配置 ...
    }
}
```

客户端配置：

```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "https://your-domain.com/sse"
    }
  }
}
```

## 故障排查

### 问题 1: 证书获取失败

```bash
# 错误: Challenge failed
```

**解决方案**:
1. 确认域名已正确解析到服务器 IP
2. 检查防火墙是否开放 80 和 443 端口
3. 确保 Nginx 正在运行

```bash
# 检查域名解析
dig your-domain.com

# 检查端口
sudo netstat -tlnp | grep -E ':(80|443)'

# 检查 Nginx
sudo systemctl status nginx
```

### 问题 2: SSL 证书未生效

```bash
# 测试 SSL
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

**解决方案**:
1. 检查 Nginx 配置是否正确
2. 确认证书路径正确
3. 重启 Nginx

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 问题 3: 混合内容警告

如果页面包含 HTTP 资源：

**解决方案**:
1. 确保所有资源都使用 HTTPS
2. 在 Nginx 配置中添加 HSTS 头
3. 使用内容安全策略（CSP）

### 问题 4: SSE 连接断开

```bash
# 错误: Connection reset
```

**解决方案**:

确保 Nginx 配置包含以下设置：

```nginx
proxy_buffering off;
proxy_cache off;
proxy_read_timeout 86400;  # 24小时
```

## 安全建议

### 1. 定期更新系统

```bash
sudo apt-get update && sudo apt-get upgrade
```

### 2. 配置防火墙

```bash
# 只允许必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. 监控证书到期

设置邮件通知或监控服务。

### 4. 使用强密码套件

在 Nginx 配置中使用现代加密算法（见上方配置）。

### 5. 启用 HSTS

强制浏览器使用 HTTPS：

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## 性能优化

### 1. 启用 HTTP/2

```nginx
listen 443 ssl http2;
```

### 2. SSL 会话缓存

```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### 3. OCSP Stapling

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/your-domain.com/chain.pem;
```

## 相关资源

- [Let's Encrypt 官网](https://letsencrypt.org/)
- [Certbot 文档](https://certbot.eff.org/)
- [Nginx SSL 配置生成器](https://ssl-config.mozilla.org/)
- [SSL Labs 测试](https://www.ssllabs.com/ssltest/)

## 测试 SSL 配置

使用在线工具测试你的 SSL 配置：

1. **SSL Labs**: https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com
2. **Security Headers**: https://securityheaders.com/?q=your-domain.com

目标评分：
- SSL Labs: A+ 级
- Security Headers: A 级或以上

---

配置完成后，你的 MCP Server 将通过安全的 HTTPS 连接提供服务！
