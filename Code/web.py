import os
import cv2
import tempfile
import subprocess
import numpy as np
import streamlit as st

from instance_segmentation_model import InstanceSegmentationModel

def create_folder():
    results_dir = "Results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)
    folder_count = len([name for name in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, name))])
    new_folder_name = f"{folder_count + 1:05d}"
    st.session_state['new_folder_path'] = os.path.join(results_dir, new_folder_name)
        
    os.makedirs(st.session_state['new_folder_path'], exist_ok=True)

# 显示初始界面
def show_initial_page():
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

# 初始化session state
def init_home_session_state():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'eliminate_state' not in st.session_state:
        st.session_state.eliminate_state = {}
    if 'add_state' not in st.session_state:
        st.session_state.add_state = {}
    if 'new_folder_path' not in st.session_state:
        st.session_state['new_folder_path'] = None

def init_eliminate_session_state():
    if 'original_video' not in st.session_state.eliminate_state:
       st.session_state.eliminate_state['original_video'] =None
    if 'detect_target_video' not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['detect_target_video'] = None
    if 'mask_target_video' not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['mask_target_video'] = None
    if 'remove_target_video' not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['remove_target_video'] = None
    if "object_images" not in st.session_state.eliminate_state:
        st.session_state.eliminate_state['object_images'] = []

# 显示消除视频
def show_eliminate_videos():
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.header('原始视频')
        if st.session_state.eliminate_state['original_video'] is not None:
            st.session_state.eliminate_state['original_video'] = st.session_state.eliminate_state['original_video'].replace("\\", "/")
            st.video(st.session_state.eliminate_state['original_video'])
        else:
            st.image("https://via.placeholder.com/400x300?text=Original+Video", caption="原始视频预览")

    with col2:
        st.header('实例分割视频')
        if st.session_state.eliminate_state['detect_target_video'] is not None and os.path.exists(st.session_state.eliminate_state['detect_target_video']):
            st.session_state.eliminate_state['detect_target_video'] = st.session_state.eliminate_state['detect_target_video'].replace("\\", "/")
            st.video(st.session_state.eliminate_state['detect_target_video'])
        else:
            st.image("https://via.placeholder.com/400x300?text=Processed+Video+2", caption="实例分割视频预览")

    with col3:
        st.header('蒙版视频')
        if st.session_state.eliminate_state['mask_target_video'] is not None and os.path.exists(st.session_state.eliminate_state['mask_target_video']):
            st.session_state.eliminate_state['mask_target_video'] = st.session_state.eliminate_state['mask_target_video'].replace("\\", "/")
            st.video(st.session_state.eliminate_state['mask_target_video'])
        else:
            st.image("https://via.placeholder.com/400x300?text=Processed+Video+1", caption="蒙版视频预览")

    with col4:
        st.header('目标消除视频')
        if st.session_state.eliminate_state['remove_target_video'] is not None and os.path.exists(st.session_state.eliminate_state['remove_target_video']):
            st.session_state.eliminate_state['remove_target_video'] = st.session_state.eliminate_state['remove_target_video'].replace("\\", "/")
            st.video(st.session_state.eliminate_state['remove_target_video'])
        else:
            st.image("https://via.placeholder.com/400x300?text=Processed+Video+3", caption="目标消除视频预览")

    print("original_video", st.session_state.eliminate_state['original_video'])
    print("detect_target_video", st.session_state.eliminate_state['detect_target_video'])
    print("mask_target_video", st.session_state.eliminate_state['mask_target_video'])
    print("remove_target_video", st.session_state.eliminate_state['remove_target_video'])

def remove_detect_target():
    script_path = '../E2FGVI-master/test.py'
    model = 'e2fgvi'
    video = st.session_state.eliminate_state['original_video']
    mask = f"{st.session_state['new_folder_path']}/frames_mask" 
    ckpt = "../E2FGVI-master/release_model/E2FGVI-CVPR22.pth"
    video_name = video.split("\\")[-1].split(".")[0]
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

    st.session_state.eliminate_state['remove_target_video'] = os.path.join(
        st.session_state['new_folder_path'], f"{video_name}_results.mp4")


# 预处理视频
def pre_process_video(uploaded_file,model):
    with st.spinner("正在处理视频..."):
        # 创建文件夹存储视频
        create_folder()

        st.session_state.eliminate_state['original_video'] = os.path.join(st.session_state['new_folder_path'], uploaded_file.name)
        st.session_state.eliminate_state['detect_target_video'] = None
        st.session_state.eliminate_state['mask_target_video'] = None
        st.session_state.eliminate_state['remove_target_video'] = None

        original_video_name = uploaded_file.name  

        # 保存原始视频到新文件夹
        with open(st.session_state.eliminate_state['original_video'], 'wb') as f:
            f.write(uploaded_file.read())

        model.set_video(original_video_path=st.session_state.eliminate_state['original_video'] , 
                output_video_path=st.session_state['new_folder_path'])
        model.instance_segmentation()

        st.session_state.eliminate_state['detect_target_video'] = os.path.join(st.session_state['new_folder_path'], 'instance_segmentation.mp4')
        

# 显示消除页面
def show_eliminate_page():
    instance_segmentation_model = InstanceSegmentationModel()
    st.title('🚫 视频对象消除')
    st.markdown("---")

    if st.button('🏠 返回主页'):
        st.session_state.current_page = 'home'
        st.rerun()

    init_eliminate_session_state()

    upload_button_text = "📤上传视频"
    uploaded_file = st.file_uploader(upload_button_text, type=['mp4', 'avi'], key='eliminate_uploader')

    video_name = uploaded_file.name if uploaded_file else ""

    if uploaded_file and uploaded_file != st.session_state.eliminate_state['original_video']:
        pre_process_video(uploaded_file, instance_segmentation_model)
        print("track_id_dict\n",instance_segmentation_model.track_id_dict)

    if len(instance_segmentation_model.track_id_dict) > 0:
        sorted_detected_object_ids = sorted(instance_segmentation_model.track_id_dict.values())
        removeWay = st.selectbox("选择消除方式", ["多选框消除","语音指令消除", "文字指令消除"])

        target_remove_objects = []
        if removeWay == "语音指令消除" or removeWay == "文字指令消除":
            st.markdown("to be continued...")
        elif removeWay == "多选框消除":
            selected_object_ids = st.multiselect(
                label='选择消除对象：',
                options=sorted_detected_object_ids
            )    
            if st.button("确认", key='maskSegmentationButton') and len(selected_object_ids) > 0:
                if selected_object_ids:
                    target_remove_objects = selected_object_ids
                    st.success(f"您已选择对象ID: {target_remove_objects}")

        if target_remove_objects:
            with st.spinner("正在消除选定目标..."):
                instance_segmentation_model.mask_generation(target_remove_objects)
                st.session_state.eliminate_state['mask_target_video'] = os.path.join(st.session_state['new_folder_path'], 'mask_generation.mp4')
                remove_detect_target()

    show_eliminate_videos()

# 主程序
def main():
    set_style()
    init_home_session_state()
    if st.session_state.current_page == 'home':
        show_initial_page()
    elif st.session_state.current_page == 'eliminate':
        show_eliminate_page()
    elif st.session_state.current_page == 'add':
        #show_add_page()
        st.markdown("to be continued...")

# 设置页面样式
def set_style():
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