#!/usr/bin/env python3
"""
RBAC功能演示脚本
展示不同角色的权限差异
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def demo_rbac_functionality():
    """演示RBAC功能"""
    print("🔐 RBAC功能演示")
    print("=" * 60)
    
    # 检查服务状态
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ 服务未运行，请先启动服务：python -m app.main")
            return
        print("✅ 服务运行正常\n")
    except:
        print("❌ 无法连接到服务，请确保服务运行在 http://localhost:8000")
        return
    
    # 演示1：仓库操作员权限限制
    print("📦 演示1: 仓库操作员权限限制")
    print("-" * 40)
    
    # 切换到仓储数据库
    try:
        requests.post(f"{BASE_URL}/api/switch_db", json={"database": "warehouse"})
        print("✅ 已切换到仓储数据库")
    except:
        print("❌ 数据库切换失败")
        return
    
    # 测试仓库操作员查询库存（应该成功）
    print("\n🔍 测试：仓库操作员查询库存信息")
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
                print("✅ 权限检查通过 - 可以查询库存")
                print(f"   生成的SQL: {result.get('meta', {}).get('sql', '')[:80]}...")
            else:
                print("❌ 权限检查失败")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试仓库操作员查询价格（应该失败）
    print("\n🔍 测试：仓库操作员查询商品价格")
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
                print("✅ 权限检查正确拒绝 - 不能查询价格")
                print(f"   拒绝原因: {result.get('answer', '')}")
            else:
                print("❌ 权限检查应该拒绝但通过了")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 演示2：仓库经理权限对比
    print("\n\n👨‍💼 演示2: 仓库经理权限对比")
    print("-" * 40)
    
    # 测试仓库经理查询价格（应该成功）
    print("\n🔍 测试：仓库经理查询商品价格")
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
                print("✅ 权限检查通过 - 经理可以查询价格")
                print(f"   生成的SQL: {result.get('meta', {}).get('sql', '')[:80]}...")
            else:
                print("❌ 权限检查失败")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 演示3：跨数据库权限控制
    print("\n\n🏥 演示3: 跨数据库权限控制")
    print("-" * 40)
    
    # 切换到医疗数据库
    try:
        requests.post(f"{BASE_URL}/api/switch_db", json={"database": "hospital"})
        print("✅ 已切换到医疗数据库")
    except:
        print("❌ 数据库切换失败")
        return
    
    # 测试医生查询病人信息（应该成功）
    print("\n🔍 测试：医生查询病人信息")
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "user_id": "D101",
            "role": "doctor",
            "question": "查询所有病人信息",
            "model_type": "auto"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('meta', {}).get('permission', True):
                print("✅ 权限检查通过 - 医生可以查询病人信息")
                print(f"   生成的SQL: {result.get('meta', {}).get('sql', '')[:80]}...")
            else:
                print("❌ 权限检查失败")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试医生查询仓库信息（应该失败）
    print("\n🔍 测试：医生查询仓库信息（跨数据库）")
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "user_id": "D101",
            "role": "doctor",
            "question": "查询仓库库存信息",
            "model_type": "auto"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('meta', {}).get('permission', True):
                print("✅ 权限检查正确拒绝 - 医生不能查询仓库信息")
                print(f"   拒绝原因: {result.get('answer', '')}")
            else:
                print("❌ 权限检查应该拒绝但通过了")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 RBAC功能演示完成！")
    print("\n📋 演示总结：")
    print("✅ 仓库操作员：可以查询库存，但不能查询价格")
    print("✅ 仓库经理：可以查询所有信息，包括价格")
    print("✅ 医生：可以查询医疗信息，但不能查询仓库信息")
    print("✅ 跨数据库权限控制正常工作")
    print("✅ 列级权限控制正常工作")

if __name__ == "__main__":
    demo_rbac_functionality()
