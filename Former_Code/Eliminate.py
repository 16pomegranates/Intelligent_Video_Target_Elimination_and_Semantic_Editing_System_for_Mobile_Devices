import cv2
import os
import subprocess
import torch
import requests
import numpy as np

from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from ToolClasses import ObjectTracker

def describe_object(image):
    model_path = r"D:\models\blip2-opt-2.7b"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    processor = Blip2Processor.from_pretrained(model_path)
    model = Blip2ForConditionalGeneration.from_pretrained(
        model_path, torch_dtype=torch.float16
    )
    model.to(device)
    inputs = processor(images=image, return_tensors="pt").to(device, torch.float16)

    generated_ids = model.generate(**inputs)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    print(generated_text)
    return generated_text

# 针对当前帧处理目标描述（每个目标只处理一次）
def process_and_describe_targets(im0, masks, clss, ids, target_classes, tracker, processed_ids, id_mapping, names):
    """
    遍历当前帧中的所有检测目标：
      - 如果目标类别在 target_classes 中
      - 并且由 tracker 分配的唯一 track_id 未被处理过
    则裁剪目标区域并调用 BLIP2 生成描述，将 (track_id, description) 存入 id_mapping
    并将 track_id 加入 processed_ids 集合，确保同一目标只处理一次。
    """
    min_area = 500  # 根据需要调整面积阈值
    for mask, cls, raw_id in zip(masks, clss, ids):
        cls_name = names[int(cls)]
        if cls_name not in target_classes:
            continue
        track_id = tracker.track_ids[cls_name].get(int(raw_id), None)
        if track_id is None:
            continue
        if track_id not in processed_ids:
            x1, y1 = mask[:, 0].min(), mask[:, 1].min()
            x2, y2 = mask[:, 0].max(), mask[:, 1].max()
            area = (x2 - x1) * (y2 - y1)
            if area > min_area:
                object_crop = im0[int(y1):int(y2), int(x1):int(x2)]
                if object_crop.size > 0:
                    object_pil = Image.fromarray(cv2.cvtColor(object_crop, cv2.COLOR_BGR2RGB))
                    #description = describe_object(object_pil)
                    description = "[描述已禁用]"
                    id_mapping[int(raw_id)] = (track_id, description)
                    processed_ids.add(track_id)

