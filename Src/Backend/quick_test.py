#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速API测试脚本
"""

import requests
import json

def quick_test():
    """快速测试API功能"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 测试ClipPersona Studio API...")
    print("=" * 50)
    
    # 1. 测试健康检查
    try:
        response = requests.get(f"{base_url}/health-check")
        print(f"✅ 健康检查: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 2. 测试创建人格
    try:
        data = {"user_id": "test_user", "persona_name": "测试剪辑师"}
        response = requests.post(f"{base_url}/api/persona/create", json=data)
        print(f"✅ 创建人格: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   结果: {result.get('message', '成功')}")
    except Exception as e:
        print(f"❌ 创建人格失败: {e}")
    
    # 3. 测试NLP解析
    try:
        data = {"instruction": "剪掉视频前10秒"}
        response = requests.post(f"{base_url}/api/nlp/parse-instruction", json=data)
        print(f"✅ NLP解析: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            operations = result.get('operations', [])
            print(f"   解析到 {len(operations)} 个操作")
    except Exception as e:
        print(f"❌ NLP解析失败: {e}")
    
    # 4. 测试列出人格
    try:
        data = {"user_id": "test_user"}
        response = requests.post(f"{base_url}/api/persona/list", json=data)
        print(f"✅ 列出人格: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            personas = result.get('personas', [])
            print(f"   找到 {len(personas)} 个人格")
    except Exception as e:
        print(f"❌ 列出人格失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    quick_test()
