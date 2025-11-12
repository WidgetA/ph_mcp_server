# 容器环境配置指南

本文档说明如何在容器环境中配置和运行 Product Hunt MCP Server。

## 环境变量配置

### uv 缓存目录

在容器中运行时，需要配置可写的缓存目录：

```dockerfile
# Dockerfile 示例
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV UV_LINK_MODE=copy
```

或者在运行时设置：

```bash
export UV_CACHE_DIR=/tmp/uv-cache
export UV_LINK_MODE=copy
```

### 应用配置

```bash
# Supabase 配置（必需）
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# 数据库表名
PRODUCTS_TABLE=ph_products
REPORTS_TABLE=ph_daily_reports

# 服务器配置
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
```

## 安装依赖

### 使用缓存目录

```bash
# 指定缓存目录
uv sync --cache-dir /tmp/uv-cache

# 或使用环境变量
export UV_CACHE_DIR=/tmp/uv-cache
uv sync
```

### 不使用缓存（适用于只读文件系统）

```bash
# 完全禁用缓存
uv sync --no-cache

# 或使用环境变量
export UV_NO_CACHE=1
uv sync
```

### 使用系统 Python

如果容器中已有 Python：

```bash
# 使用系统 Python
uv venv --python /usr/bin/python3.10
uv sync
```

## 容器启动示例

### 基本启动

```bash
# 设置环境
export UV_CACHE_DIR=/tmp/uv-cache
export SUPABASE_URL=your_url
export SUPABASE_KEY=your_key

# 安装依赖
uv sync --no-cache

# 启动服务
python server.py
```

### 使用脚本启动

```bash
#!/bin/bash
set -e

# 配置 uv
export UV_CACHE_DIR=/tmp/uv-cache
export UV_NO_CACHE=1

# 安装依赖（如果需要）
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    uv sync --no-cache
fi

# 启动服务
echo "Starting MCP server..."
exec python server.py
```

## 常见问题

### Q: 为什么会出现 "Read-only file system" 错误？

A: uv 默认将缓存存储在 `~/.cache/uv/` 目录，在某些容器环境中这个目录可能是只读的。

**解决方案**：
1. 设置 `UV_CACHE_DIR` 到可写位置（如 `/tmp/uv-cache`）
2. 使用 `--no-cache` 禁用缓存
3. 在容器配置中挂载可写的缓存卷

### Q: 如何优化容器构建速度？

A: 挂载持久化的缓存卷：

```bash
# 运行容器时挂载缓存
docker run -v uv-cache:/tmp/uv-cache \
  -e UV_CACHE_DIR=/tmp/uv-cache \
  your-image
```

### Q: 依赖安装很慢怎么办？

A: 使用预构建的依赖层：

```bash
# 第一次构建时缓存依赖
uv sync --cache-dir /tmp/uv-cache

# 后续构建重用缓存
# 确保 /tmp/uv-cache 被持久化
```

### Q: 需要在容器中使用虚拟环境吗？

A: 在容器中可以选择不使用虚拟环境：

```bash
# 直接安装到系统 Python
uv pip install --system -r requirements.txt

# 或继续使用虚拟环境（推荐）
uv sync
```

## 推荐配置

### 最小配置（生产环境）

```bash
# 环境变量
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV UV_NO_CACHE=1
ENV PYTHONUNBUFFERED=1

# 仅安装生产依赖
RUN uv sync --no-dev --no-cache

# 启动服务
CMD ["python", "server.py"]
```

### 开发配置

```bash
# 环境变量
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV PYTHONUNBUFFERED=1

# 安装所有依赖（包括开发依赖）
RUN uv sync --cache-dir /tmp/uv-cache

# 启动服务
CMD ["python", "server.py"]
```

## 性能优化

### 1. 使用本地 requirements.txt

如果 uv 在容器中遇到问题，可以回退使用 pip：

```bash
# 生成 requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# 使用 pip 安装
pip install -r requirements.txt
```

### 2. 分层构建

```bash
# 第一层：安装 uv 和基础工具
# ...

# 第二层：复制 pyproject.toml 并安装依赖
# COPY pyproject.toml .
# RUN uv sync --no-cache

# 第三层：复制应用代码
# COPY . .

# 第四层：启动服务
# CMD ["python", "server.py"]
```

### 3. 清理缓存

```bash
# 安装后清理缓存（如果使用了缓存）
RUN uv sync --cache-dir /tmp/uv-cache && \
    rm -rf /tmp/uv-cache
```

## 验证安装

```bash
# 检查 Python 版本
python --version

# 检查已安装的包
uv pip list

# 测试服务启动
python -c "import server; print('OK')"

# 测试健康检查
curl http://localhost:8080/health
```

## 故障排查

### 权限问题

```bash
# 确保工作目录可写
chmod -R 755 /app

# 确保 .venv 目录可写
chmod -R 755 .venv
```

### 依赖冲突

```bash
# 清理并重新安装
rm -rf .venv
uv sync --no-cache --reinstall
```

### 网络问题

```bash
# 使用镜像源
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 增加超时
export UV_HTTP_TIMEOUT=120
```

## 参考资源

- uv 文档: https://github.com/astral-sh/uv
- 容器最佳实践: https://docs.docker.com/develop/dev-best-practices/
- MCP 文档: https://modelcontextprotocol.io/
