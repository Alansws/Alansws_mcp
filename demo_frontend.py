#!/usr/bin/env python3
"""
MCP 智能化问答应用 - 前端界面演示脚本
演示前端界面的主要功能和特性
"""

import time
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """打印步骤"""
    print(f"\n{step}. {description}")

def test_api_endpoint(endpoint, method="GET", data=None):
    """测试 API 端点"""
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{API_BASE}{endpoint}", json=data)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"连接错误: {str(e)}"

def demo_frontend_features():
    """演示前端界面功能"""
    print_header("🎨 前端界面功能演示")
    
    print_step(1, "访问 Web 界面")
    print(f"   打开浏览器访问: {BASE_URL}")
    print("   你应该能看到一个美观的现代化界面，包含：")
    print("   - 渐变背景和毛玻璃效果")
    print("   - 左侧控制面板（数据库切换、角色选择、连接状态）")
    print("   - 右侧聊天区域（欢迎消息、输入框）")
    print("   - 响应式设计，支持各种屏幕尺寸")
    
    print_step(2, "测试数据库连接状态")
    success, result = test_api_endpoint("/test_db_connections")
    if success:
        print("   ✅ 数据库连接测试成功")
        print(f"   医疗数据库: {result['hospital']['status']}")
        print(f"   仓储数据库: {result['warehouse']['status']}")
    else:
        print(f"   ❌ 数据库连接测试失败: {result}")
    
    print_step(3, "测试数据库切换功能")
    print("   在左侧面板中：")
    print("   1. 选择 '🏥 医疗数据库'")
    print("   2. 选择 '📦 仓储数据库'")
    print("   3. 观察角色选项的变化")
    print("   4. 查看聊天区域的切换提示")
    
    print_step(4, "测试角色选择")
    print("   医疗数据库角色选项：")
    print("   - 👨‍⚕️ 医生 (D101) - 👩‍⚕️ 医生 (D102)")
    print("   - 👨‍⚕️ 医生 (D103) - 👩‍⚕️ 医生 (D104)")
    print("   - 👤 普通用户")
    print("\n   仓储数据库角色选项：")
    print("   - 👨‍💼 仓库经理 (S1001)")
    print("   - 👷 仓库操作员 (S1002-S1004)")
    print("   - 👤 普通用户")
    
    print_step(5, "测试快速示例")
    print("   点击左侧的快速示例：")
    print("   - 🔍 查询心内科医生")
    print("   - 💻 查询笔记本库存")
    print("   - 🌤️ 查询北京天气")
    print("   - 🧠 人工智能介绍")
    print("   这些示例会自动填充到输入框中")
    
    print_step(6, "测试智能问答")
    print("   在右侧聊天区域：")
    print("   1. 输入问题：'查询所有心内科的医生信息'")
    print("   2. 点击发送按钮或按 Enter")
    print("   3. 观察系统的智能回答")
    print("   4. 查看元数据信息（SQL、角色、权限等）")
    
    print_step(7, "测试权限控制")
    print("   切换到仓储数据库，选择操作员角色：")
    print("   1. 提问：'查询笔记本电脑的库存和价格'")
    print("   2. 系统会拒绝访问价格信息")
    print("   3. 提问：'查询笔记本电脑的库存数量'")
    print("   4. 系统会正常返回库存信息")

def demo_responsive_design():
    """演示响应式设计"""
    print_header("📱 响应式设计演示")
    
    print("前端界面采用完全响应式设计：")
    print("\n桌面端 (>1024px):")
    print("   - 左右分栏布局")
    print("   - 侧边栏宽度: 320px")
    print("   - 聊天区域高度: 600px")
    
    print("\n平板端 (768px-1024px):")
    print("   - 上下分栏布局")
    print("   - 侧边栏宽度: 100%")
    print("   - 聊天区域高度: 500px")
    
    print("\n手机端 (<768px):")
    print("   - 单列布局")
    print("   - 字体和间距自适应")
    print("   - 触摸友好的交互元素")
    
    print("\n要测试响应式设计：")
    print("1. 在浏览器中调整窗口大小")
    print("2. 使用开发者工具的设备模拟器")
    print("3. 在不同设备上访问应用")

def demo_ui_features():
    """演示 UI 特性"""
    print_header("✨ UI 特性演示")
    
    print("现代化设计元素：")
    print("\n🎨 视觉效果:")
    print("   - 渐变背景 (蓝紫色渐变)")
    print("   - 毛玻璃效果 (backdrop-filter)")
    print("   - 圆角设计 (border-radius: 20px)")
    print("   - 阴影效果 (box-shadow)")
    
    print("\n🎭 动画效果:")
    print("   - 消息淡入动画 (fadeInUp)")
    print("   - 按钮悬停效果 (transform: translateY)")
    print("   - 加载指示器 (spinner)")
    print("   - 通知滑入滑出动画")
    
    print("\n🔧 交互特性:")
    print("   - 实时状态更新")
    print("   - 智能表单验证")
    print("   - 键盘快捷键支持")
    print("   - 自动滚动到最新消息")

def main():
    """主函数"""
    print_header("🚀 MCP 智能化问答应用 - 前端界面演示")
    
    print("本演示将展示前端界面的主要功能和特性")
    print("请确保应用正在运行 (http://localhost:8000)")
    
    # 检查应用状态
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("\n✅ 应用正在运行")
        else:
            print(f"\n⚠️ 应用响应异常: HTTP {response.status_code}")
    except:
        print("\n❌ 无法连接到应用，请确保应用正在运行")
        print("启动命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # 演示功能
    demo_frontend_features()
    demo_responsive_design()
    demo_ui_features()
    
    print_header("🎉 演示完成")
    print("现在你可以：")
    print("1. 打开浏览器访问 http://localhost:8000")
    print("2. 体验所有功能")
    print("3. 测试不同设备和屏幕尺寸")
    print("4. 享受现代化的用户界面！")

if __name__ == "__main__":
    main()
