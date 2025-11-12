#!/bin/bash
# Product Hunt MCP Server 启动脚本 (Linux/macOS)

echo "============================================================"
echo "Product Hunt MCP Server (Remote Mode)"
echo "============================================================"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "[ERROR] .env 文件不存在！"
    echo "请先运行 python setup.py 创建配置文件"
    echo ""
    exit 1
fi

echo "[INFO] 启动 MCP 服务器..."
echo "[INFO] 端口: 8080"
echo "[INFO] 按 Ctrl+C 停止服务器"
echo ""

python server.py
