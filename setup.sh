#!/bin/bash
# Product Hunt MCP Server 快速设置脚本
# 适用于 Ubuntu/Debian Linux 和 macOS

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Product Hunt MCP Server - 快速设置${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""

# 检查操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
else
    echo -e "${RED}[错误] 不支持的操作系统: $OSTYPE${NC}"
    exit 1
fi
echo -e "${BLUE}操作系统: $OS${NC}"
echo ""

# 检查 Python 版本
echo -e "${YELLOW}[1/5] 检查 Python 版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未找到 Python 3${NC}"
    echo "请安装 Python 3.10 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"
echo ""

# 检查并安装 uv
echo -e "${YELLOW}[2/5] 检查 uv...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${BLUE}未检测到 uv，正在安装...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # 重新加载环境变量
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
    export PATH="$HOME/.cargo/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        echo -e "${RED}[错误] uv 安装失败${NC}"
        echo "请手动安装: https://github.com/astral-sh/uv"
        exit 1
    fi
    echo -e "${GREEN}✓ uv 安装成功${NC}"
else
    echo -e "${GREEN}✓ uv 已安装${NC}"
fi

UV_VERSION=$(uv --version)
echo -e "${GREEN}✓ uv 版本: $UV_VERSION${NC}"
echo ""

# 同步依赖并创建虚拟环境
echo -e "${YELLOW}[3/5] 同步依赖并创建虚拟环境...${NC}"
uv sync
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 依赖安装成功${NC}"
else
    echo -e "${RED}[错误] 依赖安装失败${NC}"
    exit 1
fi
echo ""

# 创建环境变量文件
echo -e "${YELLOW}[4/5] 创建环境变量文件...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ 已创建 .env 文件${NC}"
    echo -e "${BLUE}[提示] 请编辑 .env 文件，填入你的 Supabase 配置${NC}"
else
    echo -e "${BLUE}[提示] .env 文件已存在${NC}"
fi
echo ""

# 运行测试
echo -e "${YELLOW}[5/5] 运行测试...${NC}"
if python3 tests/test_server.py; then
    echo -e "${GREEN}✓ 测试通过${NC}"
else
    echo -e "${YELLOW}[警告] 测试失败，可能是因为未配置数据库${NC}"
fi
echo ""

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}设置完成！${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${BLUE}下一步:${NC}"
echo "1. 编辑配置文件: nano .env 或 vi .env"
echo "2. 填入 Supabase URL 和 KEY"
echo "3. 启动服务器:"
echo ""
echo -e "   ${GREEN}./start.sh${NC}          # 前台运行"
echo -e "   ${GREEN}make run${NC}            # 使用 Makefile"
echo -e "   ${GREEN}python3 server.py${NC}   # 直接运行"
echo ""
echo -e "${BLUE}部署到生产环境:${NC}"
echo "   sudo bash deploy/deploy.sh   # Ubuntu 服务器部署"
echo ""
echo -e "${BLUE}验证服务器:${NC}"
echo "   curl http://localhost:8080/health"
echo ""
echo -e "${BLUE}查看帮助:${NC}"
echo "   make help                    # 查看所有命令"
echo ""
