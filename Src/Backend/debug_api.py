#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClipPersona Studio API 调试脚本
用于测试和调试后端API功能
"""

import requests
import json
import time
import sys

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """测试健康检查端点"""
    print("=" * 50)
    print("1. 测试健康检查端点")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health-check")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_create_persona():
    """测试创建人格"""
    print("\n" + "=" * 50)
    print("2. 测试创建人格")
    print("=" * 50)
    
    data = {
        "user_id": "test_user_001",
        "persona_name": "创意剪辑师"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/persona/create", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_parse_instruction():
    """测试自然语言指令解析"""
    print("\n" + "=" * 50)
    print("3. 测试自然语言指令解析")
    print("=" * 50)
    
    test_instructions = [
        "剪掉视频前10秒",
        "加速2倍播放",
        "添加淡入淡出转场效果",
        "在视频中添加文字：欢迎观看"
    ]
    
    for instruction in test_instructions:
        print(f"\n测试指令: {instruction}")
        data = {"instruction": instruction}
        
        try:
            response = requests.post(f"{BASE_URL}/api/nlp/parse-instruction", json=data)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"解析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                print(f"错误响应: {response.text}")
        except Exception as e:
            print(f"错误: {e}")

def test_generate_editing_plan():
    """测试生成剪辑方案"""
    print("\n" + "=" * 50)
    print("4. 测试生成剪辑方案")
    print("=" * 50)
    
    data = {
        "user_id": "test_user_001",
        "persona_name": "创意剪辑师",
        "instruction": "制作一个快节奏的宣传视频",
        "video_path": "uploads/sample_video.mp4"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/persona/generate-plan", json=data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"剪辑方案: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

def test_list_personas():
    """测试列出人格"""
    print("\n" + "=" * 50)
    print("5. 测试列出人格")
    print("=" * 50)
    
    data = {"user_id": "test_user_001"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/persona/list", json=data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"人格列表: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

def test_video_analysis():
    """测试视频分析（如果有测试视频）"""
    print("\n" + "=" * 50)
    print("6. 测试视频分析")
    print("=" * 50)
    
    # 这里需要实际的视频文件路径
    data = {
        "video_path": "uploads/test_video.mp4",
        "analysis_level": "basic"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/video/analyze", json=data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"视频分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

def test_user_feedback():
    """测试用户反馈处理"""
    print("\n" + "=" * 50)
    print("7. 测试用户反馈处理")
    print("=" * 50)
    
    data = {
        "user_id": "test_user_001",
        "persona_name": "创意剪辑师",
        "feedback": {
            "style_preferences": {
                "language_rhythm": {
                    "fast_paced": 0.8,
                    "slow_paced": 0.2
                }
            },
            "tags": ["快节奏", "动感"]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/persona/feedback", json=data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"反馈处理结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

def main():
    """主函数"""
    print("ClipPersona Studio API 调试工具")
    print("=" * 60)
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    # 测试健康检查
    if not test_health_check():
        print("❌ 服务器连接失败，请检查服务器是否正在运行")
        return
    
    print("✅ 服务器连接成功！")
    
    # 运行所有测试
    test_create_persona()
    test_parse_instruction()
    test_generate_editing_plan()
    test_list_personas()
    test_video_analysis()
    test_user_feedback()
    
    print("\n" + "=" * 60)
    print("调试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
