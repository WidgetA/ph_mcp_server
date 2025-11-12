# 故障排查指南

本文档列出了常见问题及其解决方案。

## HTTP 405 错误：Method Not Allowed

### 问题描述

客户端连接时出现以下错误：
```
Error: Error POSTing to endpoint (HTTP 405): Method Not Allowed
```

### 原因

MCP 的 SSE transport 需要两个端点：
1. **GET `/sse`** - 用于建立 SSE 事件流（服务器到客户端的单向推送）
2. **POST `/messages`** - 用于接收客户端消息（客户端到服务器的双向通信）

如果只配置了 GET 端点，客户端尝试 POST 消息时就会返回 405 错误。

### 解决方案

已在 v1.0.1 中修复。确保 `server.py` 包含以下路由配置：

```python
# 创建 SSE transport
sse_transport = SseServerTransport("/messages")

# 处理 SSE 连接 (GET 请求建立 SSE 流)
async def handle_sse(scope, receive, send):
    """处理 SSE 连接 (GET)"""
    async with sse_transport.connect_sse(scope, receive, send) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )

# 处理客户端消息 (POST 请求发送消息)
async def handle_messages(scope, receive, send):
    """处理客户端消息 (POST)"""
    async with sse_transport.connect_sse(scope, receive, send) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )

# Starlette 路由配置
app = Starlette(
    debug=True,
    routes=[
        Route("/", root),
        Route("/health", health_check),
        Route("/sse", handle_sse, methods=["GET"]),          # SSE 事件流
        Route("/messages", handle_messages, methods=["POST"]),  # 客户端消息
    ]
)
```

### 验证修复

1. **重启服务器**：
   ```bash
   python server.py
   ```

2. **检查日志输出**：
   ```
   MCP SSE 端点: http://0.0.0.0:8080/sse (GET)
   MCP 消息端点: http://0.0.0.0:8080/messages (POST)
   ```

3. **测试端点**：
   ```bash
   # 测试健康检查
   curl http://localhost:8080/health

   # 测试根路径（查看端点信息）
   curl http://localhost:8080/
   ```

4. **重新连接客户端**

### Nginx 配置注意事项

如果使用 Nginx 反向代理，确保同时代理两个端点：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 配置...

    # 代理所有请求到后端
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;

        # WebSocket/SSE 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 其他代理头...

        # SSE 特殊配置
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;  # 24小时
    }
}
```

这个配置会自动代理 `/sse` (GET) 和 `/messages` (POST) 两个端点。

---

## 连接超时或断开

### 问题描述

SSE 连接建立后很快断开，或者出现超时错误。

### 原因

1. Nginx 代理的超时设置太短
2. 缺少 SSE 相关的代理配置
3. 缓冲设置不正确

### 解决方案

在 Nginx 配置中添加以下设置：

```nginx
location / {
    proxy_pass http://localhost:8080;
    proxy_http_version 1.1;

    # WebSocket/SSE 支持
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # SSE 关键配置
    proxy_buffering off;           # 禁用缓冲
    proxy_cache off;               # 禁用缓存
    proxy_read_timeout 86400;      # 24小时超时（SSE 长连接）

    # 超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
}
```

重启 Nginx：
```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## Supabase 连接失败

### 问题描述

```
Error: Could not connect to Supabase
```

### 原因

1. `.env` 文件配置错误
2. Supabase URL 或 KEY 无效
3. 网络无法访问 Supabase

### 解决方案

