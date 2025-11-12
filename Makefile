.PHONY: help install dev run test clean venv

help: ## 显示帮助信息
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

venv: ## 创建虚拟环境
	python3 -m venv .venv
	@echo "虚拟环境已创建。激活方式："
	@echo "  Linux/macOS: source .venv/bin/activate"
	@echo "  Windows: .venv\\Scripts\\activate"

install: ## 安装项目依赖（使用 pip）
	pip install -r requirements.txt

dev: ## 安装开发依赖（使用 pip）
	pip install -r requirements-dev.txt

upgrade: ## 升级所有依赖到最新版本
	pip install --upgrade -r requirements.txt

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
