import os
import cv2
import torch
import numpy as np
from ultralytics import solutions
from ultralytics.utils.plotting import colors
from ultralytics.solutions.solutions import BaseSolution, SolutionAnnotator

device = "cuda" if torch.cuda.is_available() else "cpu"

class InstanceSegmentationModel:
    def __init__(self,target_classes=None):
        self.__model__ = solutions.InstanceSegmentation(
            model="yolo11n-seg.pt", 
            device=device,
            show=False,
            verbose=False,
            )
        
        self.__all_results__ = []
        self.__object_counter__ = {}
        self.track_id_dict = {}

    def set_video(self, original_video_path, output_video_path):
        self.original_video_path = original_video_path
        self.output_video_path = output_video_path
        # 重置计数器
        self.__object_counter__ = {}
        self.track_id_dict = {}

    def __read_video__(self):
        # 读取视频信息
        self.frame_count = 0
        self.cap = cv2.VideoCapture(self.original_video_path)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 重置视频到第一帧
        assert self.cap.isOpened(), "Error reading video file"
        self.w, self.h, self.fps = (int(self.cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
        
        os.makedirs(self.output_video_path, exist_ok=True)
        
    def instance_segmentation(self):
        self.__read_video__()
        self.__all_results__ = []
        video_writer = cv2.VideoWriter(os.path.join(self.output_video_path, 'instance_segmentation.mp4'), cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (self.w, self.h))

        while self.cap.isOpened():
            success, im0 = self.cap.read()
            if not success:
                print("Video frame is empty or video processing has been successfully completed.")
                break

            self.__model__.extract_tracks(im0)
            frame_result = {
                'im0': im0.copy(),
                'clss': self.__model__.clss.copy() if hasattr(self.__model__, 'clss') else [],
                'track_ids': self.__model__.track_ids.copy() if hasattr(self.__model__, 'track_ids') else [],
                'masks': [mask.copy() for mask in self.__model__.masks] if hasattr(self.__model__, 'masks') else []
            }
            self.__all_results__.append(frame_result)

            annotator = SolutionAnnotator(im0, line_width=2)
            if self.__model__.masks is not None:
                for cls, t_id, mask in zip(self.__model__.clss, self.__model__.track_ids, self.__model__.masks):
                    # 统计每个类别的实例数量
                    class_name = self.__model__.names[cls]
                    if class_name not in self.__object_counter__:
                        self.__object_counter__[class_name] = 0
                    if t_id not in self.track_id_dict:
                        self.__object_counter__[class_name] += 1
                        self.track_id_dict[t_id] = f"{class_name} {self.__object_counter__[class_name]}"

                    # 获取掩码的边界框并扩大
                    x1, y1 = mask.min(axis=0).squeeze()
                    x2, y2 = mask.max(axis=0).squeeze()
                    expand_size = 50
                    y1_new = max(0, y1 - expand_size)
                    y2_new = min(im0.shape[0], y2 + expand_size)
                    x1_new = max(0, x1 - expand_size)
                    x2_new = min(im0.shape[1], x2 + expand_size)

                    # 绘制掩码
                    annotator.segmentation_mask(mask=mask, mask_color=colors(t_id, True), label=self.track_id_dict[t_id], alpha=0.5)

            # 保存视频
            plot_im = annotator.result()
            video_writer.write(plot_im)

        self.cap.release()
        self.__model__.display_output(plot_im)
        video_writer.release()
        
    def mask_generation(self,selected_ids):
        if self.track_id_dict is None:
            error_msg = "Please run instance_segmentation() first to generate track_id_dict."
            raise ValueError(error_msg)

        frames_output_dir = os.path.join(self.output_video_path, "frames_mask")
        os.makedirs(frames_output_dir, exist_ok=True)  
        self.__read_video__()
       
        video_writer = cv2.VideoWriter(os.path.join(self.output_video_path, 'mask_generation.mp4'), cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (self.w, self.h))
        
        frame_count = 0

        for frame_count, result in enumerate(self.__all_results__):
            mask_im0 = np.zeros(result['im0'].shape, dtype=np.uint8)
            
            if result['masks']:
                for cls, t_id, mask in zip(result['clss'], result['track_ids'], result['masks']):
                    target_id = self.track_id_dict[t_id]
                    
                    if target_id in selected_ids:
                        mask_points = mask.astype(np.int32).reshape(-1, 1, 2)
                        cv2.fillPoly(mask_im0, [mask_points], (255, 255, 255), cv2.LINE_AA)
            
            video_writer.write(mask_im0)
            frame_filename = os.path.join(frames_output_dir, f"{frame_count:05d}.png")
            cv2.imwrite(frame_filename, mask_im0)
            frame_count += 1

        self.cap.release()
        video_writer.release()

    
        
        
# # 使用示例
# __model__ = InstanceSegmentationModel()

# __model__.set_video(original_video_path=r'D:\test1\video016.mp4', output_video_path='..')
# __model__.instance_segmentation()  # 执行实例分割
# __model__.mask_generation(selected_ids=['person 1'])
