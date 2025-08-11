import os
import hashlib
import subprocess
import streamlit as st
from typing import Optional, List
from instance_segmentation_model import InstanceSegmentationModel


class VideoEditorWebApp:
    """基于Streamlit的智能视频编辑系统前端界面类，提供视频对象消除和合成功能。"""

    def __init__(self):
        """初始化视频编辑系统，设置页面样式并初始化会话状态。"""
        self._set_style()
        self._init_session_state()
        self.instance_segmentation_model = None

    def _set_style(self) -> None:
        """设置Streamlit页面样式，优化按钮和布局的视觉效果。"""
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

    def _init_session_state(self) -> None:
        """初始化会话状态，设置默认页面和状态字典。"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'
        if 'eliminate_state' not in st.session_state:
            st.session_state.eliminate_state = {
                'original_video': None,
                'last_file_hash': None,
                'detect_target_video': None,
                'mask_target_video': None,
                'remove_target_video': None,
                'object_images': []
            }
        if 'add_state' not in st.session_state:
            st.session_state.add_state = {}
        if 'new_folder_path' not in st.session_state:
            st.session_state['new_folder_path'] = None

    def _create_folder(self) -> None:
        """创建结果存储文件夹，按照编号递增命名。"""
        results_dir = "../Results"
        os.makedirs(results_dir, exist_ok=True)
        folder_count = len([name for name in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, name))])
        new_folder_name = f"{folder_count + 1:05d}"
        st.session_state['new_folder_path'] = os.path.join(results_dir, new_folder_name)
        os.makedirs(st.session_state['new_folder_path'], exist_ok=True)

    def _get_partial_file_hash(self, file, chunk_size: int = 4096, num_chunks: int = 10) -> str:
        """
        计算文件部分内容的哈希值，用于检测文件是否发生变化。

        参数:
            file: 上传的文件对象。
            chunk_size (int): 每次读取的块大小，默认为4096字节。
            num_chunks (int): 读取的块数量，默认为10。

        返回:
            str: 文件的SHA256哈希值。
        """
        file.seek(0)
        hash_object = hashlib.sha256()
        for _ in range(num_chunks):
            chunk = file.read(chunk_size)
            if not chunk:
                break
            hash_object.update(chunk)
        file.seek(0)
        return hash_object.hexdigest()

    def _pre_process_video(self, uploaded_file, model: InstanceSegmentationModel) -> None:
        """
        预处理上传的视频，保存原始视频并执行实例分割。

        参数:
            uploaded_file: 上传的视频文件对象。
            model (InstanceSegmentationModel): 实例分割模型实例。
        """
        with st.spinner("正在处理视频..."):
            self._create_folder()

            st.session_state.eliminate_state['original_video'] = os.path.join(st.session_state['new_folder_path'], uploaded_file.name)
            st.session_state.eliminate_state['detect_target_video'] = None
            st.session_state.eliminate_state['mask_target_video'] = None
            st.session_state.eliminate_state['remove_target_video'] = None

            with open(st.session_state.eliminate_state['original_video'], 'wb') as f:
                f.write(uploaded_file.read())

            model.set_video(
                original_video_path=st.session_state.eliminate_state['original_video'],
                output_video_path=st.session_state['new_folder_path']
            )
            model.instance_segmentation()

            st.session_state.eliminate_state['detect_target_video'] = os.path.join(st.session_state['new_folder_path'], 'instance_segmentation.mp4')

    def _remove_detect_target(self, video: str) -> None:
        """
        执行目标消除，使用外部脚本处理视频和掩码。

        参数:
            video (str): 输入视频文件路径。
        """
        script_path = '../E2FGVI_master/test.py'
        model = 'e2fgvi'
        mask = f"{st.session_state['new_folder_path']}/frames_mask"
        ckpt = "../E2FGVI_master/release_model/E2FGVI-CVPR22.pth"
        video_name = video.split("/")[-1].split(".")[0]

        try:
            subprocess.run([
                "python", script_path,
                "--model", model,
                "--video", video,
                "--mask", mask,
                "--ckpt", ckpt,
                "--save_path", st.session_state['new_folder_path']
            ], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"命令运行失败，错误代码: {e.returncode}")

        st.session_state.eliminate_state['remove_target_video'] = os.path.join(
            st.session_state['new_folder_path'], f"{video_name}_results.mp4"
        )

    def _show_initial_page(self) -> None:
        """显示系统主页，提供功能选择入口。"""
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

    def _show_eliminate_videos(self) -> None:
        """显示视频对象消除页面的四个视频预览：原始、实例分割、蒙版和目标消除视频。"""
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

    def _show_eliminate_page(self) -> None:
        """显示视频对象消除页面，处理视频上传、目标选择和消除逻辑。"""
        if 'instance_segmentation_model' not in st.session_state:
            st.session_state.instance_segmentation_model = InstanceSegmentationModel()
        self.instance_segmentation_model = st.session_state.instance_segmentation_model

        st.title('🚫 视频对象消除')
        st.markdown("---")

        if st.button('🏠 返回主页'):
            st.session_state.current_page = 'home'
            st.rerun()

        uploaded_file = st.file_uploader("📤 上传视频", type=['mp4', ' Avi'], key='eliminate_uploader')

        if uploaded_file:
            current_file_hash = self._get_partial_file_hash(uploaded_file)
            last_file_hash = st.session_state.eliminate_state.get('last_file_hash')
            if current_file_hash != last_file_hash:
                self._pre_process_video(uploaded_file, self.instance_segmentation_model)
                st.session_state.eliminate_state['last_file_hash'] = current_file_hash

        if len(self.instance_segmentation_model.track_id_dict) > 0:
            sorted_detected_object_ids = sorted(self.instance_segmentation_model.track_id_dict.values())
            remove_method = st.selectbox("选择消除方式", ["多选框消除", "语音指令消除", "文字指令消除"])

            if remove_method == "语音指令消除" or remove_method == "文字指令消除":
                st.markdown("功能开发中...")
            elif remove_method == "多选框消除":
                selected_object_ids = st.multiselect(
                    label='选择消除对象：',
                    options=sorted_detected_object_ids
                )
                # 禁用确认按钮直到选择至少一个对象
                confirm_button_disabled = len(selected_object_ids) == 0
                if st.button("确认", key='maskSegmentationButton', disabled=confirm_button_disabled,help="请选择至少一个要消除的对象"):
                    target_remove_objects = selected_object_ids
                    st.success(f"您已选择对象ID: {target_remove_objects}")
                    with st.spinner("正在消除选定目标..."):
                        self.instance_segmentation_model.mask_generation(target_remove_objects)
                        st.session_state.eliminate_state['mask_target_video'] = os.path.join(
                            st.session_state['new_folder_path'], 'mask_generation.mp4')
                        self._remove_detect_target(st.session_state.eliminate_state['original_video'])

        self._show_eliminate_videos()

    def run(self) -> None:
        """运行视频编辑系统，根据当前页面状态显示对应界面。"""
        if st.session_state.current_page == 'home':
            self._show_initial_page()
        elif st.session_state.current_page == 'eliminate':
            self._show_eliminate_page()
        elif st.session_state.current_page == 'add':
            st.markdown("功能开发中...")


if __name__ == "__main__":
    app = VideoEditorWebApp()
    app.run()