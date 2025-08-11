#!/usr/bin/env python3
"""
测试：使用 FFmpegVideoEditor 保持纵横比改变视频分辨率。
生成两份输出：
- 1080p（保持纵横比，补边）
- 720p（保持纵横比，补边）
"""

import os
from ffmpeg_editor import FFmpegVideoEditor


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def test_set_resolution(input_video: str, out_1080: str, out_720: str):
    ensure_dir(os.path.dirname(out_1080))

    # 1080p
    editor = FFmpegVideoEditor(input_video)
    try:
        editor.set_resolution(1920, 1080, keep_aspect=True, fill_color='black')
        editor.output_path = out_1080
        editor.save()
        print(f"OK: 1080p 已输出 -> {out_1080}")
    finally:
        editor.close()

    # 720p
    editor2 = FFmpegVideoEditor(input_video)
    try:
        editor2.set_resolution(1280, 720, keep_aspect=True, fill_color='black')
        editor2.output_path = out_720
        editor2.save()
        print(f"OK: 720p 已输出 -> {out_720}")
    finally:
        editor2.close()


if __name__ == "__main__":
    input_video = r"D:\\test1\\video001.mp4"
    out_1080 = r"D:\\ClipPersona\\Src\\Backend\\Output\\setres_1080p.mp4"
    out_720 = r"D:\\ClipPersona\\Src\\Backend\\Output\\setres_720p.mp4"
    test_set_resolution(input_video, out_1080, out_720)

#!/usr/bin/env python3
"""
独立测试：使用 FFmpegVideoEditor 等比缩放输出 360p/480p/720p/1080p，保持原始比例不变。

运行方式：
  python Src/Backend/test_set_resolution.py

注意：需要本机已安装 ffmpeg/ffprobe，并将其加入 PATH。
"""

import os
import subprocess
import shlex
from typing import Tuple, Optional

from ffmpeg_editor import FFmpegVideoEditor


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_video_resolution(video_path: str) -> Optional[Tuple[int, int]]:
    """返回 (width, height)；若 ffprobe 不可用则返回 None。"""
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{video_path}"'
    try:
        result = subprocess.run(shlex.split(cmd), check=True, capture_output=True, text=True)
        text = result.stdout.strip()
        if 'x' in text:
            w_str, h_str = text.split('x')
            return int(w_str), int(h_str)
    except Exception:
        return None
    return None


def export_with_resolution(input_video: str, output_path: str, preset: str) -> None:
    ensure_dir(os.path.dirname(output_path))
    editor = FFmpegVideoEditor(input_video)
    try:
        in_res = get_video_resolution(input_video)
        print(f"输入视频分辨率: {in_res[0]}x{in_res[1]}" if in_res else "输入分辨率未知")
        editor.set_resolution(resolution=preset)
        editor.output_path = output_path
        editor.save()
        res = get_video_resolution(output_path)
        if res:
            print(f"OK: {preset} -> {output_path} 分辨率={res[0]}x{res[1]}")
        else:
            print(f"OK: {preset} -> {output_path}")
    finally:
        editor.close()


if __name__ == "__main__":
    # 根据你的本地路径修改
    input_video = r"D:\\test1\\video025.mp4"
    output_dir = r"D:\\ClipPersona\\Src\\Backend\\Output"

    presets = ["360p", "480p", "720p", "1080p"]
    for p in presets:
        output_path = os.path.join(output_dir, f"res_{p}_keep.mp4")
        export_with_resolution(input_video, output_path, p)


