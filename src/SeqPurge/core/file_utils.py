import os
import re
from typing import List
import shutil

def get_segment_dirs(root_dir: str) -> List[str]:
    """获取所有分段目录，按时间顺序排序"""
    segment_dirs = []
    for item in os.listdir(root_dir):
        path = os.path.join(root_dir, item)
        if os.path.isdir(path) and item.startswith("segment_"):
            try:
                # 从目录名中提取时间信息
                start_time, end_time = map(float, item.split("_")[1:])
                segment_dirs.append((path, start_time))
            except (ValueError, IndexError):
                continue
                
    # 按开始时间排序
    segment_dirs.sort(key=lambda x: x[1])
    return [dir_path for dir_path, _ in segment_dirs]

def get_sorted_frames(segment_dir: str) -> List[str]:
    """获取排序后的帧文件列表"""
    frames = []
    for filename in os.listdir(segment_dir):
        if filename.startswith("frame_") and filename.endswith(".png"):
            try:
                # 提取帧号
                frame_num = int(filename.split("_")[1].split(".")[0])
                frames.append((filename, frame_num))
            except (ValueError, IndexError):
                continue
                
    # 按帧号排序
    frames.sort(key=lambda x: x[1])
    return [filename for filename, _ in frames]

def natural_sort_key(s: str) -> List[int]:
    """自然排序键函数"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def ensure_dir_exists(dir_path: str) -> None:
    """确保目录存在"""
    os.makedirs(dir_path, exist_ok=True)

def safe_remove(path: str) -> None:
    """安全删除文件"""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"删除文件失败: {path}, 错误: {str(e)}")

def safe_copy(src: str, dst: str) -> None:
    """安全复制文件"""
    try:
        shutil.copy2(src, dst)
    except Exception as e:
        print(f"复制文件失败: {src} -> {dst}, 错误: {str(e)}") 