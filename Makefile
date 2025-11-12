.PHONY: help install dev run test clean

help: ## 显示帮助信息
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 安装项目依赖
	uv pip install -e .

dev: ## 安装开发依赖
	uv pip install -e ".[dev]"

sync: ## 同步依赖（使用 uv sync）
	uv sync

lock: ## 生成 uv.lock 文件
	uv lock

run: ## 运行服务器
	python3 server.py

test: ## 运行测试
	python3 tests/test_server.py

clean: ## 清理临时文件
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf build/ dist/ *.egg-info/
