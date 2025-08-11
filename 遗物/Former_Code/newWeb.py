import streamlit as st
import os
import tempfile
import subprocess
import re
import cv2
import numpy as np    
from PIL import Image

from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from Eliminate import instance_segmentation, mask_segmentation
from ToolClasses import ObjectTracker,VideoProcessor
from Audio import AudioWeb, getAudio, AudioToText
from KeyWordEn import tokenize,checkRemoveObjects
from SynthsizeVideo import get_available_objects,generate_preview,synthesize_video

# ---------------------------- 消除功能页面 ----------------------------

def maskAndRemove(selectedIDs,sessionState):
   # 确保原视频路径有效

    if not os.path.exists( sessionState['original_video_path']):
        st.error(f"原视频路径无效：{ sessionState['original_video_path']}")
    else:
    # 运行 mask_segmentation
        mask_segmentation(
            st.session_state.all_results,
            sessionState['original_video_path'],  # 原视频路径
            sessionState['new_folder_path'],  # 输出目录
            "frames_mask",  # 帧输出目录
            selectedIDs,    # 选中的对象ID列表
            sessionState.id_mapping
        )   

        # 更新处理后的视频路径
        st.session_state.eliminate_state['processed_video'] = os.path.join(sessionState['new_folder_path'], 'mask_segmentation_output.mp4')
        
        # 定义参数
        script_path = r"..\..\E2FGVI-master\test.py"#path to your e2fgvi model
        model = "e2fgvi"
        video = sessionState['original_video_path']
        mask = fr"{sessionState['new_folder_path']}\frames_mask" 
        #r"D:\test1\frames_mask"
        ckpt = r"..\..\E2FGVI-master\release_model\E2FGVI-CVPR22.pth"#path to your e2fgvi model
        #使用 subprocess 运行命令
        try:
            subprocess.run([
                "python", script_path, 
                "--model", model, 
                "--video", video, 
                "--mask", mask, 
                "--ckpt", ckpt
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"命令运行失败，错误代码: {e.returncode}")
            print(f"错误信息: {e.stderr}")

        st.session_state.eliminate_state['recognition_result_removed_video'] = os.path.join(
            st.session_state['new_folder_path'], f"{st.session_state['base_name']}_results.mp4")

def show_eliminate_page():
    st.title('🚫 视频对象消除')
    st.markdown("---")
    
    target_classes = {"person": "人"}

    # 初始化消除页面状态

    if 'original_video' not in st.session_state.eliminate_state:
       st.session_state.eliminate_state['original_video'] =None
    if 'processed_video' not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['processed_video'] = None
    if 'recognition_result_video' not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['recognition_result_video'] = None
    if 'recognition_result_removed_video' not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['recognition_result_removed_video'] = None
    if 'detected_object_ids' not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['detected_object_ids'] = []
    if "selected_object_ids" not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['selected_object_ids'] = []
    if "object_images" not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['object_images'] = []

    # 文件上传
    upload_button_text = "📤上传视频"
    uploaded_file = st.file_uploader(upload_button_text, type=['mp4', 'avi'], key='eliminate_uploader')

    # 返回主页
    if st.button('🏠 返回主页'):
        st.session_state.current_page = 'home'
        st.rerun()

    # 仅在首次上传视频时运行 instance_segmentation
    if uploaded_file and uploaded_file != st.session_state.eliminate_state['original_video']:

        with st.spinner("正在处理视频..."):
            st.session_state.eliminate_state['original_video'] = uploaded_file
            original_video_name = uploaded_file.name  
            st.session_state['base_name'] = os.path.splitext(original_video_name)[0]
            
            # 创建新文件夹
            create_folder()

            # 设置视频路径
            st.session_state['original_video_path'] = os.path.join(st.session_state['new_folder_path'], uploaded_file.name)

            # 保存原始视频到新文件夹
            with open(st.session_state['original_video_path'], 'wb') as f:
                f.write(uploaded_file.read())

            print("\n\nnew_folder_path:",st.session_state['new_folder_path'])
            print("\n\noriginal_video_path:",st.session_state['original_video_path'])

            # 运行 instance_segmentation 并保存结果到 st.session_state.eliminate_state
            (st.session_state.eliminate_state['detected_object_ids'], 
            st.session_state.all_results,
            st.session_state.id_mapping, 
            object_images
            ) = instance_segmentation(
                st.session_state['original_video_path'], st.session_state['new_folder_path'], target_classes
            )
            st.session_state.eliminate_state['object_images'] = object_images

            # 设置视频路径
            recognition_result_video_path = os.path.join(st.session_state['new_folder_path'], 'instance_segmentation_output.mp4')
            st.session_state.eliminate_state['recognition_result_video'] = recognition_result_video_path

    # 如果已检测到对象，显示多选框和录音按钮
    if st.session_state.eliminate_state['detected_object_ids']:
        sorted_detected_object_ids = sorted(st.session_state.eliminate_state['detected_object_ids'])

        removeWay = st.selectbox("选择消除方式", ["多选框消除","语音指令消除", "文字指令消除"])
        print("sorted_detected_object_ids",sorted_detected_object_ids)

        # 根据选择执行相应的操作
        target_remove_objects = []
        if removeWay == "语音指令消除" or removeWay == "文字指令消除":
            category_values = list(target_classes.values())
            display_text = "、".join(category_values)
            st.markdown(f"可供消除的对象类型有：{display_text}")

            if removeWay == "语音指令消除":
            # 录音函数
                text = AudioWeb()     
            elif removeWay == "文字指令消除":
            # 文字指令输入
                text = st.text_input(label='请输入消除指令:',max_chars=100)  
            
            # 翻译+匹配
            if text:
                tokesized_text = tokenize(text)
                target_remove_objects = checkRemoveObjects(target_classes,sorted_detected_object_ids,tokesized_text)

            if target_remove_objects:
                st.success(f"您已选择对象ID: {target_remove_objects}")
            else:
                st.warning("未识别到可行的消除目标")
            
        elif removeWay == "多选框消除":
            st.session_state.eliminate_state['selected_object_ids'] = st.multiselect(
                label='选择消除对象：',
                options=sorted_detected_object_ids,  # 使用检测到的对象ID作为选项
            )   
            if st.button("确认", key='maskSegmentationButton'):
                if st.session_state.eliminate_state['selected_object_ids']:
                    target_remove_objects =  st.session_state.eliminate_state['selected_object_ids']
                    if target_remove_objects:
                        st.success(f"您已选择对象ID: {target_remove_objects}")
        
        if target_remove_objects:
            with st.spinner("正在消除选定目标..."):
                maskAndRemove(target_remove_objects,st.session_state)

    
    # 显示视频预览
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.header('原始视频')
        if st.session_state.eliminate_state['original_video'] is not None:
            st.video(st.session_state.eliminate_state['original_video'])
        else:
            st.image("https://via.placeholder.com/400x300?text=Original+Video", caption="原始视频预览")

    with col2:
        st.header('实例分割视频')
        if st.session_state.eliminate_state['recognition_result_video'] is not None and os.path.exists(st.session_state.eliminate_state['recognition_result_video']):
            st.video(st.session_state.eliminate_state['recognition_result_video'])
        else:
            st.image("https://via.placeholder.com/400x300?text=Processed+Video+2", caption="实例分割视频预览")

    with col3:
        st.header('蒙版视频')
        if st.session_state.eliminate_state['processed_video'] is not None and os.path.exists(st.session_state.eliminate_state['processed_video']):
            st.video(st.session_state.eliminate_state['processed_video'])
        else:
            st.image("https://via.placeholder.com/400x300?text=Processed+Video+1", caption="蒙版视频预览")

    with col4:
        st.header('目标消除视频')
        if st.session_state.eliminate_state['recognition_result_removed_video'] is not None and os.path.exists(st.session_state.eliminate_state['recognition_result_removed_video']):
            st.video(st.session_state.eliminate_state['recognition_result_removed_video'])
        else:
            st.image("https://via.placeholder.com/400x300?text=Processed+Video+3", caption="目标消除视频预览")

    # 多选框中显示所有目标的唯一标识
    st.header("选择目标查看详情")
    options = [item[0] for item in st.session_state.eliminate_state['object_images'] ]
    selected = st.multiselect("选择目标", options, default=options)
    
    # 根据选择展示目标图片、名称和描述，左右分栏显示
    for option in selected:
        for unique_id, obj_img, desc in st.session_state.eliminate_state['object_images'] :
            if unique_id == option:
                original_width, original_height = obj_img.size

                new_hight = 180
                new_width = int(original_width * new_hight / original_height)
                obj_img = obj_img.resize((new_width, new_hight))

                col_img, col_info = st.columns([1, 2])
                with col_img:
                    st.image(obj_img, caption=unique_id)
                with col_info:
                    st.markdown(f"**目标名称：** {unique_id}")
                    st.markdown(f"**描述：** {desc}")
                break



# ---------------------------- 合成功能页面 ----------------------------
def show_add_page():
    st.title('➕ 视频对象合成')
    st.markdown("---")
    
    processor = VideoProcessor()
    
    # 初始化合成页面状态
    if 'video1' not in st.session_state.add_state:
        st.session_state.add_state['video1'] = None
    if 'video2' not in st.session_state.add_state:
        st.session_state.add_state['video2'] = None

    # 文件上传
    with st.expander("📤 上传视频", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            video1 = st.file_uploader("选择视频1", type=["mp4", "avi"], key='add_video1')
        with col2:
            video2 = st.file_uploader("选择视频2", type=["mp4", "avi"], key='add_video2')

    create_new_folder = False
    flag = 0
    # 视频处理逻辑
    if video1 and not st.session_state.add_state['video1']:
        create_new_folder = True
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
            tfile.write(video1.read())
            video_path = tfile.name
        
        with st.spinner("正在处理视频1..."):
            st.session_state.add_state['video1'] = processor.process_video(video_path, "video1")
        os.unlink(video_path)

    if video2 and not st.session_state.add_state['video2']:
        create_new_folder = True
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
            tfile.write(video2.read())
            video_path = tfile.name
        
        with st.spinner("正在处理视频2..."):
            st.session_state.add_state['video2'] = processor.process_video(video_path, "video2")
        os.unlink(video_path)

    if create_new_folder and flag == 0:
        create_folder()

    # 返回主页
    if st.button('🏠 返回主页'):
        st.session_state.current_page = 'home'
        st.rerun()

        #——————————————————

    if st.session_state.add_state['video1'] and st.session_state.add_state['video2']:
        st.success("✅ 视频分析完成！")
        st.markdown("---")
        
        with st.expander("🎨 合成设置", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                bg_choice = st.selectbox("选择背景视频", ["视频1", "视频2"])
            with col2:
                available_objects = get_available_objects()
                layer_order = st.multiselect(
                    "图层顺序（从上到下）",
                    available_objects,
                    format_func=lambda x: f"{x.split('_')[0]} - {x.split('_')[1]} {x.split('_')[2]}"
                )

        with st.expander("👀 实时预览", expanded=True):
            if st.session_state.add_state['video1']['frames'] and st.session_state.add_state['video2']['frames']:
                max_frame = min(len(st.session_state.add_state['video1']['frames']), len(st.session_state.add_state['video2']['frames'])) - 1
                frame_idx = st.slider("选择帧号", 0, max_frame, 0)
                
                if st.button("生成预览"):
                    preview = generate_preview(bg_choice, layer_order, frame_idx)
                    st.image(preview, use_container_width =True)

        st.markdown("---")
        with st.expander("🎞️ 视频合成", expanded=True):
            output_name = st.text_input("输出文件名", "synthesized_video.mp4")
            if st.button("开始合成"):
                with st.spinner("正在合成视频..."):
                    output_path = synthesize_video(bg_choice, layer_order, output_name)
                    st.video(output_path)
                    st.success(f"✅ 视频合成完成！保存路径：{output_path}")
                    print("\n\noutput_path:",output_path,"\n\n")


# ---------------------------- 通用工具函数 ----------------------------
def init_session_state():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'eliminate_state' not in st.session_state:
        st.session_state.eliminate_state = {}
    if 'add_state' not in st.session_state:
        st.session_state.add_state = {}

def create_folder():
    # 确定存储结果的文件夹路径
    results_dir = os.path.join(os.getcwd(), r"..\Results")
    folder_count = len([name for name in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, name))])
    new_folder_name = f"{folder_count + 1:05d}"  # 生成格式为 '00001' 的文件夹名
    st.session_state['new_folder_path'] = os.path.join(results_dir, new_folder_name)
        
    # 创建新的文件夹
    os.makedirs(st.session_state['new_folder_path'], exist_ok=True)


# ---------------------------- 导航页面 ----------------------------
def show_home():
    st.title('🎥 智能视频编辑系统')
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button('🚫 视频对象消除', use_container_width=True):
            st.session_state.current_page = 'eliminate'
            st.rerun()
        st.markdown("""
            **功能说明**  
            1. 上传需要处理的视频  
            2. 选择要消除的对象  
            3. 生成消除后的视频
        """)

    with col2:
        if st.button('➕ 视频对象合成', use_container_width=True):
            st.session_state.current_page = 'add'
            st.rerun()
        st.markdown("""
            **功能说明**  
            1. 上传两个视频素材  
            2. 设置合成参数  
            3. 生成合成视频
        """)
    
    st.markdown("---")


# ---------------------------- 主程序 ----------------------------
def main():
    init_session_state()
    if 'base_name' not in st.session_state:
        st.session_state['base_name'] = None
    if 'original_video_path' not in st.session_state:
        st.session_state['original_video_path'] = None
    if 'new_folder_path' not in st.session_state:
        st.session_state['new_folder_path'] = None
    # 页面路由
    if st.session_state.current_page == 'home':
        show_home()
    elif st.session_state.current_page == 'eliminate':
        show_eliminate_page()
    elif st.session_state.current_page == 'add':
        show_add_page()

    # 添加样式
    st.markdown("""
    <style>
    [data-testid="stButton"] > button {
        border-radius: 10px;
        padding: 1rem 2rem;
        transition: all 0.3s;
    }
    [data-testid="stButton"] > button:hover {
        transform: scale(1.05);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-1y4p8pa {
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()