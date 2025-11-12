#!/bin/bash
# Product Hunt MCP Server 启动

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "错误: 请先运行 ./install.sh"
    exit 1
fi

source .venv/bin/activate
exec python server.py
