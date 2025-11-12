#!/bin/bash
# Product Hunt MCP Server 安装脚本

cd "$(dirname "$0")"

echo "安装 Product Hunt MCP Server..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 创建虚拟环境
echo "[1/2] 创建虚拟环境..."
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
echo "[2/2] 安装依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "✓ 安装完成！"
echo ""
echo "下一步: ./run.sh 启动服务"
echo ""
