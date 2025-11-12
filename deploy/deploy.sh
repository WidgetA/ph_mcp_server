#!/bin/bash
# Ubuntu Server 部署脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
INSTALL_DIR="/opt/ph_mcp_server"
SERVICE_FILE="ph-mcp-server.service"
SERVICE_USER="www-data"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Product Hunt MCP Server - Ubuntu 部署${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 检查 Ubuntu 版本
echo -e "${YELLOW}[1/8] 检查系统版本...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "操作系统: $NAME $VERSION"
else
    echo -e "${RED}错误: 无法确定操作系统版本${NC}"
    exit 1
fi

# 安装系统依赖
echo -e "${YELLOW}[2/8] 安装系统依赖...${NC}"
apt-get update
apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    curl \
    build-essential \
    nginx \
    ufw

echo "Python 版本: $(python3 --version)"
echo "pip 版本: $(pip3 --version)"

# 创建安装目录
echo -e "${YELLOW}[3/8] 创建安装目录...${NC}"
mkdir -p $INSTALL_DIR

# 复制项目文件
echo -e "${YELLOW}[4/8] 复制项目文件...${NC}"
if [ ! -f "server.py" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

cp -r . $INSTALL_DIR/
cd $INSTALL_DIR

# 创建虚拟环境
echo -e "${YELLOW}[5/8] 创建虚拟环境...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# 安装 Python 依赖
echo -e "${YELLOW}[6/8] 安装 Python 依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 配置环境变量
echo -e "${YELLOW}[7/8] 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}请编辑 $INSTALL_DIR/.env 文件并填入配置${NC}"
    echo -e "${YELLOW}按任意键继续...${NC}"
    read -n 1 -s
fi

# 设置权限
echo -e "${YELLOW}[8/8] 设置权限和服务...${NC}"
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
chmod +x setup.sh start.sh

# 安装 systemd 服务
cp deploy/$SERVICE_FILE /etc/systemd/system/
systemctl daemon-reload
systemctl enable $SERVICE_FILE

# 配置防火墙
echo -e "${YELLOW}配置防火墙...${NC}"
ufw allow 8080/tcp
echo "防火墙规则已添加（端口 8080）"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "下一步:"
echo "1. 编辑配置文件: sudo nano $INSTALL_DIR/.env"
echo "2. 启动服务: sudo systemctl start $SERVICE_FILE"
echo "3. 查看状态: sudo systemctl status $SERVICE_FILE"
echo "4. 查看日志: sudo journalctl -u $SERVICE_FILE -f"
echo "5. 访问: http://your-server-ip:8080/health"
echo ""
echo "其他命令:"
echo "  sudo systemctl stop $SERVICE_FILE     # 停止服务"
echo "  sudo systemctl restart $SERVICE_FILE  # 重启服务"
echo "  sudo systemctl disable $SERVICE_FILE  # 禁用自启动"
echo ""
