#!/bin/bash

# 🚀 MCP智能化问答应用 - GitHub部署脚本
# 作者: Alan

echo "🚀 开始部署MCP智能化问答应用到GitHub..."

# 检查Git是否安装
if ! command -v git &> /dev/null; then
    echo "❌ Git未安装，请先安装Git"
    exit 1
fi

echo "✅ Git已安装: $(git --version)"

# 检查当前目录
if [ ! -f "app/main.py" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 初始化Git仓库
if [ ! -d ".git" ]; then
    echo "📁 初始化Git仓库..."
    git init
else
    echo "📁 Git仓库已存在"
fi

# 添加文件
echo "📝 添加文件到Git..."
git add .

# 创建首次提交
echo "💾 创建首次提交..."
git commit -m "🎉 初始提交: MCP智能化问答应用

✨ 核心功能:
- 多数据库智能问答系统
- 本地GGUF模型 + 云端API易模型
- RBAC权限控制
- Docker一键部署
- 现代化Web界面

🚀 技术栈:
- FastAPI + SQLAlchemy
- MySQL + PostgreSQL
- llama-cpp-python
- Docker Compose

📚 完整文档和部署指南"

# 添加远程仓库
echo "🌐 配置远程仓库..."
git remote add origin https://github.com/Alansws/Alansws_mcp.git 2>/dev/null || git remote set-url origin https://github.com/Alansws/Alansws_mcp.git

# 推送到GitHub
echo "🚀 推送到GitHub..."
git branch -M main

if git push -u origin main; then
    echo "🎉 部署完成!"
    echo "📖 仓库地址: https://github.com/Alansws/Alansws_mcp"
else
    echo "❌ 推送失败，请检查:"
    echo "1. 是否已在GitHub上创建仓库 'Alansws_mcp'"
    echo "2. 是否已配置正确的认证方式"
    echo "3. 网络连接是否正常"
fi
