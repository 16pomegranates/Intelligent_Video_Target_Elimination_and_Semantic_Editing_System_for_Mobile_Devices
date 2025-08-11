import numpy as np
import cv2

from ultralytics import YOLO

# ---------------------------- 目标跟踪类 ----------------------------
class ObjectTracker:
    def __init__(self):
        self.track_ids = {}
        self.next_id = {}
        self.tracked_boxes = {}

    def update(self, detections):
        current_ids = []
        for detection in detections:
            cls, box, id = detection
            current_ids.append(id)

            cls_name = cls
            if cls_name not in self.track_ids:
                self.track_ids[cls_name] = {}
                self.next_id[cls_name] = 1

            if id in self.tracked_boxes:
                self.tracked_boxes[id] = box
            else:
                unique_id = self.next_id[cls_name]
                self.track_ids[cls_name][id] = unique_id
                self.tracked_boxes[id] = box
                self.next_id[cls_name] += 1
        return current_ids


# ---------------------------- 视频处理器类 ----------------------------
class VideoProcessor:
    def __init__(self):
    ##########################################需要改成自己电脑上的路径
        self.model = YOLO(r"..\models\yolov8n-seg.pt")
        self.names = self.model.model.names
        self.track_ids = {}
        self.next_id = {}
        self.tracked_boxes = {}

    def process_video(self, video_path, video_id):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error(f"无法打开视频文件：{video_path}")
            return None

        w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
        
        results = {
            'frames': [],
            'masks': {},
            'original_path': video_path,
            'fps': fps,
            'resolution': (w, h)
        }

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results['frames'].append(frame_rgb)
            tracked = self.track_objects(frame_rgb)
            
            for obj in tracked:
                cls_name, obj_id, mask = obj
                key = f"{video_id}_{cls_name}_{obj_id}"
                if key not in results['masks']:
                    results['masks'][key] = []
                results['masks'][key].append(mask)

        cap.release()
        return results

    def track_objects(self, frame):
        results = self.model.track(frame, persist=True, tracker='bytetrack.yaml')
        detections = []
        
        if results[0].masks is not None and results[0].boxes.id is not None:
            clss = results[0].boxes.cls.cpu().tolist()
            ids = results[0].boxes.id.cpu().tolist()
            masks = results[0].masks.xy
            
            for mask, cls, obj_id in zip(masks, clss, ids):
                cls_name = self.names[int(cls)]
                if cls_name not in self.track_ids:
                    self.track_ids[cls_name] = {}
                    self.next_id[cls_name] = 1
                
                if obj_id not in self.track_ids[cls_name]:
                    self.track_ids[cls_name][obj_id] = self.next_id[cls_name]
                    self.next_id[cls_name] += 1
                
                unique_id = self.track_ids[cls_name][obj_id]
                detections.append((cls_name, unique_id, mask))
        
        return detections