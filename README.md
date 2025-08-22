# 🚀 MCP 智能化问答应用

基于 FastAPI 的多数据库智能问答系统，支持医疗和仓储数据库的智能查询、本地大模型推理、云端AI服务调用，以及完整的RBAC权限控制。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Alansws_mcp-brightgreen.svg)](https://github.com/Alansws/Alansws_mcp)

## ✨ 项目特性

### 🎯 核心功能
- **🤖 智能模型路由**: 自动选择本地GGUF模型或云端API，支持手动切换
- **🗄️ 多数据库支持**: MySQL医疗数据库 + PostgreSQL仓储数据库
- **🔐 RBAC权限控制**: 基于角色的访问控制，确保数据安全
- **🌤️ 天气工具集成**: 支持Function Calling的天气查询功能
- **💻 现代化前端**: 响应式Web界面，支持桌面端和移动端
- **🐳 Docker一键部署**: 完整的容器化部署方案

### 🏗️ 技术架构
- **后端**: FastAPI + SQLAlchemy + Pydantic
- **前端**: HTML5 + CSS3 + JavaScript (响应式设计)
- **本地AI**: llama-cpp-python + GGUF模型
- **云端AI**: API易 (OpenAI兼容接口)
- **数据库**: MySQL 8.0 + PostgreSQL 15
- **部署**: Docker Compose + Uvicorn

## 🚀 快速开始

### 📋 系统要求

- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8+ (推荐3.9+)
- **内存**: 至少4GB RAM (使用本地模型建议8GB+)
- **存储**: 至少2GB可用空间
- **Docker**: Docker Desktop 或 Docker Engine

### 🔧 环境准备

#### 1. 克隆项目
```bash
# 克隆项目到本地
git clone https://github.com/Alansws/Alansws_mcp.git
cd Alansws_mcp

# 或者使用SSH (如果你配置了SSH密钥)
git clone git@github.com:Alansws/Alansws_mcp.git
cd Alansws_mcp
```

#### 2. 创建Python虚拟环境
```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 验证激活成功 (应该显示虚拟环境路径)
which python  # macOS/Linux
# where python  # Windows
```

#### 3. 安装依赖
```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 如果安装llama-cpp-python失败，可以尝试：
# pip install llama-cpp-python --no-cache-dir
```

### ⚙️ 配置环境变量

#### 1. 创建环境变量文件
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
# macOS/Linux:
nano .env
# 或者使用其他编辑器:
# code .env
# vim .env
```

#### 2. 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，配置以下内容:
# - 云端模型配置 (必需)
# - 本地模型配置 (可选)
# - 数据库配置 (使用Docker时保持默认即可)
```

**重要提示**:
- 如果你没有API易的API Key，可以注册获取: https://api.apiyi.com
- 本地模型路径是可选的，如果不配置，系统会自动使用云端模型
- 数据库配置使用Docker时保持默认即可
- 详细配置说明请参考 `env.example` 文件

### 🐳 启动数据库服务

#### 1. 启动Docker容器
```bash
# 启动MySQL和PostgreSQL容器
docker compose up -d

# 查看容器状态
docker ps

# 查看容器日志 (如果遇到问题)
docker logs mysql_hospital
docker logs postgres_warehouse
```

#### 2. 等待数据库初始化
```bash
# 等待约30秒让数据库完全启动
# 可以查看日志确认初始化完成
docker logs mysql_hospital | grep "ready for connections"
docker logs postgres_warehouse | grep "database system is ready"
```

### 🚀 启动应用

#### 1. 启动FastAPI服务
```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 验证服务状态
```bash
# 健康检查
curl http://localhost:8000/api/health

# 测试数据库连接
curl http://localhost:8000/api/test_db_connections
```

### 🌐 访问应用

- **🌍 Web界面**: http://localhost:8000
- **📚 API文档**: http://localhost:8000/docs
- **🔍 交互式API**: http://localhost:8000/redoc

## 🎯 使用指南

### 💻 前端界面操作

#### 1. 基本操作流程
1. **选择数据库**: 在左侧面板选择医疗数据库或仓储数据库
2. **选择用户角色**: 根据你的身份选择相应的用户角色
3. **选择AI模型**: 选择自动选择、本地模型或云端模型
4. **开始提问**: 在右侧输入框输入问题或点击快速示例

#### 2. 模型选择说明
- **🤖 自动选择**: 系统智能判断，优先使用本地模型，失败时自动降级
- **🏠 本地模型**: 强制使用本地GGUF模型 (需要配置模型文件)
- **☁️ 云端模型**: 强制使用API易云端模型，可选择不同模型

#### 3. 快速示例
- 点击左侧的快速示例按钮，系统会自动填充预设问题
- 包含数据库查询、天气查询、知识问答等类型

### 🔌 API接口使用

#### 1. 智能问答
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "D101",
    "question": "查询所有心内科的医生信息",
    "model_type": "auto"
  }'
```

#### 2. 切换数据库
```bash
# 切换到医疗数据库
curl -X POST http://localhost:8000/api/switch_db \
  -H "Content-Type: application/json" \
  -d '{"target": "hospital"}'

# 切换到仓储数据库
curl -X POST http://localhost:8000/api/switch_db \
  -H "Content-Type: application/json" \
  -d '{"target": "warehouse"}'
```

#### 3. 模型管理
```bash
# 获取模型状态
curl http://localhost:8000/api/models/status

# 切换模型
curl -X POST http://localhost:8000/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_type": "cloud", "model_name": "deepseek-r1"}'
```

### 👥 用户角色与权限

#### 医疗数据库角色
- **D101-D104**: 医生用户，可访问医生、病人、诊疗记录表
- **P001-P010**: 病人用户，只读权限

#### 仓储数据库角色
- **S1001**: 仓库经理 (Manager)，完整权限
- **S1002-S1004**: 仓库操作员 (Operator)，不能查看价格信息

## 🔧 配置详解

### 📁 项目结构
```
Alansws_mcp/
├── app/                    # 主应用代码
│   ├── api/               # API路由
│   ├── db/                # 数据库管理
│   ├── llm/               # AI模型客户端
│   ├── schemas/           # 数据模型
│   ├── security/          # 安全相关
│   └── tools/             # 工具函数
├── db/                    # 数据库初始化脚本
├── static/                # 前端静态文件
├── docker-compose.yml     # Docker配置
├── requirements.txt        # Python依赖
└── README.md              # 项目文档
```

### 🌍 环境变量配置

#### 必需配置
```bash
# 云端AI服务 (API易)
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.apiyi.com/v1
OPENAI_MODEL=deepseek-r1
```

#### 可选配置
```bash
# 本地AI模型
GGUF_MODEL_PATH=/path/to/model.gguf

# 自定义端口
PORT=8000

# 日志级别
LOG_LEVEL=INFO
```

### 🗄️ 数据库配置

#### MySQL (医疗数据库)
- **端口**: 3306
- **用户名**: root
- **密码**: password
- **数据库**: hospital_db

#### PostgreSQL (仓储数据库)
- **端口**: 5432
- **用户名**: postgres
- **密码**: password
- **数据库**: warehouse_db

## 🚨 故障排除

### ❌ 常见问题及解决方案

#### 1. 依赖安装失败
```bash
# 问题: pip install 失败
# 解决方案:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir

# 如果llama-cpp-python安装失败:
pip install llama-cpp-python --no-cache-dir
# 或者使用预编译版本:
pip install llama-cpp-python --prefer-binary
```

#### 2. 数据库连接失败
```bash
# 检查Docker容器状态
docker ps

# 重启容器
docker compose down
docker compose up -d

# 查看容器日志
docker logs mysql_hospital
docker logs postgres_warehouse
```

#### 3. 本地模型加载失败
```bash
# 检查模型文件路径
ls -la /path/to/your/model.gguf

# 检查文件权限
chmod 644 /path/to/your/model.gguf

# 验证模型文件完整性
# 可以尝试重新下载模型文件
```

#### 4. 端口被占用
```bash
# 查看端口占用
lsof -i :8000  # macOS/Linux
netstat -an | findstr :8000  # Windows

# 杀死占用进程
kill -9 <PID>

# 或者使用其他端口
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### 5. 权限问题
```bash
# 检查文件权限
ls -la

# 修复权限
chmod -R 755 .
chmod 644 .env
```

### 📊 日志查看

#### 应用日志
```bash
# 查看实时日志
tail -f app.log

# 查看错误日志
grep ERROR app.log
```

#### Docker日志
```bash
# 查看MySQL日志
docker logs -f mysql_hospital

# 查看PostgreSQL日志
docker logs -f postgres_warehouse
```

## 📈 性能优化

### 🚀 系统优化建议

#### 本地模型优化
- 使用SSD存储模型文件
- 调整模型参数 (n_threads, n_ctx等)
- 使用量化模型减少内存占用

#### 数据库优化
- 配置适当的连接池大小
- 为常用查询添加索引
- 定期清理日志和临时数据

#### 应用优化
- 启用模型缓存
- 使用异步处理
- 配置静态文件缓存

### 🔍 性能监控

```bash
# 查看系统资源使用
htop  # macOS/Linux
# 任务管理器 # Windows

# 查看Docker资源使用
docker stats

# 查看应用性能
curl http://localhost:8000/api/health
```

## 🔮 扩展开发

### 🛠️ 添加新功能

#### 1. 添加新的AI模型
在 `app/llm/` 目录下创建新的客户端文件

#### 2. 添加新的数据库
在 `app/db/` 目录下添加新的数据库管理器

#### 3. 添加新的工具
在 `app/tools/` 目录下创建新的工具模块

### 🧪 测试

```bash
# 运行测试
python -m pytest

# 运行特定测试
python -m pytest test_rbac.py
```

## 📚 学习资源

### 🔗 相关链接
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [llama-cpp-python文档](https://github.com/abetlen/llama-cpp-python)
- [Docker官方文档](https://docs.docker.com/)

### 📖 推荐阅读
- FastAPI最佳实践
- 大语言模型部署指南
- Docker容器化部署
- 数据库设计原则

## 🤝 贡献指南

### 📝 如何贡献

1. **Fork项目**: 在GitHub上fork本项目
2. **创建分支**: 创建功能分支 `git checkout -b feature/AmazingFeature`
3. **提交更改**: 提交你的更改 `git commit -m 'Add some AmazingFeature'`
4. **推送分支**: 推送到分支 `git push origin feature/AmazingFeature`
5. **创建PR**: 打开Pull Request

### 🐛 报告问题

如果发现bug或有功能建议，请：
1. 检查是否已有相关issue
2. 创建新的issue，详细描述问题
3. 提供复现步骤和环境信息

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**Alan** - [GitHub](https://github.com/Alansws)

## 🙏 致谢

- 感谢所有开源项目的贡献者
- 感谢API易提供的AI服务支持
- 感谢社区用户的支持和反馈

## 📞 联系方式

- **项目主页**: https://github.com/Alansws/Alansws_mcp
- **问题反馈**: https://github.com/Alansws/Alansws_mcp/issues
- **邮箱**: alan@example.com

---

## 🎉 快速验证

完成部署后，可以通过以下步骤快速验证系统是否正常工作：

1. **访问Web界面**: http://localhost:8000
2. **测试数据库连接**: 点击"测试连接"按钮
3. **尝试简单问答**: 输入"你好"或点击快速示例
4. **检查API文档**: http://localhost:8000/docs

如果一切正常，恭喜你！🎊 MCP智能化问答应用已经成功部署并运行。

**遇到问题？** 请查看 [故障排除](#-故障排除) 部分，或者创建GitHub issue寻求帮助。
