#!/usr/bin/env python3
"""
测试修复后的视频合并功能
"""

import os
import sys
from moviepy_editor import MoviePyVideoEditor

def test_simple_concatenation():
    """测试简单视频合并"""
    print("🧪 测试简单视频合并...")
    
    # 测试文件路径
    input_video = r"D:\test1\video025.mp4"
    second_video = r"D:\test1\video026.mp4"
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    
    if not os.path.exists(input_video):
        print(f"❌ 输入视频不存在: {input_video}")
        return False
    
    if not os.path.exists(second_video):
        print(f"❌ 第二个视频不存在: {second_video}")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        editor = MoviePyVideoEditor(input_video)
        
        # 测试简单合并
        editor.concatenate(
            second_video=second_video,
            transition="none"
        )
        
        # 设置输出路径
        output_path = os.path.join(output_dir, "test_simple_merge.mp4")
        editor.output_path = output_path
        
        # 保存
        editor.save()
        print(f"✅ 简单合并测试成功: {output_path}")
        
        editor.close()
        return True
        
    except Exception as e:
        print(f"❌ 简单合并测试失败: {e}")
        if 'editor' in locals():
            editor.close()
        return False

def test_fade_transition():
    """测试淡入淡出转场合并"""
    print("\n🧪 测试淡入淡出转场合并...")
    
    input_video = r"D:\test1\video025.mp4"
    second_video = r"D:\test1\video026.mp4"
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    
    if not os.path.exists(input_video) or not os.path.exists(second_video):
        print("❌ 测试视频文件不存在")
        return False
    
    try:
        editor = MoviePyVideoEditor(input_video)
        
        # 测试淡入淡出转场
        editor.concatenate(
            second_video=second_video,
            transition="fade",
            transition_duration=1.0
        )
        
        # 设置输出路径
        output_path = os.path.join(output_dir, "test_fade_transition.mp4")
        editor.output_path = output_path
        
        # 保存
        editor.save()
        print(f"✅ 淡入淡出转场测试成功: {output_path}")
        
        editor.close()
        return True
        
    except Exception as e:
        print(f"❌ 淡入淡出转场测试失败: {e}")
        if 'editor' in locals():
            editor.close()
        return False

def test_multiple_concatenation():
    """测试多视频合并"""
    print("\n🧪 测试多视频合并...")
    
    input_video = r"D:\test1\video025.mp4"
    video_files = [r"D:\test1\video026.mp4", r"D:\test1\video016.mp4"]  # 可以添加更多视频文件
    output_dir = r"D:\ClipPersona\Src\Backend\Output"
    
    if not os.path.exists(input_video):
        print(f"❌ 输入视频不存在: {input_video}")
        return False
    
    # 检查所有视频文件是否存在
    missing_files = [f for f in video_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ 以下视频文件不存在: {missing_files}")
        return False
    
    try:
        editor = MoviePyVideoEditor(input_video)
        
        # 测试多视频合并
        editor.concatenate_multiple(
            video_files=video_files,
            transition="none"
        )
        
        # 设置输出路径
        output_path = os.path.join(output_dir, "test_multiple_merge.mp4")
        editor.output_path = output_path
        
        # 保存
        editor.save()
        print(f"✅ 多视频合并测试成功: {output_path}")
        
        editor.close()
        return True
        
    except Exception as e:
        print(f"❌ 多视频合并测试失败: {e}")
        if 'editor' in locals():
            editor.close()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试修复后的视频合并功能")
    print("=" * 50)
    
    # 检查测试环境
    print("📋 检查测试环境...")
    test_dir = r"D:\test1"
    if not os.path.exists(test_dir):
        print(f"❌ 测试目录不存在: {test_dir}")
        print("请确保测试视频文件存在")
        return
    
    # 运行测试
    tests = [
       # test_simple_concatenation,
       # test_fade_transition,
        test_multiple_concatenation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试 {test.__name__} 出现异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功！")
    else:
        print("⚠️  部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()
