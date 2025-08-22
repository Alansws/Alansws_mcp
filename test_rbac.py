#!/usr/bin/env python3
"""
RBAC功能测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_rbac():
    """测试RBAC功能"""
    print("🚀 开始测试RBAC功能...\n")
    
    # 测试仓库操作员权限
    print("📦 测试仓库操作员(S1002)权限:")
    
    # 1. 切换到仓储数据库
    try:
        db_response = requests.post(f"{BASE_URL}/api/switch_db", 
                                  json={"database": "warehouse"}, timeout=10)
        if db_response.status_code != 200:
            print("❌ 数据库切换失败")
            return
        print("✅ 已切换到仓储数据库")
    except Exception as e:
        print(f"❌ 数据库切换异常: {e}")
        return
    
    # 2. 测试仓库操作员查询库存(应该成功)
    print("\n🔍 测试1: 查询库存信息(应该成功)")
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "user_id": "S1002",
            "role": "Operator", 
            "question": "查询所有商品的库存数量",
            "model_type": "auto"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('meta', {}).get('permission', True):
                print("✅ 权限检查通过")
                print(f"   生成的SQL: {result.get('meta', {}).get('sql', '')[:100]}...")
            else:
                print("❌ 权限检查失败")
                print(f"   错误信息: {result.get('answer', '')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 3. 测试仓库操作员查询价格(应该失败)
    print("\n🔍 测试2: 查询商品价格(应该失败)")
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "user_id": "S1002",
            "role": "Operator",
            "question": "查询所有商品的价格信息", 
            "model_type": "auto"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('meta', {}).get('permission', True):
                print("✅ 权限检查正确拒绝")
                print(f"   拒绝原因: {result.get('answer', '')}")
            else:
                print("❌ 权限检查应该拒绝但通过了")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 4. 测试仓库经理权限
    print("\n🔍 测试3: 仓库经理查询价格(应该成功)")
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "user_id": "S1001",
            "role": "Manager",
            "question": "查询所有商品的价格信息",
            "model_type": "auto"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('meta', {}).get('permission', True):
                print("✅ 权限检查通过")
                print(f"   生成的SQL: {result.get('meta', {}).get('sql', '')[:100]}...")
            else:
                print("❌ 权限检查失败")
                print(f"   错误信息: {result.get('answer', '')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("🔐 RBAC功能测试工具")
    print("=" * 50)
    
    # 检查服务状态
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
            test_rbac()
        else:
            print("❌ 服务响应异常")
    except:
        print("❌ 无法连接到服务，请确保服务运行在 http://localhost:8000")
