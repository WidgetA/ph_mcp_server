# 迁移到 pip 管理 - 改动总结

## 📝 改动概述

由于线上环境对 uv 的支持不够完善，项目已迁移到使用传统的 pip + venv 进行包管理。

## 🔄 主要改动

### 1. 依赖管理

**之前（uv）：**
```bash
uv sync
uv add package-name
uv run server.py
```

**现在（pip）：**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

### 2. 更新的文件

#### 配置文件
- ✅ `requirements.txt` - 添加了完整的依赖列表（包括 uvicorn 和 starlette）
- ✅ `pyproject.toml` - 添加了 hatchling 构建配置（保留用于开发）
- ✅ `Makefile` - 改用 pip 命令

#### 脚本文件
- ✅ `setup.sh` - 改用 pip 和 venv
- ✅ `deploy/deploy.sh` - 改用 pip 和 venv
- ✅ `deploy/update.sh` - 改用 pip 和 venv

#### 文档文件
- ✅ `QUICKSTART.md` - 完全重写，以 pip 为主
- ✅ `PROJECT_SUMMARY.md` - 更新技术栈说明
- ✅ `CONTAINER_SETUP.md` - 添加容器环境配置（支持 pip 和 uv）

### 3. 保留的 uv 配置

以下文件保留用于本地开发（可选）：
- `pyproject.toml` - 依然可以用 uv，但不推荐生产环境使用
- `.python-version` - Python 版本锁定
- `DEVELOPMENT.md` - 包含 uv 的使用说明（作为可选项）

## 🚀 快速开始（新方式）

### 本地开发

```bash
# 1. 克隆项目
git clone <repository-url>
cd ph_mcp_server

# 2. 运行自动设置
chmod +x setup.sh
./setup.sh

# 3. 配置环境变量
cp .env.example .env
nano .env  # 填入 Supabase 配置

# 4. 启动服务器
python3 server.py
```

### Ubuntu 服务器部署

```bash
# 1. 上传项目到服务器
scp -r ph_mcp_server user@server:/tmp/

# 2. SSH 到服务器
ssh user@server

# 3. 运行部署脚本
cd /tmp/ph_mcp_server
sudo bash deploy/deploy.sh

# 4. 配置并启动
sudo nano /opt/ph_mcp_server/.env
sudo systemctl start ph-mcp-server
```

### 容器环境

参考 [CONTAINER_SETUP.md](CONTAINER_SETUP.md) 获取详细的容器配置说明。

## 📦 requirements.txt 内容

```
mcp>=1.1.0
supabase==2.10.0
pydantic-settings==2.6.1
python-dotenv==1.0.1
httpx==0.27.2
uvicorn[standard]>=0.32.0
starlette>=0.35.0
```

## 🛠️ 常用命令对比

| 操作 | uv (旧) | pip (新) |
|------|---------|----------|
| 创建环境 | `uv sync` | `python3 -m venv .venv && source .venv/bin/activate` |
| 安装依赖 | `uv sync` | `pip install -r requirements.txt` |
| 添加依赖 | `uv add package` | `pip install package && pip freeze > requirements.txt` |
| 升级依赖 | `uv sync --upgrade` | `pip install --upgrade -r requirements.txt` |
| 运行服务器 | `uv run server.py` | `python server.py` |
| 运行测试 | `uv run pytest` | `python tests/test_server.py` |

## ⚙️ Makefile 命令

新的 Makefile 命令（使用 pip）：

```bash
make help       # 显示所有命令
make venv       # 创建虚拟环境
make install    # 安装依赖
make dev        # 安装开发依赖
make upgrade    # 升级所有依赖
make run        # 运行服务器
make test       # 运行测试
make clean      # 清理临时文件
```

## 🐛 故障排查

### 容器环境中的问题

如果在容器中仍然想使用 uv，参考 [CONTAINER_SETUP.md](CONTAINER_SETUP.md)：

```bash
# 方式 1: 设置缓存目录
export UV_CACHE_DIR=/tmp/uv-cache
uv sync

# 方式 2: 禁用缓存
export UV_NO_CACHE=1
uv sync --no-cache

# 方式 3: 使用 pip（推荐）
pip install -r requirements.txt
```

### hatchling 构建错误

如果遇到 "Unable to determine which files to ship" 错误：

这已经在 `pyproject.toml` 中修复，添加了：
```toml
[tool.hatch.build.targets.wheel]
packages = ["."]
only-include = [
    "server.py",
    "config.py",
    "services/",
]
```

但在生产环境中，不需要构建 wheel，直接运行即可。

## 📚 相关文档

- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始（pip 版本）
- [CONTAINER_SETUP.md](CONTAINER_SETUP.md) - 容器环境配置
- [deploy/README.md](deploy/README.md) - Ubuntu 部署指南
- [DEVELOPMENT.md](DEVELOPMENT.md) - 开发指南（包含 uv 可选说明）

## ✅ 验证迁移

运行以下命令验证安装：

```bash
# 1. 检查 Python
python3 --version  # 应该 >= 3.10

# 2. 检查 pip
pip --version

# 3. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 测试服务器
python server.py
# 打开另一个终端
curl http://localhost:8080/health

# 6. 运行测试
python tests/test_server.py
```

## 🎯 总结

- ✅ 所有脚本已更新为使用 pip + venv
- ✅ requirements.txt 包含所有依赖
- ✅ 文档已更新
- ✅ uv 配置保留作为可选项（本地开发）
- ✅ 生产环境推荐使用 pip（稳定可靠）

现在你可以在任何支持 Python 和 pip 的环境中部署项目，无需担心 uv 兼容性问题！
