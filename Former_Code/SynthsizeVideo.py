import cv2
import os
import tempfile
import streamlit as st
import numpy as np

from PIL import Image
from moviepy import VideoFileClip, CompositeVideoClip

def get_available_objects():
    objects = []
    videos = {
        "video1": st.session_state.add_state['video1'],
        "video2": st.session_state.add_state['video2']
    }
    
    for vid_key, video in videos.items():
        if video and 'masks' in video:
            for mask_key in video['masks'].keys():
                if mask_key.count('_') >= 2:
                    parts = mask_key.split('_', 2)
                    objects.append(f"{parts[0]}_{parts[1]}_{parts[2]}")
    
    return list(set(objects))

def generate_preview(bg_choice, layer_order, frame_idx):
    bg_video = st.session_state.add_state['video1'] if bg_choice == "视频1" else st.session_state.add_state['video2']
    bg_frame = np.array(bg_video['frames'][frame_idx].copy())
    
    for layer in reversed(layer_order):
        vid_id, cls_name, obj_id = layer.split('_', 2)
        video = st.session_state.add_state['video1'] if vid_id == "video1" else st.session_state.add_state['video2']
        
        mask_key = f"{vid_id}_{cls_name}_{obj_id}"
        if mask_key in video['masks'] and frame_idx < len(video['masks'][mask_key]):
            mask = video['masks'][mask_key][frame_idx]
            obj_frame = np.array(video['frames'][frame_idx])
            
            mask_img = np.zeros_like(obj_frame)
            cv2.fillPoly(mask_img, [np.array(mask, dtype=np.int32)], (255, 255, 255))
            
            bg_frame = np.where(mask_img == 255, obj_frame, bg_frame)
    
    return Image.fromarray(bg_frame)

def synthesize_video(bg_choice, layer_order, output_name):
    bg_video = st.session_state.add_state['video1'] if bg_choice == "视频1" else st.session_state.add_state['video2']
    
    # 创建临时视频文件（解决原始文件被删除的问题）
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_bg:
        # 将背景视频帧重新编码保存
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_bg.name, fourcc, bg_video['fps'], 
                            bg_video['resolution'])
        for frame in bg_video['frames']:
            out.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
        out.release()
    
    # 使用新生成的临时文件
    bg_clip = VideoFileClip(temp_bg.name)
    clips = [bg_clip]

    # 为每个图层创建临时视频
    temp_files = []
    for layer in layer_order:
        vid_id, cls_name, obj_id = layer.split('_', 2)
        video = st.session_state.add_state['video1'] if vid_id == "video1" else st.session_state.add_state['video2']
        mask_key = f"{vid_id}_{cls_name}_{obj_id}"

        if mask_key not in video['masks']:
            continue

        # 创建临时视频文件
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_layer:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            layer_writer = cv2.VideoWriter(temp_layer.name, fourcc, video['fps'], 
                                         video['resolution'])
            
            for i in range(len(video['frames'])):
                mask_img = np.zeros_like(video['frames'][i])
                if i < len(video['masks'][mask_key]):
                    mask = video['masks'][mask_key][i]
                    cv2.fillPoly(mask_img, [np.array(mask, dtype=np.int32)], (255, 255, 255))
                layer_writer.write(cv2.cvtColor(mask_img, cv2.COLOR_RGB2BGR))
            
            layer_writer.release()
            temp_files.append(temp_layer.name)

        # 创建剪辑时添加重试机制
        try:
            mask_clip = VideoFileClip(temp_layer.name).set_opacity(1)
            clips.append(mask_clip)
        except Exception as e:
            st.error(f"创建图层剪辑失败：{str(e)}")
            continue

    # 合成视频（添加异常处理）
    try:
        final_clip = CompositeVideoClip(clips)
        final_clip.write_videofile(
            output_name,
            codec='libx264',
            fps=bg_video['fps'],
            ffmpeg_params=['-crf', '23', '-preset', 'fast'],
            logger=None  # 避免日志污染
        )
    except Exception as e:
        st.error(f"视频合成失败：{str(e)}")
        return None
    finally:
        # 清理临时文件
        os.unlink(temp_bg.name)
        for f in temp_files:
            os.unlink(f)

    return output_name