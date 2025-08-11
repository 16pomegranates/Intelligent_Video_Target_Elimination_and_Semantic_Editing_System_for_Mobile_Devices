import os
import cv2
import torch
import subprocess
import numpy as np
import shutil
from PIL import Image
from pathlib import Path
from sam2.build_sam import build_sam2_video_predictor

class SAM2InstanceSegmentationModel:
    """使用 SAM2 模型对视频进行实例分割的类。"""

    def __init__(self, model_cfg: str, checkpoint: str, device: str = "cuda"):
        """
        初始化 SAM2 模型，加载配置文件和检查点。

        参数:
            model_cfg (str): 模型配置文件路径。
            checkpoint (str): 模型检查点文件路径。
            device (str): 运行模型的设备（'cuda' 或 'cpu'），默认为 'cuda'。

        异常:
            RuntimeError: 如果请求使用 CUDA 但不可用。
        """
        self.model_cfg = model_cfg
        self.checkpoint = checkpoint
        self.device = device if torch.cuda.is_available() else "cpu"
        self.predictor = None
        self.input_video_path = None
        self.output_video_path = None
        self.original_frames_folder = "./original_frames"
        self.frames_mask_dir = "./frames_mask"  # 用于彩色掩码帧
        self.white_mask_dir = "./white_mask_frames"  # 用于黑白掩码图像
        self.original_mask_dir = "./original_mask_frames"  # 用于原始对象掩码图像
        self.frame_names = []
        self.video_segments = None  # 存储分割结果

        # 配置张量计算精度
        self._setup_precision()

        # 初始化 SAM2 视频预测器
        self._init_predictor()

    def _setup_precision(self) -> None:
        """配置张量计算的精度设置。"""
        torch.autocast(device_type=self.device, dtype=torch.bfloat16).__enter__()
        if self.device == "cuda" and torch.cuda.get_device_properties(0).major >= 8:
            # 为 Ampere GPU 启用 TensorFloat32
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True

    def _init_predictor(self) -> None:
        """初始化 SAM2 视频预测器。"""
        self.predictor = build_sam2_video_predictor(self.model_cfg, self.checkpoint)

    def set_video_path(self, input_video_path: str, output_video_path: str) -> None:
        """
        设置输入和输出视频路径。

        参数:
            input_video_path (str): 输入视频文件路径。
            output_video_path (str): 分割后输出视频的保存路径。

        异常:
            FileNotFoundError: 如果输入视频文件不存在。
        """
        self.input_video_path = input_video_path
        self.output_video_path = output_video_path
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"输入视频文件不存在: {input_video_path}")

    def _extract_frames(self, quality: int = 2, start_number: int = 0) -> None:
        """
        使用 FFmpeg 从输入视频中提取帧。

        参数:
            quality (int): 帧质量（0-31，数值越低质量越高），默认为 2。
            start_number (int): 起始帧编号，默认为 0。

        异常:
            subprocess.CalledProcessError: 如果 FFmpeg 命令执行失败。
        """
        os.makedirs(self.original_frames_folder, exist_ok=True)

        command = [
            'ffmpeg',
            '-i', self.input_video_path,
            '-q:v', str(quality),
            '-start_number', str(start_number),
            os.path.join(self.original_frames_folder, '%05d.jpg')
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"帧已成功提取到 {self.original_frames_folder}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg 执行失败: {e.stderr}")
            raise

        # 收集并排序帧文件名
        self.frame_names = [
            p for p in os.listdir(self.original_frames_folder)
            if p.lower().endswith(('.jpg', '.jpeg'))
        ]
        self.frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))

    def _apply_colored_mask(self, image: np.ndarray, mask: np.ndarray, color_id: int) -> np.ndarray:
        """
        将彩色掩码应用到图像上，保留原始背景，分割对象覆盖为彩色。

        参数:
            image (np.ndarray): 输入图像，形状为 (H, W, 3)。
            mask (np.ndarray): 二值掩码，形状为 (H, W)，1 表示前景，0 表示背景。
            color_id (int): 使用的颜色索引。

        返回:
            np.ndarray: 应用掩码后的图像，分割对象为彩色，背景保留原始图像。
        """
        colors = [
            np.array([0, 128, 255], dtype=np.uint8),  # 蓝色
            np.array([255, 128, 0], dtype=np.uint8)   # 橙色
        ]

        # 将掩码转换为 uint8 并创建三通道掩码
        int_mask = mask.astype(np.uint8)
        int_mask_3d = np.dstack((int_mask, int_mask, int_mask))

        # 创建彩色掩码
        mask_color = colors[color_id % len(colors)]  # 循环使用颜色
        colored_mask = np.full_like(image, mask_color)
        colored_mask[int_mask == 0] = 0

        # 混合图像和掩码
        alpha = 0.6  # 原始图像权重
        beta = 1 - alpha  # 掩码权重
        blended = cv2.addWeighted(image, alpha, colored_mask, beta, 0.0, dtype=cv2.CV_8U)

        # 在非掩码区域保留原始图像
        blended[int_mask_3d == 0] = image[int_mask_3d == 0]
        return blended

    def _apply_white_mask(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        将白色掩码应用到图像上，分割目标为白色，背景为黑色，不透明。

        参数:
            image (np.ndarray): 输入图像，形状为 (H, W, 3)。
            mask (np.ndarray): 二值掩码，形状为 (H, W)，1 表示前景，0 表示背景。

        返回:
            np.ndarray: 应用掩码后的图像，分割区域为白色，背景为黑色。
        """
        # 将掩码转换为 uint8
        int_mask = mask.astype(np.uint8)

        # 创建白色掩码（255, 255, 255）和黑色背景（0, 0, 0）
        result = np.zeros_like(image)
        result[int_mask == 1] = [255, 255, 255]  # 分割目标设为白色
        result[int_mask == 0] = [0, 0, 0]        # 背景设为黑色

        return result

    def _apply_original_mask(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        将原始对象掩码应用到图像上，分割目标为原始视频中的对象，背景为白色，不透明。

        参数:
            image (np.ndarray): 输入图像，形状为 (H, W, 3)。
            mask (np.ndarray): 二值掩码，形状为 (H, W)，1 表示前景，0 表示背景。

        返回:
            np.ndarray: 应用掩码后的图像，分割区域为原始对象，背景为白色。
        """
        # 将掩码转换为 uint8
        int_mask = mask.astype(np.uint8)

        # 创建结果图像，初始化为白色背景（255, 255, 255）
        result = np.full_like(image, [255, 255, 255])

        # 将掩码区域设置为原始图像的内容
        result[int_mask == 1] = image[int_mask == 1]

        return result

    def cleanup(self) -> None:
        """
        删除视频帧文件夹（保留掩码帧文件夹）。

        异常:
            OSError: 如果删除文件夹失败。
        """
        folders_to_delete = [self.original_frames_folder, self.frames_mask_dir, self.white_mask_dir]
        for folder in folders_to_delete:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    print(f"已删除文件夹: {folder}")
                except OSError as e:
                    print(f"删除文件夹 {folder} 失败: {e}")


    def _get_unique_output_path(self, output_path: str) -> str:
        """
        检查输出路径是否已存在，若存在则生成一个新的文件名。

        参数:
            output_path (str): 原始输出路径。

        返回:
            str: 不存在冲突的输出路径。
        """
        base, ext = os.path.splitext(output_path)
        counter = 1
        new_path = output_path
        while os.path.exists(new_path):
            new_path = f"{base}_{counter}{ext}"
            counter += 1
        return new_path

    def segment_with_points(self, points: np.ndarray, labels: np.ndarray, frame_idx: int = 0) -> None:
        """
        使用用户提供的点进行实例分割，存储分割结果。

        参数:
            points (np.ndarray): 分割点坐标，形状为 (N, 2)，每行为 [x, y]。
            labels (np.ndarray): 点标签，形状为 (N,)，1 表示前景，0 表示背景。
            frame_idx (int): 开始分割的帧索引，默认为 0。

        异常:
            ValueError: 如果未设置视频路径。
            FileNotFoundError: 如果帧文件不存在。
        """
        if not self.input_video_path:
            raise ValueError("必须使用 set_video_path 设置输入视频路径。")

        print(f"输入视频: {self.input_video_path}")

        # 提取视频帧
        self._extract_frames()

        # 初始化视频状态
        inference_state = self.predictor.init_state(video_path=self.original_frames_folder)

        # 添加分割点
        _, out_obj_ids, out_mask_logits = self.predictor.add_new_points(
            inference_state=inference_state,
            frame_idx=frame_idx,
            obj_id=1,
            points=points,
            labels=labels
        )

        # 将分割传播到整个视频
        self.video_segments = {}
        for out_frame_idx, out_obj_ids, out_mask_logits in self.predictor.propagate_in_video(inference_state):
            self.video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }

        print("实例分割完成，分割结果已存储。")

    def generate_colored_mask_video(self) -> None:
        """
        生成彩色掩码视频，保留原始背景，分割对象覆盖为彩色。

        异常:
            ValueError: 如果未进行分割或视频路径未设置。
            FileNotFoundError: 如果帧文件不存在。
        """
        if not self.output_video_path:
            raise ValueError("必须使用 set_video_path 设置输出视频路径。")
        if self.video_segments is None:
            raise ValueError("必须先调用 segment_with_points 进行实例分割。")

        print(f"生成彩色掩码视频，输出目录: {self.frames_mask_dir}")

        # 创建用于存储掩码帧的目录
        os.makedirs(self.frames_mask_dir, exist_ok=True)

        # 处理每一帧
        for out_frame_idx in range(len(self.frame_names)):
            frame_path = os.path.join(self.original_frames_folder, self.frame_names[out_frame_idx])
            if not os.path.exists(frame_path):
                raise FileNotFoundError(f"帧文件不存在: {frame_path}")

            image = cv2.imread(frame_path)
            if image is None:
                raise ValueError(f"无法读取帧: {frame_path}")

            color_num = 0
            for obj_id, mask in self.video_segments[out_frame_idx].items():
                print(f"处理帧 {out_frame_idx}: 图像形状={image.shape}, "
                      f"掩码形状={mask.shape}, 颜色索引={color_num}, 对象ID={obj_id}")
                image = self._apply_colored_mask(image, np.squeeze(mask), color_num)
                color_num += 1

            # 保存掩码帧
            output_path = os.path.join(self.frames_mask_dir, f"{out_frame_idx:05d}.jpg")
            cv2.imwrite(output_path, image)

        # 创建输出视频
        self._create_video_from_frames()

    def generate_white_mask_images(self) -> None:
        """
        生成黑白掩码图像，背景为黑色，分割对象为白色，保存为图片形式。

        异常:
            ValueError: 如果未进行分割或视频路径未设置。
            FileNotFoundError: 如果帧文件不存在。
        """
        if not self.output_video_path:
            raise ValueError("必须使用 set_video_path 设置输出视频路径。")
        if self.video_segments is None:
            raise ValueError("必须先调用 segment_with_points 进行实例分割。")

        print(f"生成黑白掩码图像，输出目录: {self.white_mask_dir}")

        # 创建用于存储黑白掩码图像的目录
        os.makedirs(self.white_mask_dir, exist_ok=True)

        # 处理每一帧
        for out_frame_idx in range(len(self.frame_names)):
            frame_path = os.path.join(self.original_frames_folder, self.frame_names[out_frame_idx])
            if not os.path.exists(frame_path):
                raise FileNotFoundError(f"帧文件不存在: {frame_path}")

            image = cv2.imread(frame_path)
            if image is None:
                raise ValueError(f"无法读取帧: {frame_path}")

            for obj_id, mask in self.video_segments[out_frame_idx].items():
                print(f"处理帧 {out_frame_idx}: 图像形状={image.shape}, "
                      f"掩码形状={mask.shape}, 对象ID={obj_id}")
                image = self._apply_white_mask(image, np.squeeze(mask))

            # 保存黑白掩码图像
            output_path = os.path.join(self.white_mask_dir, f"{out_frame_idx:05d}.jpg")
            cv2.imwrite(output_path, image)

        print(f"黑白掩码图像已保存到: {self.white_mask_dir}")

    def generate_original_mask_images(self) -> None:
        """
        生成原始对象掩码图像，背景为白色，分割对象为原始视频中的目标，保存为图片形式。

        异常:
            ValueError: 如果未进行分割或视频路径未设置。
            FileNotFoundError: 如果帧文件不存在。
        """
        if not self.output_video_path:
            raise ValueError("必须使用 set_video_path 设置输出视频路径。")
        if self.video_segments is None:
            raise ValueError("必须先调用 segment_with_points 进行实例分割。")

        print(f"生成原始对象掩码图像，输出目录: {self.original_mask_dir}")

        # 创建用于存储原始对象掩码图像的目录
        os.makedirs(self.original_mask_dir, exist_ok=True)

        # 处理每一帧
        for out_frame_idx in range(len(self.frame_names)):
            frame_path = os.path.join(self.original_frames_folder, self.frame_names[out_frame_idx])
            if not os.path.exists(frame_path):
                raise FileNotFoundError(f"帧文件不存在: {frame_path}")

            image = cv2.imread(frame_path)
            if image is None:
                raise ValueError(f"无法读取帧: {frame_path}")

            for obj_id, mask in self.video_segments[out_frame_idx].items():
                print(f"处理帧 {out_frame_idx}: 图像形状={image.shape}, "
                      f"掩码形状={mask.shape}, 对象ID={obj_id}")
                image = self._apply_original_mask(image, np.squeeze(mask))

            # 保存原始对象掩码图像
            output_path = os.path.join(self.original_mask_dir, f"{out_frame_idx:05d}.jpg")
            cv2.imwrite(output_path, image)

        print(f"原始对象掩码图像已保存到: {self.original_mask_dir}")

    def _create_video_from_frames(self, framerate: int = 30, codec: str = 'libx264', pix_fmt: str = 'yuv420p') -> None:
        """
        使用 FFmpeg 从掩码帧创建视频。

        参数:
            framerate (int): 输出视频的帧率，默认为 30。
            codec (str): 使用的视频编码器，默认为 'libx264'。
            pix_fmt (str): 像素格式，默认为 'yuv420p'。

        异常:
            subprocess.CalledProcessError: 如果 FFmpeg 命令执行失败。
        """
        # 检查并获取无冲突的输出路径
        final_output_path = self._get_unique_output_path(self.output_video_path)

        command = [
            'ffmpeg',
            '-framerate', str(framerate),
            '-i', os.path.join(self.frames_mask_dir, '%05d.jpg'),
            '-c:v', codec,
            '-pix_fmt', pix_fmt,
            final_output_path
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"视频已成功创建: {final_output_path}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg 执行失败: {e.stderr}")
            raise

if __name__ == "__main__":
    # 示例用法
    checkpoint = "D:\GitHub\sitp-bronze96\models\sam2.1_hiera_tiny.pt"
    model_cfg = "D:\GitHub\sitp-bronze96\models\sam2.1_hiera_t.yaml"

    input_video = r"D:\test1\video016.mp4"
    output_video = r"./result.mp4"

    # 初始化模型
    model = SAM2InstanceSegmentationModel(model_cfg, checkpoint)
    model.set_video_path(input_video, output_video)

    # 执行实例分割
    points = np.array([[100, 600]], dtype=np.float32)
    labels = np.array([1], dtype=np.int32)
    model.segment_with_points(points, labels)

    # 生成彩色掩码视频
    model.generate_colored_mask_video()

    # 生成黑白掩码图像
    model.generate_white_mask_images()

    # 生成原始对象掩码图像
    model.generate_original_mask_images()

    # 手动清理 original_frames（可选）
    model.cleanup()