1. **检查 `.env` 文件**：
   ```bash
   cat .env
   ```

   确保包含：
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   PRODUCTS_TABLE=ph_products
   REPORTS_TABLE=ph_daily_reports
   ```

2. **测试 Supabase 连接**：
   ```python
   from supabase import create_client
   import os
   from dotenv import load_dotenv

   load_dotenv()
   client = create_client(
       os.getenv("SUPABASE_URL"),
       os.getenv("SUPABASE_KEY")
   )
   print("Connection successful!")
   ```

3. **检查防火墙**：
   ```bash
   # 确保可以访问 Supabase
   curl https://your-project.supabase.co
   ```

---

## 端口被占用

### 问题描述

```
Error: Address already in use
```

### 原因

8080 端口已被其他程序占用。

### 解决方案

1. **查找占用端口的进程**：
   ```bash
   sudo lsof -i :8080
   # 或
   sudo netstat -tlnp | grep 8080
   ```

2. **停止占用的进程**：
   ```bash
   sudo kill <PID>
   ```

3. **或使用其他端口**：
   ```bash
   # 修改 .env 文件
   echo "MCP_SERVER_PORT=8081" >> .env

   # 重启服务器
   python server.py
   ```

---

## 工具调用失败

### 问题描述

客户端调用 MCP 工具时返回错误。

### 可能原因

1. 数据库表不存在
2. 数据库权限不足
3. 参数格式错误

### 解决方案

1. **检查数据库表**：
   ```sql
   -- 在 Supabase SQL 编辑器中运行
   SELECT * FROM ph_products LIMIT 1;
   SELECT * FROM ph_daily_reports LIMIT 1;
   ```

2. **检查服务器日志**：
   ```bash
   # 如果使用 systemd
   sudo journalctl -u ph-mcp-server -n 50

   # 或直接运行查看输出
   python server.py
   ```

3. **测试单个工具**：
   在客户端尝试最简单的调用：
   ```
   "显示今天 Product Hunt 上的产品"
   ```

---

## SSL 证书问题

### 问题描述

HTTPS 连接失败或证书警告。

### 解决方案

1. **检查证书状态**：
   ```bash
   sudo certbot certificates
   ```

2. **测试 SSL 连接**：
   ```bash
   openssl s_client -connect your-domain.com:443 -servername your-domain.com
   ```

3. **续期证书**：
   ```bash
   sudo certbot renew
   sudo systemctl restart nginx
   ```

4. **检查证书路径**：
   ```bash
   ls -l /etc/letsencrypt/live/your-domain.com/
   ```

详细 HTTPS 配置请参考：[HTTPS_SETUP.md](HTTPS_SETUP.md)

---

## 性能问题

### 问题描述

响应缓慢或超时。

### 可能原因

1. 数据库查询慢
2. 返回数据量太大
3. 服务器资源不足

### 解决方案

1. **限制返回数量**：
   ```
   "显示今天前 10 个产品"  # 而不是全部
   ```

2. **检查服务器资源**：
   ```bash
   # 查看 CPU 和内存使用
   htop

   # 查看服务状态
   sudo systemctl status ph-mcp-server
   ```

3. **优化数据库查询**：
   - 确保数据库表有索引
   - 检查 Supabase 性能指标

4. **增加超时时间**：
   在 Nginx 配置中：
   ```nginx
   proxy_read_timeout 120;
   ```

---

## 日志查看

### systemd 服务日志

```bash
# 查看最近日志
sudo journalctl -u ph-mcp-server -n 100

# 实时跟踪日志
sudo journalctl -u ph-mcp-server -f

# 查看错误日志
sudo journalctl -u ph-mcp-server -p err

# 查看今天的日志
sudo journalctl -u ph-mcp-server --since today
```

### Nginx 日志

```bash
# 访问日志
sudo tail -f /var/log/nginx/ph-mcp-server-access.log

# 错误日志
sudo tail -f /var/log/nginx/ph-mcp-server-error.log

# SSL 日志（如果配置了）
sudo tail -f /var/log/nginx/ph-mcp-server-ssl-access.log
```

### 直接运行查看日志

```bash
# 前台运行，直接查看输出
python server.py
```

---

## 获取帮助

如果以上方法都无法解决问题：

1. **查看日志**：收集错误日志信息
2. **检查配置**：确认所有配置文件正确
3. **测试连接**：使用 curl 测试各个端点
4. **提交 Issue**：在 GitHub 上提交问题，附上：
   - 错误信息
   - 日志输出
   - 配置文件（隐藏敏感信息）
   - 系统环境信息

---

## 常用诊断命令

```bash
# 检查服务状态
sudo systemctl status ph-mcp-server

# 检查端口监听
sudo netstat -tlnp | grep -E ':(8080|443|80)'

# 测试健康检查
curl http://localhost:8080/health

# 测试 HTTPS（如果配置了）
curl https://your-domain.com/health

# 查看 Nginx 配置
sudo nginx -t

# 重启所有服务
sudo systemctl restart ph-mcp-server
sudo systemctl restart nginx

# 查看进程
ps aux | grep server.py
```

---

**更新时间**: 2024-11-12
**版本**: 1.0.1
