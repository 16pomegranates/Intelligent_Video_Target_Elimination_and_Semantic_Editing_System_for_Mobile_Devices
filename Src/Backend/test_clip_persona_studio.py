#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClipPersona Studio 功能测试脚本
演示人格生成、视频分析、自然语言处理等核心功能
"""

import os
import sys
import json
import logging
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clip_persona_studio import ClipPersonaStudio
from enhanced_nlp_parser import EnhancedNLPParser
from enhanced_video_comprehension import EnhancedVideoComprehension

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_clip_persona_studio():
    """测试ClipPersona Studio的完整功能"""
    print("=" * 60)
    print("ClipPersona Studio 功能测试")
    print("=" * 60)
    
    # 初始化系统
    print("\n1. 初始化ClipPersona Studio系统...")
    studio = ClipPersonaStudio()
    nlp_parser = EnhancedNLPParser()
    video_comprehension = EnhancedVideoComprehension()
    
    # 测试用户ID和人格名称
    user_id = "test_user_001"
    persona_name = "创意剪辑师"
    
    print(f"用户ID: {user_id}")
    print(f"人格名称: {persona_name}")
    
    # 2. 创建新的人格
    print("\n2. 创建新的剪辑人格...")
    try:
        persona = studio.create_persona(user_id, persona_name)
        persona.save_persona()
        print(f"✓ 成功创建人格: {persona.persona_name}")
        print(f"  创建时间: {persona.creation_date}")
        print(f"  风格摘要: {persona.get_style_summary()}")
    except Exception as e:
        print(f"✗ 创建人格失败: {e}")
        return
    
    # 3. 测试视频分析（如果有测试视频）
    print("\n3. 测试视频分析功能...")
    test_video_path = "uploads/001.mp4"  # 假设存在这个测试视频
    
    if os.path.exists(test_video_path):
        try:
            # 分析视频偏好
            analysis_result = studio.analyze_video_preferences(persona, test_video_path)
            print("✓ 视频分析完成")
            print(f"  分析结果: {json.dumps(analysis_result, ensure_ascii=False, indent=2)}")
            
            # 综合视频分析
            comprehensive_analysis = video_comprehension.comprehensive_analysis(test_video_path, 'basic')
            print("✓ 综合视频分析完成")
            print(f"  视频类型: {comprehensive_analysis['summary']['video_type']}")
            print(f"  主导风格: {comprehensive_analysis['summary']['dominant_style']}")
            print(f"  剪辑建议: {comprehensive_analysis['summary']['editing_recommendations']}")
            
        except Exception as e:
            print(f"✗ 视频分析失败: {e}")
    else:
        print("⚠ 测试视频不存在，跳过视频分析测试")
    
    # 4. 测试自然语言处理
    print("\n4. 测试自然语言处理功能...")
    test_instructions = [
        "剪掉视频前10秒",
        "加速2倍播放",
        "添加淡入淡出转场效果",
        "在视频中添加文字：欢迎观看",
        "调整亮度到80%",
        "添加背景音乐"
    ]
    
    for instruction in test_instructions:
        try:
            print(f"\n测试指令: {instruction}")
            
            # 解析指令
            parsed_result = nlp_parser.parse_instruction(instruction)
            print(f"  解析结果: {parsed_result['operations']}")
            print(f"  置信度: {parsed_result['confidence_score']:.2f}")
            
            # 验证指令
            validation = nlp_parser.validate_instruction(instruction)
            if validation['is_valid']:
                print("  ✓ 指令有效")
            else:
                print(f"  ✗ 指令无效: {validation['errors']}")
            
            # 生成剪辑方案
            editing_plan = nlp_parser.generate_editing_plan(parsed_result, persona.style_vector.__dict__)
            print(f"  生成方案: {len(editing_plan['operations'])} 个操作")
            
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
    
    # 5. 测试用户反馈处理
    print("\n5. 测试用户反馈处理...")
    try:
        feedback = {
            'style_preferences': {
                'language_rhythm': {
                    'fast_paced': 0.8,
                    'slow_paced': 0.2
                },
                'shot_selection': {
                    'close_up_frequency': 0.7,
                    'transition_smoothness': 0.9
                }
            },
            'tags': ['快节奏', '特写镜头', '平滑转场']
        }
        
        studio.process_user_feedback(persona, feedback)
        print("✓ 用户反馈处理完成")
        print(f"  更新后的风格摘要: {persona.get_style_summary()}")
        
    except Exception as e:
        print(f"✗ 反馈处理失败: {e}")
    
    # 6. 测试基于人格的剪辑方案生成
    print("\n6. 测试基于人格的剪辑方案生成...")
    try:
        user_instruction = "制作一个快节奏的宣传视频"
        video_path = test_video_path if os.path.exists(test_video_path) else None
        
        editing_plan = studio.generate_editing_plan(persona, user_instruction, video_path)
        print("✓ 剪辑方案生成完成")
        print(f"  方案置信度: {editing_plan['confidence_score']:.2f}")
        print(f"  操作数量: {len(editing_plan['operations'])}")
        print(f"  风格说明: {editing_plan['style_notes']}")
        
        for i, op in enumerate(editing_plan['operations']):
            print(f"    操作{i+1}: {op['type']} - {op['description']}")
        
    except Exception as e:
        print(f"✗ 方案生成失败: {e}")
    
    # 7. 测试人格保存和加载
    print("\n7. 测试人格保存和加载...")
    try:
        # 保存人格
        persona.save_persona()
        print("✓ 人格保存完成")
        
        # 重新加载人格
        loaded_persona = studio.get_persona(user_id, persona_name)
        if loaded_persona:
            print("✓ 人格加载成功")
            print(f"  人格名称: {loaded_persona.persona_name}")
            print(f"  偏好标签: {[tag['tag'] for tag in loaded_persona.preference_tags]}")
        else:
            print("✗ 人格加载失败")
            
    except Exception as e:
        print(f"✗ 保存/加载失败: {e}")
    
    # 8. 测试复杂指令处理
    print("\n8. 测试复杂指令处理...")
    complex_instructions = [
        "将视频剪成3段，每段添加不同的转场效果，最后加速1.5倍",
        "在视频开头添加淡入效果，中间添加文字标题，结尾添加背景音乐",
        "制作一个30秒的短视频，包含快节奏剪辑和动态特效"
    ]
    
    for instruction in complex_instructions:
        try:
            print(f"\n复杂指令: {instruction}")
            
            # 解析指令
            parsed_result = nlp_parser.parse_instruction(instruction)
            print(f"  复杂度: {parsed_result['complexity']}")
            print(f"  操作数量: {len(parsed_result['operations'])}")
            print(f"  目标对象: {parsed_result['target_objects']}")
            
            # 生成方案
            editing_plan = nlp_parser.generate_editing_plan(parsed_result, persona.style_vector.__dict__)
            print(f"  生成方案操作数: {len(editing_plan['operations'])}")
            
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
    
    print("\n" + "=" * 60)
    print("ClipPersona Studio 功能测试完成")
    print("=" * 60)

def test_api_endpoints():
    """测试API端点（需要启动服务器）"""
    print("\n" + "=" * 60)
    print("API端点测试")
    print("=" * 60)
    
    import requests
    
    base_url = "http://localhost:5000"
    
    # 测试端点列表
    endpoints = [
        {
            'name': '创建人格',
            'url': '/api/persona/create',
            'method': 'POST',
            'data': {
                'user_id': 'test_user_002',
                'persona_name': '专业剪辑师'
            }
        },
        {
            'name': '解析指令',
            'url': '/api/nlp/parse-instruction',
            'method': 'POST',
            'data': {
                'instruction': '剪掉视频前5秒并加速2倍'
            }
        },
        {
            'name': '列出人格',
            'url': '/api/persona/list',
            'method': 'POST',
            'data': {
                'user_id': 'test_user_002'
            }
        }
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n测试端点: {endpoint['name']}")
            response = requests.post(
                f"{base_url}{endpoint['url']}",
                json=endpoint['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ 成功: {result.get('success', False)}")
                if 'error' in result:
                    print(f"    错误: {result['error']}")
            else:
                print(f"  ✗ 失败: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ⚠ 无法连接到服务器，请确保服务器正在运行")
            break
        except Exception as e:
            print(f"  ✗ 请求失败: {e}")

def main():
    """主函数"""
    print("ClipPersona Studio 测试程序")
    print("请选择测试类型:")
    print("1. 功能测试（本地测试）")
    print("2. API端点测试（需要服务器运行）")
    print("3. 全部测试")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == '1':
        test_clip_persona_studio()
    elif choice == '2':
        test_api_endpoints()
    elif choice == '3':
        test_clip_persona_studio()
        test_api_endpoints()
    else:
        print("无效选择，执行功能测试...")
        test_clip_persona_studio()

if __name__ == "__main__":
    main()
