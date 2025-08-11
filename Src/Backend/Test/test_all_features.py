#!/usr/bin/env python3
"""
全面测试 MoviePy 视频编辑器所有功能
测试 moviepy_editor.py 中除了消除以外的所有功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from video_editor import DialogueVideoEditor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_features():
    """测试所有视频编辑功能"""
    input_video = "D:\\test1\\video001.mp4"  # 请根据实际情况修改路径
    
    # 检查输入文件是否存在
    if not os.path.exists(input_video):
        logger.error(f"输入视频文件不存在: {input_video}")
        logger.info("请修改 input_video 路径为实际的视频文件路径")
        return False
    
    try:
        editor = DialogueVideoEditor(input_video)
        logger.info("✅ 视频编辑器初始化成功")
        
        # 定义所有测试命令
        test_commands = [
            {
                "name": "裁剪视频（时间裁剪）",
                "command": "将视频的前 2 秒剪掉",
                "description": "测试 trim 功能"
            },
            {
                "name": "调整音量",
                "command": "将视频音量调整为原来的三倍",
                "description": "测试 adjust_volume 功能"
            },
            {
                "name": "旋转视频",
                "command": "将视频旋转三十度",
                "description": "测试 rotate 功能"
            },
            {
                "name": "调整播放速度",
                "command": "将视频播放速度调整为原来的两倍",
                "description": "测试 adjust_speed 功能"
            },
            {
                "name": "调整亮度",
                "command": "将视频亮度调整为原来的1.5倍",
                "description": "测试 adjust_brightness 功能"
            },
                         {
                 "name": "调整对比度",
                 "command": "对比度增强到1.2倍",
                 "description": "测试 adjust_contrast 功能"
             },
            {
                "name": "添加转场效果",
                "command": "在视频开头添加淡入效果，持续时间为2秒",
                "description": "测试 add_transition 功能"
            },
                         {
                 "name": "裁剪画面（空间裁剪）",
                 "command": "将视频画面裁剪为左上角四分之一区域",
                 "description": "测试 crop 功能"
             },

        ]
        
        # 可选测试（需要额外文件）
        optional_commands = [
            {
                "name": "添加背景音乐",
                "command": "添加背景音乐 background_music.mp3，混合原音频",
                "description": "测试 add_background_music 功能",
                "requires_file": "background_music.mp3"
            },
            {
                "name": "合并视频",
                "command": "将视频与 second_video.mp4 合并",
                "description": "测试 concatenate 功能",
                "requires_file": "second_video.mp4"
            }
        ]
        
        # 检查可选测试的文件是否存在
        for opt_cmd in optional_commands:
            if "requires_file" in opt_cmd:
                file_path = opt_cmd["requires_file"]
                if os.path.exists(file_path):
                    test_commands.append(opt_cmd)
                    logger.info(f"✅ 找到文件 {file_path}，将测试 {opt_cmd['name']}")
                else:
                    logger.warning(f"⚠️ 文件 {file_path} 不存在，跳过 {opt_cmd['name']} 测试")
        
        success_count = 0
        total_count = len(test_commands)
        
        logger.info(f"🚀 开始测试 {total_count} 个功能")
        
        for i, test in enumerate(test_commands):
            logger.info(f"\n📋 测试 {i+1}/{total_count}: {test['name']}")
            logger.info(f"📝 描述: {test['description']}")
            logger.info(f"🔧 命令: {test['command']}")
            
            # 检查编辑器状态
            if not editor.is_editor_ready():
                logger.error("❌ 编辑器未准备就绪，停止测试")
                break
                
            result = editor.process_command(test['command'])
            logger.info(f"📤 系统响应: {result['response']}")
            logger.info(f"✅ 执行成功: {result['success']}")
            
            if result['success']:
                success_count += 1
                if i == len(test_commands) - 1:
                    # 最后一个操作，保存视频
                    output_path = "Output\\test_all_features_output.mp4"
                    editor.save_final(output_path)
                    logger.info(f"💾 视频已保存至: {output_path}")
                else:
                    logger.info("⏭️ 操作成功，继续下一个操作")
            else:
                logger.error("❌ 操作失败，停止测试")
                break
        
        # 关闭编辑器
        editor.close()
        logger.info("🔒 编辑器已关闭")
        
        logger.info(f"\n📊 测试结果: {success_count}/{total_count} 个功能测试成功")
        
        if success_count == total_count:
            logger.info("🎉 所有功能测试通过！")
            return True
        else:
            logger.warning(f"⚠️ 部分功能测试失败，成功率: {success_count/total_count*100:.1f}%")
            return False
        
    except Exception as e:
        logger.error(f"❌ 测试过程中发生异常: {e}")
        return False

def test_individual_features():
    """单独测试每个功能"""
    logger.info("\n🔍 单独功能测试模式")
    
    # 这里可以添加单独测试特定功能的代码
    # 例如：只测试音量调整、只测试旋转等
    
    pass

if __name__ == "__main__":
    logger.info("🚀 开始全面测试 MoviePy 视频编辑器功能")
    
    # 运行全面测试
    success = test_all_features()
    
    if success:
        logger.info("🎉 所有测试通过！MoviePy 编辑器功能完整！")
    else:
        logger.error("💥 部分测试失败，需要检查相关功能")
    
    # 可以在这里添加单独功能测试
    # test_individual_features()
