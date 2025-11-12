#!/bin/bash
# Ubuntu 服务器更新脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

INSTALL_DIR="/opt/ph_mcp_server"
SERVICE_NAME="ph-mcp-server"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Product Hunt MCP Server - 更新${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 检查安装目录
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}错误: 未找到安装目录 $INSTALL_DIR${NC}"
    echo "请先运行 deploy.sh 进行初始部署"
    exit 1
fi

cd $INSTALL_DIR

echo -e "${YELLOW}[1/6] 停止服务...${NC}"
systemctl stop $SERVICE_NAME
echo -e "${GREEN}✓ 服务已停止${NC}"
echo ""

echo -e "${YELLOW}[2/6] 备份当前配置...${NC}"
BACKUP_DIR="/tmp/ph_mcp_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp .env $BACKUP_DIR/.env
echo -e "${GREEN}✓ 配置已备份到 $BACKUP_DIR${NC}"
echo ""

echo -e "${YELLOW}[3/6] 拉取最新代码...${NC}"
if [ -d ".git" ]; then
    git pull
    echo -e "${GREEN}✓ 代码已更新${NC}"
else
    echo -e "${YELLOW}警告: 不是 Git 仓库，请手动更新代码${NC}"
fi
echo ""

echo -e "${YELLOW}[4/6] 更新依赖...${NC}"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade -r requirements.txt
    echo -e "${GREEN}✓ 依赖已更新${NC}"
else
    echo -e "${RED}错误: 未找到虚拟环境${NC}"
    echo "正在创建虚拟环境..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ 虚拟环境已创建并安装依赖${NC}"
fi
echo ""

echo -e "${YELLOW}[5/6] 设置权限...${NC}"
chown -R www-data:www-data $INSTALL_DIR
echo -e "${GREEN}✓ 权限已设置${NC}"
echo ""

echo -e "${YELLOW}[6/6] 启动服务...${NC}"
systemctl start $SERVICE_NAME
sleep 2
systemctl status $SERVICE_NAME --no-pager
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}更新完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "备份位置: $BACKUP_DIR"
echo ""
echo "检查服务状态:"
echo "  sudo systemctl status $SERVICE_NAME"
echo ""
echo "查看日志:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "测试健康检查:"
echo "  curl http://localhost:8080/health"
echo ""
