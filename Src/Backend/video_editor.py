import os
import gc
import uuid
import time
import psutil
import logging
import tempfile
import retrying
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, Protocol
from nlp_parser import OPERATIONS, EDITOR_TYPES, process_instruction, DialogueManager
from moviepy_editor import MoviePyVideoEditor, AbstractVideoEditor
from ffmpeg_editor import FFmpegVideoEditor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoEditorFactory:
    """视频编辑器工厂类，负责创建不同类型的视频编辑器实例"""
    
    @staticmethod
    def create_editor(editor_type: str, input_video: str) -> AbstractVideoEditor:
        """
        根据指定的编辑器类型创建相应的视频编辑器实例。
        
        Args:
            editor_type: 编辑器类型，必须是 EDITOR_TYPES 中定义的类型之一
            input_video: 输入视频文件路径
            
        Returns:
            AbstractVideoEditor: 视频编辑器实例
            
        Raises:
            ValueError: 当指定的编辑器类型不支持时抛出
        """
        if editor_type not in EDITOR_TYPES:
            raise ValueError(f"不支持的编辑器类型: {editor_type}")
            
        if editor_type == 'moviepy':
            return MoviePyVideoEditor(input_video)
        elif editor_type == 'ffmpeg':
            return FFmpegVideoEditor(input_video)
        elif editor_type == 'opencv':
            raise NotImplementedError("OpenCV 编辑器尚未实现")
        else:
            raise ValueError(f"未知的编辑器类型: {editor_type}")

class DialogueVideoEditor:
    """对话式视频编辑器，整合自然语言处理和视频编辑功能"""
    
    def __init__(self, input_video: str, editor_type: str = 'moviepy'):
        """
        初始化对话式视频编辑器。
        
        Args:
            input_video: 输入视频文件路径
            editor_type: 编辑器类型，默认使用 MoviePy
        """
        self.editor = VideoEditorFactory.create_editor(editor_type, input_video)
        self.dialogue_manager = DialogueManager()
        self.dialogue_manager.set_current_video(input_video)
        self.history = []
        
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户的自然语言命令。

        Args:
            user_input: 用户输入的自然语言命令
            
        Returns:
            Dict: {
                "response": 处理结果的自然语言响应,
                "success": 是否成功执行,
                "action": 执行的操作指令
            }
        """
        try:
            # 处理用户输入
            result = self.dialogue_manager.process_user_input(user_input)
            print("result: ",result)
            if not result["success"]:
                return {
                    "response": result["response"],
                    "success": False,
                    "action": None
                }
                
            # 如果是撤销操作
            if result["action"] == "undo":
                return {
                    "response": result["response"],
                    "success": True,
                    "action": "undo"
                }
                    
            # 如果是帮助信息
            if not result["action"]:
                return {
                    "response": result["response"],
                    "success": True,
                    "action": None
                }
                
            # 执行编辑操作
            action_str = result["action"]
            action_parts = action_str.strip().split()
            editor_type = 'moviepy'  # 默认使用 MoviePy
            
            # 解析编辑器类型
            for part in action_parts:
                if part.startswith('editor='):
                    editor_type = part.split('=')[1]
                    break
                    
            # 检查操作是否被指定编辑器支持
            action = action_parts[1]
            if action in OPERATIONS and editor_type not in OPERATIONS[action]['supported_editors']:
                return {
                    "response": f"抱歉，{editor_type} 编辑器不支持 {action} 操作",
                    "success": False,
                    "action": action_str
                }
                
            # 检查编辑器状态
            if not self.is_editor_ready():
                return {
                    "response": "视频编辑器未初始化或已被关闭，请重新加载视频",
                    "success": False,
                    "action": action_str
                }
                
            # 执行操作并检查结果
            try:
                success = self.editor.execute_action(action_str, OPERATIONS)
                if success:
                    return {
                        "response": result["response"],
                        "success": True,
                        "action": action_str
                    }
                else:
                    return {
                        "response": "操作执行失败，请检查参数是否正确",
                        "success": False,
                        "action": action_str
                    }
            except Exception as e:
                logger.error(f"执行操作时发生异常: {e}")
                return {
                    "response": f"操作执行失败: {str(e)}",
                    "success": False,
                    "action": action_str
                }
        except Exception as e:
            logger.error(f"处理命令失败: {e}")
            return {
                "response": f"处理命令时出错: {str(e)}",
                "success": False,
                "action": None
            }

    def save_final(self, output_path: str):
        """
        保存最终的视频文件。

        Args:
            output_path: 输出文件路径
        """
        self.editor.output_path = output_path
        self.editor.save()
        # 注意：这里不关闭编辑器，让调用方决定何时关闭
        
    def is_operation_successful(self, result: Dict[str, Any]) -> bool:
        """检查操作是否成功"""
        return result.get('success', False)
        
    def is_editor_ready(self) -> bool:
        """检查编辑器是否准备就绪"""
        # 对 MoviePy：要求 video_clip 存在且非 None；对 FFmpeg：无持有 clip 的概念，视为就绪
        if hasattr(self.editor, 'video_clip'):
            return self.editor.video_clip is not None
        return True
        
    def close(self):
        """关闭编辑器并清理资源"""
        self.editor.close()
        self.dialogue_manager.clear_history()

def process_video_edit(user_input: str, input_video: str, editor_type: str = 'moviepy') -> Tuple[str, Optional[AbstractVideoEditor]]:
    """
    处理单次视频编辑指令，返回确认消息和编辑器实例。
    
    Args:
        user_input: 用户输入的自然语言指令
        input_video: 输入视频文件路径
        editor_type: 编辑器类型，默认使用 MoviePy
        
    Returns:
        Tuple[str, Optional[AbstractVideoEditor]]: (确认消息, 编辑器实例)
    """
    try:
        editor = VideoEditorFactory.create_editor(editor_type, input_video)
    except FileNotFoundError as e:
        logger.error(str(e))
        return str(e), None
    except Exception as e:
        logger.error(f"创建编辑器失败: {e}")
        return f"创建编辑器失败: {str(e)}", None
        
    content, confirmation, _ = process_instruction(user_input)
    if content:
        try:
            success = editor.execute_action(content, OPERATIONS)
            if not success:
                return "操作执行失败，请检查参数是否正确", None
        except Exception as e:
            logger.error(f"执行操作时发生异常: {e}")
            return f"操作执行失败: {str(e)}", None
        
    return confirmation, editor

if __name__ == "__main__":
    input_video = "D:\\test1\\video001.mp4"
    # 使用 ffmpeg 编辑器
    editor = DialogueVideoEditor(input_video, editor_type='ffmpeg')

    # 仅测试：添加字幕（底部居中，3s 出现，持续 5s）
    commands = [
        "在视频中添加字幕'测试字幕'，字体大小为48，持续时间为5秒，位置在底部中央，开始时间为3秒 editor=ffmpeg"
    ]

    for i, cmd in enumerate(commands):
        print(f"\n用户输入: {cmd}")
        result = editor.process_command(cmd)
        print(f"系统响应: {result['response']}")
        print(f"执行成功: {result['success']}")

        if result['success']:
            if i == len(commands) - 1:
                editor.save_final("Output\\ffmpeg_add_text_from_dialogue.mp4")
                print("视频已保存")
        else:
            print("操作失败，未保存视频")
            break

    editor.close()