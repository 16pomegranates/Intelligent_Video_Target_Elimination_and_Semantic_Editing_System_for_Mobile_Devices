#!/usr/bin/env python3
"""
测试 MoviePyVideoEditor 的音频添加和视频合并功能
"""

import os
from moviepy_editor import MoviePyVideoEditor


def test_add_background_music():
    """测试添加背景音乐功能"""
    print("=== 测试添加背景音乐 ===")
    
    input_video = r"D:\test1\video025.mp4"
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试1：在视频的5-15秒时间段添加音频的0-10秒
    editor = MoviePyVideoEditor(input_video)
    try:
        editor.add_background_music(
            audio_file=r"D:\test1\audio001.mp3",  # 请替换为实际的音频文件路径
            video_start_time=5.0,
            video_end_time=15.0,
            audio_start_time=0.0,
            audio_end_time=10.0,
            mix=True
        )
        editor.output_path = os.path.join(output_dir, "test_bg_music_mixed.mp4")
        editor.save()
        print("✓ 背景音乐混合测试完成")
    except Exception as e:
        print(f"✗ 背景音乐混合测试失败: {e}")
    finally:
        editor.close()
    
    # 测试2：替换原音频
    editor2 = MoviePyVideoEditor(input_video)
    try:
        editor2.add_background_music(
            audio_file=r"D:\test1\audio001.mp3",  # 请替换为实际的音频文件路径
            video_start_time=0.0,
            video_end_time=None,  # 到视频结尾
            audio_start_time=0.0,
            audio_end_time=None,  # 到音频结尾
            mix=False
        )
        editor2.output_path = os.path.join(output_dir, "test_bg_music_replaced.mp4")
        editor2.save()
        print("✓ 背景音乐替换测试完成")
    except Exception as e:
        print(f"✗ 背景音乐替换测试失败: {e}")
    finally:
        editor2.close()


def test_add_audio_segment():
    """测试在特定时间段添加音频片段"""
    print("\n=== 测试添加音频片段 ===")
    
    input_video = r"D:\test1\video025.mp4"
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试：在视频的10-20秒时间段添加音频片段
    editor = MoviePyVideoEditor(input_video)
    try:
        editor.add_audio_segment(
            audio_file=r"D:\test1\audio001.mp3",  # 请替换为实际的音频文件路径
            video_start_time=10.0,
            video_end_time=20.0,
            audio_start_time=5.0,  # 从音频的第5秒开始
            audio_end_time=15.0,   # 到音频的第15秒结束
            volume=1.5,            # 音量放大1.5倍
            mix=True               # 与原音频混合
        )
        editor.output_path = os.path.join(output_dir, "test_audio_segment.mp4")
        editor.save()
        print("✓ 音频片段添加测试完成")
    except Exception as e:
        print(f"✗ 音频片段添加测试失败: {e}")
    finally:
        editor.close()


def test_concatenate_videos():
    """测试视频合并功能"""
    print("\n=== 测试视频合并 ===")
    
    input_video = r"D:\test1\video025.mp4"
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试1：简单合并
    editor = MoviePyVideoEditor(input_video)
    try:
        editor.concatenate(
            second_video=r"D:\test1\video026.mp4",  # 请替换为实际的第二个视频文件路径
            transition="none"
        )
        editor.output_path = os.path.join(output_dir, "test_concatenate_simple.mp4")
        editor.save()
        print("✓ 简单视频合并测试完成")
    except Exception as e:
        print(f"✗ 简单视频合并测试失败: {e}")
    finally:
        editor.close()
    
    # 测试2：带转场效果的合并
    editor2 = MoviePyVideoEditor(input_video)
    try:
        editor2.concatenate(
            second_video=r"D:\test1\video026.mp4",  # 请替换为实际的第二个视频文件路径
            transition="fade",
            transition_duration=2.0
        )
        editor2.output_path = os.path.join(output_dir, "test_concatenate_fade.mp4")
        editor2.save()
        print("✓ 带转场效果视频合并测试完成")
    except Exception as e:
        print(f"✗ 带转场效果视频合并测试失败: {e}")
    finally:
        editor2.close()


def test_concatenate_multiple():
    """测试多视频合并功能"""
    print("\n=== 测试多视频合并 ===")
    
    input_video = r"D:\test1\video025.mp4"
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试：合并多个视频文件
    editor = MoviePyVideoEditor(input_video)
    try:
        video_files = [
            r"D:\test1\video026.mp4",  # 请替换为实际的视频文件路径
            r"D:\test1\video027.mp4"   # 请替换为实际的视频文件路径
        ]
        editor.concatenate_multiple(
            video_files=video_files,
            transition="crossfade",
            transition_duration=1.5
        )
        editor.output_path = os.path.join(output_dir, "test_concatenate_multiple.mp4")
        editor.save()
        print("✓ 多视频合并测试完成")
    except Exception as e:
        print(f"✗ 多视频合并测试失败: {e}")
    finally:
        editor.close()


if __name__ == "__main__":
    print("开始测试 MoviePyVideoEditor 的音频和视频合并功能...")
    
    # 注意：请根据你的实际文件路径修改以下测试
    # 确保音频和视频文件存在
    
    try:
        test_add_background_music()
        test_add_audio_segment()
        test_concatenate_videos()
        test_concatenate_multiple()
        print("\n🎉 所有测试完成！")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        print("请检查文件路径是否正确，以及是否已安装所需的依赖包。")