def instance_segmentation(originalVideoDir, outputDir, targetClasses):
    """
    执行实例分割并返回推理结果。
    """

    model_yolo = YOLO(r"..\models\yolov8n-seg.pt")
    names = model_yolo.model.names
    cap = cv2.VideoCapture(originalVideoDir)
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    
    output_dir = outputDir
    os.makedirs(output_dir, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter(os.path.join(output_dir, 'instance_segmentation_output.mp4'), fourcc, fps, (w, h))
    tracker = ObjectTracker()

    detected_ids = set()       # 用于绘制检测框的集合
    all_results = []           # 存储所有帧的推理结果
    id_mapping = {}            # 存储原始ID -> (track_id, description)
    processed_ids = set()      # 记录已处理的 track_id，确保每个目标只处理一次

    first_frame_object_images = []  # 存储第一帧中每个目标的 (唯一标识, 图片, 描述)
    frame_count = 0

    while True:
        ret, im0 = cap.read()
        if not ret:
            print("Video frame is empty or video processing has been successfully completed.")
            break

        # 复制原始帧 im0
        im0_original = im0.copy()

        annotator = Annotator(im0, line_width=2)
        results = model_yolo.track(im0, persist=True)  # 仅推理一次
        all_results.append(results)  # 存储推理结果

        if results[0].masks is not None and results[0].boxes.id is not None:
            clss = results[0].boxes.cls.cpu().tolist()
            ids = results[0].boxes.id.cpu().tolist()
            masks = results[0].masks.xy
            detections = []

            # 构建检测列表供 tracker 更新
            for mask, cls, raw_id in zip(masks, clss, ids):
                cls_name = names[int(cls)]
                if cls_name not in targetClasses:
                    continue
                box = results[0].boxes.xyxy.cpu().numpy().tolist()
                detections.append((names[int(cls)], box, int(raw_id)))
            tracker.update(detections)

            # 对当前帧中尚未处理过的目标生成描述（模型调用部分已禁用）
            process_and_describe_targets(im0, masks, clss, ids, targetClasses, tracker, processed_ids, id_mapping, names)

            # 绘制检测框和标签，并在第一帧保存目标截图供前端展示
            for mask, cls, raw_id in zip(masks, clss, ids):
                cls_name = names[int(cls)]
                if cls_name not in targetClasses:
                    continue

                track_id = tracker.track_ids[cls_name].get(int(raw_id), None)
                if track_id is None:
                    continue

                unique_id = f"{cls_name} {track_id}"
                detected_ids.add(unique_id) 
                color = colors(int(cls), True)
                txt_color = (0, 0, 0)
                mask_points = mask.astype(np.int32).reshape((-1, 1, 2))
                annotator.seg_bbox(mask=mask, mask_color=color)
                x1, y1 = mask_points.min(axis=0).squeeze()
                x2, y2 = mask_points.max(axis=0).squeeze()
                annotator.box_label((x1, y1, x2, y2), unique_id, color=txt_color)

                expand_size = 50

                y1_new = max(0, y1 - expand_size)
                y2_new = min(im0_original.shape[0], y2 + expand_size)
                x1_new = max(0, x1 - expand_size)
                x2_new = min(im0_original.shape[1], x2 + expand_size)

                # 仅在第一帧保存目标截图、名称及描述
                if frame_count == 0:
                    object_crop = im0_original[int(y1_new):int(y2_new), int(x1_new):int(x2_new)]
                    if object_crop.size > 0:
                        object_pil = Image.fromarray(cv2.cvtColor(object_crop, cv2.COLOR_BGR2RGB))
                        # 若 id_mapping 中已有对应描述则使用，否则默认描述

                       
                        if int(raw_id) in id_mapping:
                            desc = id_mapping[int(raw_id)][1]
                        # desc = describe_object(object_pil)
                        desc = "[描述已禁用]"
                        first_frame_object_images.append((unique_id, object_pil, desc))

        out.write(im0)
        frame_count += 1

    cap.release()
    out.release()
    print("Detected IDs:", detected_ids)  # 打印列表

    # 输出检测目标描述信息
    print("Detected IDs and their descriptions:")
    for obj_id, (track_id, description) in id_mapping.items():
        print(f"Object ID {obj_id} (Track ID {track_id}): {description}")

    # 返回检测到的目标ID、所有结果、ID映射以及第一帧的目标截图（包含名称和描述）
    print("id_mapping:----------",id_mapping)
    print(type(id_mapping))
    return detected_ids, all_results, id_mapping, first_frame_object_images

def mask_segmentation(all_results, originalVideoDir, output_dir, framesOutputDir, selected_ids, id_mapping):
    """
    使用实例分割阶段的推理结果，执行掩码过滤。
    """

    model = YOLO(r"..\models\yolov8n-seg.pt")
    names = model.model.names
    cap = cv2.VideoCapture(originalVideoDir)
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    print(f"\n\noutput_dir: {output_dir},\n\n framesOutputDir: {framesOutputDir}") 
    frames_output_dir = os.path.join(output_dir, framesOutputDir)
    os.makedirs(frames_output_dir, exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter(os.path.join(output_dir, 'mask_segmentation_output.mp4'), fourcc, fps, (w, h))
    
    frame_count = 0

    for results in all_results:
        ret, im0 = cap.read()
        if not ret:
            break
    
        mask_im0 = np.zeros(im0.shape, dtype=np.uint8)

        if results[0].masks is not None:
            clss = results[0].boxes.cls.cpu().tolist()
            ids = results[0].boxes.id.cpu().tolist()
            masks = results[0].masks.xy
            
            for mask, cls, id in zip(masks, clss, ids):
                cls_name = names[int(cls)]
                nid = id_mapping.get(id, None)
                obj_id_str = f"{cls_name} {nid}"
                parts = obj_id_str.split('(')
                if len(parts) > 1:
                    number = str({parts[1].split(',')[0]})[2:-2]
                    obj_id_str = f"{cls_name} {number}"

                # 检查是否在用户选择的ID列表中
                if obj_id_str in selected_ids:

                    mask_points = mask.astype(np.int32).reshape(-1, 1, 2)
                    cv2.fillPoly(mask_im0, [mask_points], (255, 255, 255), cv2.LINE_AA)

        out.write(mask_im0)
        frame_filename = os.path.join(frames_output_dir, f"{frame_count:05d}.png")
        cv2.imwrite(frame_filename, mask_im0)
        frame_count += 1

    cap.release()
    out.release()
    print("Mask segmentation completed.")