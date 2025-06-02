import requests
import json
import time

API_KEY = "xxxxx"#这里需要修改成自己的api-key

def submit_video_task():
    video_url = "https://videos.pexels.com/video-files/31521163/13436601_2560_1440_60fps.mp4"
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "X-DashScope-Async": "enable",
        "X-DashScope-DataInspection": "enable"
    }
    payload = {
        "model": "video-style-transform",
        "input": {"video_url": video_url},
        "parameters": {"style": 0, "video_fps": 15}
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print("提交任务响应：")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        try:
            print("错误信息：", response.json().get("message", "无详细错误信息"))
        except Exception:
            print("无法解析错误信息")
        return None

    task_id = response.json().get("output", {}).get("task_id")
    return task_id

def poll_task_status(task_id, interval=10):
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    i=1
    while(True):
        response = requests.get(url, headers=headers)
        try:
            result = response.json()
        except Exception:
            print("任务状态响应解析失败：", response.text)
            return None

        print(f"第{i}次轮询响应：")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        i+=1

        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}")
            try:
                print("错误信息：", result.get("message", "无详细错误信息"))
            except Exception:
                print("无法解析错误信息")
            return None

        status = result.get("output", {}).get("task_status", "")
        if status == "SUCCEEDED":
            print("任务成功完成！")
            return result
        elif status == "FAILED":
            print("任务执行失败。")
            return None
        else:
            time.sleep(interval)

if __name__ == "__main__":
    task_id = submit_video_task()
    if task_id:
        poll_task_status(task_id)
