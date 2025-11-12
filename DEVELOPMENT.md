# 开发指南

本文档介绍如何使用 uv 进行 Product Hunt MCP Server 的开发。

## 安装 uv

### Windows

使用 PowerShell:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

或使用 pip:
```bash
pip install uv
```

### macOS/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

或使用 pip:
```bash
pip install uv
```

## 项目设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd ph_mcp_server
```

### 2. 初始化项目

**方式 1: 使用 uv sync（推荐）**

这会自动创建虚拟环境、安装所有依赖并生成 lock 文件：

```bash
uv sync
```

**方式 2: 手动步骤**

```bash
# 生成 lock 文件
uv lock

# 安装依赖
uv pip install -e .

# 安装开发依赖
uv pip install -e ".[dev]"
```

**方式 3: 使用 Makefile**

```bash
# 同步所有依赖
make sync

# 或分别安装
make install  # 生产依赖
make dev      # 开发依赖
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

## 开发工作流

### 添加新依赖

```bash
# 添加生产依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 这会自动更新 pyproject.toml 和 uv.lock
```

### 移除依赖

```bash
uv remove package-name
```

### 更新依赖

```bash
# 更新所有依赖
uv sync --upgrade

# 更新特定包
uv add package-name --upgrade

# 重新生成 lock 文件
uv lock --upgrade
```

### 运行服务器

```bash
# 方式 1: 使用 make
make run

# 方式 2: 使用 uv run
uv run server.py

# 方式 3: 激活虚拟环境后运行
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
python server.py
```

### 运行测试

```bash
# 使用 make
make test

# 或直接运行
python tests/test_server.py

# 使用 pytest（需安装开发依赖）
uv run pytest tests/ -v
```

### 代码质量检查

```bash
# 格式化代码（black）
uv run black .

# 检查代码风格（ruff）
uv run ruff check .

# 自动修复问题
uv run ruff check --fix .
```

## 项目结构

```
ph_mcp_server/
├── pyproject.toml         # uv 项目配置（依赖管理）
├── .python-version        # Python 版本锁定
├── uv.lock               # 依赖锁定文件
├── requirements.txt      # 传统 pip 依赖（备份）
├── Makefile              # 常用命令快捷方式
├── .env.example          # 环境变量模板
├── .gitignore            # Git 忽略文件
├── README.md             # 项目文档
├── DEVELOPMENT.md        # 开发指南（本文件）
├── server.py             # MCP server 主文件
├── config.py             # 配置管理
├── services/             # 服务模块
│   ├── __init__.py
│   └── supabase_service.py
└── tests/                # 测试文件
    ├── __init__.py
    └── test_server.py
```

## 虚拟环境管理

uv 会自动在 `.venv` 目录创建虚拟环境。

### 激活虚拟环境

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 停用虚拟环境

```bash
deactivate
```

## 常见问题

### Q: uv.lock 文件是什么？

A: `uv.lock` 是依赖锁定文件，确保所有开发者使用相同版本的依赖。类似于 `package-lock.json` (npm) 或 `Cargo.lock` (Rust)。

### Q: 应该提交 uv.lock 到 Git 吗？

A: 是的！`uv.lock` 应该提交到版本控制，这样团队成员可以获得完全相同的依赖版本。

### Q: requirements.txt 还需要吗？

A: 保留 `requirements.txt` 作为备份，但主要使用 `pyproject.toml` 和 `uv.lock` 进行依赖管理。

### Q: 如何从 pip 迁移到 uv？

A: 项目已经配置好 `pyproject.toml`，只需运行 `uv sync` 即可。

### Q: uv 比 pip 快多少？

A: uv 通常比 pip 快 10-100 倍，特别是在安装大量依赖时。

## 最佳实践

1. **始终使用 uv sync**: 确保依赖与 lock 文件同步
2. **提交 lock 文件**: 确保团队依赖一致
3. **使用 Makefile**: 简化常用命令
4. **定期更新依赖**: 使用 `uv sync --upgrade` 保持最新
5. **代码质量检查**: 提交前运行 black 和 ruff

## 发布清单

在发布新版本前：

- [ ] 运行所有测试：`make test`
- [ ] 格式化代码：`uv run black .`
- [ ] 检查代码质量：`uv run ruff check .`
- [ ] 更新依赖：`uv sync --upgrade`
- [ ] 测试服务器启动：`python server.py`（验证无错误）
- [ ] 更新 CHANGELOG.md
- [ ] 更新版本号（pyproject.toml）
- [ ] 创建 Git tag

## 获取帮助

- uv 文档: https://github.com/astral-sh/uv
- MCP 文档: https://modelcontextprotocol.io/
- 项目 Issues: <your-repo-url>/issues
