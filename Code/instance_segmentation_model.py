import os
import cv2
import torch
import numpy as np
from typing import List, Dict, Optional, Tuple
from ultralytics import solutions
from ultralytics.utils.plotting import colors
from ultralytics.solutions.solutions import BaseSolution, SolutionAnnotator


class InstanceSegmentationModel:
    """用于视频实例分割和掩码生成的模型类，基于Ultralytics YOLO。"""

    def __init__(self, model_path: str = "../models/yolo11n-seg.pt", target_classes: Optional[List[str]] = None):
        """
        初始化实例分割模型。

        参数:
            model_path (str): 预训练模型文件路径，默认为"models\yolo11n-seg.pt"。
            target_classes (Optional[List[str]]): 目标类别列表，若为空则检测所有类别。

        异常:
            RuntimeError: 如果CUDA请求但不可用。
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = solutions.InstanceSegmentation(
            model=model_path,
            device=self.device,
            show=False,
            verbose=False,
        )
        self.results = []
        self.object_counter: Dict[str, int] = {}
        self.track_id_dict: Dict[int, str] = {}
        self.original_video_path: Optional[str] = None
        self.output_video_path: Optional[str] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_width: Optional[int] = None
        self.frame_height: Optional[int] = None
        self.fps: Optional[float] = None

    def set_video(self, original_video_path: str, output_video_path: str) -> None:
        """
        设置输入和输出视频路径，并初始化相关参数。

        参数:
            original_video_path (str): 输入视频文件路径。
            output_video_path (str): 输出视频和掩码帧的保存目录。

        异常:
            FileNotFoundError: 如果输入视频文件不存在。
        """
        self.original_video_path = original_video_path
        self.output_video_path = output_video_path
        self.object_counter = {}
        self.track_id_dict = {}

        if not os.path.exists(original_video_path):
            raise FileNotFoundError(f"输入视频文件不存在: {original_video_path}")

    def _initialize_video_capture(self) -> None:
        """初始化视频捕获并获取视频属性。"""
        self.cap = cv2.VideoCapture(self.original_video_path)
        if not self.cap.isOpened():
            raise AssertionError("无法打开视频文件")
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        os.makedirs(self.output_video_path, exist_ok=True)

    def _release_video_resources(self) -> None:
        """释放视频捕获和写入资源。"""
        if self.cap is not None:
            self.cap.release()
        self.cap = None

    def _create_video_writer(self, output_filename: str) -> cv2.VideoWriter:
        """
        创建视频写入器。

        参数:
            output_filename (str): 输出视频文件名。

        返回:
            cv2.VideoWriter: 配置好的视频写入器。
        """
        output_path = os.path.join(self.output_video_path, output_filename)
        fourcc = cv2.VideoWriter_fourcc(*"X","2","6","4")
        return cv2.VideoWriter(output_path, fourcc, self.fps, (self.frame_width, self.frame_height))

    def instance_segmentation(self) -> None:
        """
        执行实例分割，生成带有彩色掩码的视频。

        输出:
            - 保存分割视频到 output_video_path/instance_segmentation.mp4
            - 存储分割结果到 self.results

        异常:
            AssertionError: 如果视频文件无法打开。
        """
        self._initialize_video_capture()
        self.results = []
        video_writer = self._create_video_writer("instance_segmentation.mp4")

        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                print("视频帧为空或处理已完成。")
                break

            self.model.extract_tracks(frame)
            frame_result = {
                "frame": frame.copy(),
                "classes": self.model.clss.copy() if hasattr(self.model, "clss") else [],
                "track_ids": self.model.track_ids.copy() if hasattr(self.model, "track_ids") else [],
                "masks": [mask.copy() for mask in self.model.masks] if hasattr(self.model, "masks") else [],
            }
            self.results.append(frame_result)

            annotator = SolutionAnnotator(frame, line_width=2)
            if hasattr(self.model, "masks") and self.model.masks:
                for cls, track_id, mask in zip(self.model.clss, self.model.track_ids, self.model.masks):
                    class_name = self.model.names[cls]
                    if class_name not in self.object_counter:
                        self.object_counter[class_name] = 0
                    if track_id not in self.track_id_dict:
                        self.object_counter[class_name] += 1
                        self.track_id_dict[track_id] = f"{class_name} {self.object_counter[class_name]}"

                    annotator.segmentation_mask(
                        mask=mask,
                        mask_color=colors(track_id, True),
                        label=self.track_id_dict[track_id],
                        alpha=0.5,
                    )

            plot_frame = annotator.result()
            video_writer.write(plot_frame)

        self.model.display_output(plot_frame)
        video_writer.release()
        self._release_video_resources()

    def mask_generation(self, selected_ids: List[str]) -> None:
        """
        为指定跟踪ID生成黑白掩码视频和帧图像。

        参数:
            selected_ids (List[str]): 需要生成掩码的跟踪ID列表（例如，['person 1']）。

        输出:
            - 保存黑白掩码视频到 output_video_path/mask_generation.mp4
            - 保存黑白掩码帧到 output_video_path/frames_mask/*.png

        异常:
            ValueError: 如果未运行 instance_segmentation 或 selected_ids 无效。
            AssertionError: 如果视频文件无法打开。
        """
        if not self.track_id_dict:
            raise ValueError("请先运行 instance_segmentation 以生成 track_id_dict。")

        self._initialize_video_capture()
        frames_output_dir = os.path.join(self.output_video_path, "frames_mask")
        os.makedirs(frames_output_dir, exist_ok=True)
        video_writer = self._create_video_writer("mask_generation.mp4")

        for frame_idx, result in enumerate(self.results):
            mask_frame = np.zeros_like(result["frame"], dtype=np.uint8)

            if result["masks"]:
                for cls, track_id, mask in zip(result["classes"], result["track_ids"], result["masks"]):
                    target_id = self.track_id_dict.get(track_id)
                    if target_id in selected_ids:
                        mask_points = mask.astype(np.int32).reshape(-1, 1, 2)
                        cv2.fillPoly(mask_frame, [mask_points], (255, 255, 255), cv2.LINE_AA)

            video_writer.write(mask_frame)
            frame_filename = os.path.join(frames_output_dir, f"{frame_idx:05d}.png")
            cv2.imwrite(frame_filename, mask_frame)

        video_writer.release()
        self._release_video_resources()
        print(f"黑白掩码图像已保存到: {frames_output_dir}")
        print(f"黑白掩码视频已保存到: {os.path.join(self.output_video_path, 'mask_generation.mp4')}")


if __name__ == "__main__":
    # 示例用法
    model = InstanceSegmentationModel()
    model.set_video(
        original_video_path=r"D:\test1\video016.mp4",
        output_video_path="output",
    )
    model.instance_segmentation()
    model.mask_generation(selected_ids=["person 1"])