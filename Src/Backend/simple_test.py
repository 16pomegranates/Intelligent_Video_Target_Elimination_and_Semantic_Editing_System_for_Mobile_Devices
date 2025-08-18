#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版ClipPersona Studio 功能测试脚本
专注于人格生成和自然语言处理功能测试
"""

import os
import sys
import json
import logging
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_imports():
    """测试基本模块导入"""
    print("=" * 60)
    print("测试基本模块导入")
    print("=" * 60)
    
    try:
        from clip_persona_studio import ClipPersonaStudio
        print("✓ ClipPersonaStudio 导入成功")
    except Exception as e:
        print(f"✗ ClipPersonaStudio 导入失败: {e}")
        return False
    
    try:
        from enhanced_nlp_parser import EnhancedNLPParser
        print("✓ EnhancedNLPParser 导入成功")
    except Exception as e:
        print(f"✗ EnhancedNLPParser 导入失败: {e}")
        return False
    
    try:
        from enhanced_video_comprehension import EnhancedVideoComprehension
        print("✓ EnhancedVideoComprehension 导入成功")
    except Exception as e:
        print(f"✗ EnhancedVideoComprehension 导入失败: {e}")
        return False
    
    return True

def test_nlp_parser():
    """测试自然语言处理功能"""
    print("\n" + "=" * 60)
    print("测试自然语言处理功能")
    print("=" * 60)
    
    try:
        from enhanced_nlp_parser import EnhancedNLPParser
        nlp_parser = EnhancedNLPParser()
        print("✓ NLP解析器初始化成功")
        
        # 测试简单指令
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
                
            except Exception as e:
                print(f"  ✗ 处理失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ NLP测试失败: {e}")
        return False

def test_persona_creation():
    """测试人格创建功能"""
    print("\n" + "=" * 60)
    print("测试人格创建功能")
    print("=" * 60)
    
    try:
        from clip_persona_studio import ClipPersonaStudio
        studio = ClipPersonaStudio()
        print("✓ ClipPersonaStudio 初始化成功")
        
        # 测试用户ID和人格名称
        user_id = "test_user_001"
        persona_name = "创意剪辑师"
        
        print(f"用户ID: {user_id}")
        print(f"人格名称: {persona_name}")
        
        # 创建新的人格
        try:
            persona = studio.create_persona(user_id, persona_name)
            print(f"✓ 成功创建人格: {persona.persona_name}")
            print(f"  创建时间: {persona.creation_date}")
            print(f"  风格摘要: {persona.get_style_summary()}")
            
            # 测试风格向量
            style_vector = persona.style_vector
            print(f"  语言节奏偏好: {style_vector.language_rhythm}")
            print(f"  镜头选择偏好: {style_vector.shot_selection}")
            
            return True
            
        except Exception as e:
            print(f"✗ 创建人格失败: {e}")
            return False
        
    except Exception as e:
        print(f"✗ 人格测试失败: {e}")
        return False

def test_complex_instructions():
    """测试复杂指令处理"""
    print("\n" + "=" * 60)
    print("测试复杂指令处理")
    print("=" * 60)
    
    try:
        from enhanced_nlp_parser import EnhancedNLPParser
        nlp_parser = EnhancedNLPParser()
        
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
                
                # 显示解析的操作
                for i, op in enumerate(parsed_result['operations']):
                    print(f"    操作{i+1}: {op['type']} - {op['description']}")
                
            except Exception as e:
                print(f"  ✗ 处理失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ 复杂指令测试失败: {e}")
        return False

def test_persona_style_adaptation():
    """测试人格风格适应"""
    print("\n" + "=" * 60)
    print("测试人格风格适应")
    print("=" * 60)
    
    try:
        from clip_persona_studio import ClipPersonaStudio
        from enhanced_nlp_parser import EnhancedNLPParser
        
        studio = ClipPersonaStudio()
        nlp_parser = EnhancedNLPParser()
        
        # 创建人格
        user_id = "test_user_002"
        persona_name = "专业剪辑师"
        persona = studio.create_persona(user_id, persona_name)
        
        print(f"✓ 创建人格: {persona.persona_name}")
        
        # 测试用户反馈处理
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
        
        try:
            studio.process_user_feedback(persona, feedback)
            print("✓ 用户反馈处理完成")
            print(f"  更新后的风格摘要: {persona.get_style_summary()}")
            
            # 测试基于人格的剪辑方案生成
            user_instruction = "制作一个快节奏的宣传视频"
            
            editing_plan = studio.generate_editing_plan(persona, user_instruction, None)
            print("✓ 剪辑方案生成完成")
            print(f"  方案置信度: {editing_plan['confidence_score']:.2f}")
            print(f"  操作数量: {len(editing_plan['operations'])}")
            print(f"  风格说明: {editing_plan['style_notes']}")
            
            for i, op in enumerate(editing_plan['operations']):
                print(f"    操作{i+1}: {op['type']} - {op['description']}")
            
            return True
            
        except Exception as e:
            print(f"✗ 风格适应失败: {e}")
            return False
        
    except Exception as e:
        print(f"✗ 人格风格测试失败: {e}")
        return False

def main():
    """主函数"""
    print("简化版ClipPersona Studio 测试程序")
    print("专注于人格生成和自然语言处理功能测试")
    
    # 测试基本导入
    if not test_basic_imports():
        print("\n基本模块导入失败，无法继续测试")
        return
    
    # 测试NLP功能
    test_nlp_parser()
    
    # 测试人格创建
    test_persona_creation()
    
    # 测试复杂指令
    test_complex_instructions()
    
    # 测试人格风格适应
    test_persona_style_adaptation()
    
    print("\n" + "=" * 60)
    print("简化版测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
