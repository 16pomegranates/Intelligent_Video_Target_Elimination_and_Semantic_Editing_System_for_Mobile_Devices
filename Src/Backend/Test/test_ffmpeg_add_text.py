#!/usr/bin/env python3
"""
独立测试：使用 FFmpegVideoEditor 给视频添加字幕（底部居中，指定开始时间与持续时间）。
"""

import os
from ffmpeg_editor import FFmpegVideoEditor


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def test_ffmpeg_add_text(
    input_video: str,
    output_path: str,
    text: str = "测试字幕",
    fontsize: int = 64,
    start_time: float = 0.0,
    duration: float = 5.0,
):
    ensure_dir(os.path.dirname(output_path))
    editor = FFmpegVideoEditor(input_video)
    try:
        editor.add_text(text=text, fontsize=fontsize, duration=duration, start_time=start_time)
        editor.output_path = output_path
        editor.save()
        print(f"OK: 已输出 -> {output_path}")
    finally:
        editor.close()


if __name__ == "__main__":
    # 根据你的本地路径修改
    input_video = r"D:\test1\video001.mp4"
    output_path = r"D:\ClipPersona\Src\Backend\Output\ffmpeg_add_text.mp4"
    test_ffmpeg_add_text(input_video, output_path)

    # 批量连贯字幕
    output_path2 = r"D:\\ClipPersona\\Src\\Backend\\Output\\ffmpeg_add_text_batch.mp4"
    editor = FFmpegVideoEditor(input_video)
    try:
        subtitles = [
            ["测试字幕1", 0, 3],          # 默认36号
            ["测试字幕2", 3, 5, 40],     # 明确40号
            ["测试字幕3", 8, 4],          # 默认36号
        ]
        editor.add_subtitles(subtitles)
        editor.output_path = output_path2
        editor.save()
        print(f"OK: 批量字幕已输出 -> {output_path2}")
    finally:
        editor.close()


