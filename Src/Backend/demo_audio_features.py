#!/usr/bin/env python3
"""
演示 MoviePyVideoEditor 的音频添加和视频合并功能
"""

import os
from moviepy_editor import MoviePyVideoEditor


def demo_audio_features():
    """演示音频相关功能"""
    print("🎵 演示 MoviePyVideoEditor 音频功能")
    
    # 请根据你的实际文件路径修改
    input_video = r"D:\test1\video025.mp4"
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"输入视频: {input_video}")
    print(f"输出目录: {output_dir}")
    
    # 1. 演示精确时间控制的背景音乐
    print("\n1️⃣ 演示：在视频5-15秒时间段添加音频的0-10秒")
    editor1 = MoviePyVideoEditor(input_video)
    try:
        # 注意：请替换为实际的音频文件路径
        audio_file = r"Audio/bgm.wav"
        if os.path.exists(audio_file):
            editor1.add_background_music(
                audio_file=audio_file,
                video_start_time=5.0,
                video_end_time=15.0,
                audio_start_time=0.0,
                audio_end_time=10.0,
                mix=True
            )
            output_path = os.path.join(output_dir, "demo_bg_music_precise.mp4")
            editor1.output_path = output_path
            editor1.save()
            print(f"✅ 已生成: {output_path}")
        else:
            print(f"⚠️  音频文件不存在: {audio_file}")
    except Exception as e:
        print(f"❌ 背景音乐演示失败: {e}")
    finally:
        editor1.close()
    
    # 2. 演示音频片段插入
    print("\n2️⃣ 演示：在视频10-20秒时间段插入音效片段")
    editor2 = MoviePyVideoEditor(input_video)
    try:
        if os.path.exists(audio_file):
            editor2.add_audio_segment(
                audio_file=audio_file,
                video_start_time=10.0,
                video_end_time=20.0,
                audio_start_time=5.0,  # 从音频第5秒开始
                audio_end_time=15.0,   # 到音频第15秒结束
                volume=1.5,            # 音量放大1.5倍
                mix=True               # 与原音频混合
            )
            output_path = os.path.join(output_dir, "demo_audio_segment.mp4")
            editor2.output_path = output_path
            editor2.save()
            print(f"✅ 已生成: {output_path}")
        else:
            print(f"⚠️  音频文件不存在: {audio_file}")
    except Exception as e:
        print(f"❌ 音频片段演示失败: {e}")
    finally:
        editor2.close()


def demo_video_concatenation():
    """演示视频合并功能"""
    print("\n🎬 演示 MoviePyVideoEditor 视频合并功能")
    
    input_video = r"D:\test1\video025.mp4"
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 演示简单合并
    print("\n1️⃣ 演示：简单视频合并")
    editor1 = MoviePyVideoEditor(input_video)
    try:
        # 注意：请替换为实际的第二个视频文件路径
        second_video = r"D:\test1\video026.mp4"
        if os.path.exists(second_video):
            editor1.concatenate(
                second_video=second_video,
                transition="none"
            )
            output_path = os.path.join(output_dir, "demo_concatenate_simple.mp4")
            editor1.output_path = output_path
            editor1.save()
            print(f"✅ 已生成: {output_path}")
        else:
            print(f"⚠️  第二个视频文件不存在: {second_video}")
    except Exception as e:
        print(f"❌ 简单合并演示失败: {e}")
    finally:
        editor1.close()
    
    # 2. 演示带转场效果的合并
    print("\n2️⃣ 演示：带淡入淡出转场的视频合并")
    editor2 = MoviePyVideoEditor(input_video)
    try:
        if os.path.exists(second_video):
            editor2.concatenate(
                second_video=second_video,
                transition="fade",
                transition_duration=2.0
            )
            output_path = os.path.join(output_dir, "demo_concatenate_fade.mp4")
            editor2.output_path = output_path
            editor2.save()
            print(f"✅ 已生成: {output_path}")
        else:
            print(f"⚠️  第二个视频文件不存在: {second_video}")
    except Exception as e:
        print(f"❌ 转场合并演示失败: {e}")
    finally:
        editor2.close()


def main():
    """主函数"""
    print("🚀 MoviePyVideoEditor 功能演示")
    print("=" * 50)
    
    try:
        # 演示音频功能
        demo_audio_features()
        
        # 演示视频合并功能
        demo_video_concatenation()
        
        print("\n🎉 演示完成！")
        print("\n📝 使用说明：")
        print("1. 请确保输入的视频文件存在")
        print("2. 请确保音频文件存在（用于音频功能演示）")
        print("3. 请确保第二个视频文件存在（用于合并功能演示）")
        print("4. 所有输出文件将保存在 Output 目录中")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        print("请检查文件路径是否正确，以及是否已安装所需的依赖包。")


if __name__ == "__main__":
    main()
