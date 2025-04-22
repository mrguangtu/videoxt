import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from .image_utils import ImageComparator
from .file_utils import get_sorted_frames, get_segment_dirs

class Deduplicator:
    def __init__(self, input_dir, output_dir, mode, threshold, algorithm, progress_callback, log_callback):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.mode = mode
        self.threshold = threshold
        self.algorithm = algorithm
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.stop_flag = False
        self.comparator = ImageComparator(algorithm, threshold)
        
    def process(self):
        try:
            # 获取所有分段目录
            segment_dirs = get_segment_dirs(self.input_dir)
            total_segments = len(segment_dirs)
            
            # 创建输出目录（如果需要）
            if self.mode in [2, 3]:
                os.makedirs(self.output_dir, exist_ok=True)
                
            # 处理每个分段
            for i, segment_dir in enumerate(segment_dirs):
                if self.stop_flag:
                    break
                    
                self.log_callback(f"处理分段: {os.path.basename(segment_dir)}")
                self._process_segment(segment_dir, i, total_segments)
                
            # 处理跨片段去重
            if not self.stop_flag and self.mode in [2, 3]:
                self._process_cross_segments(segment_dirs)
                
        except Exception as e:
            self.log_callback(f"处理过程中发生错误: {str(e)}")
            raise
            
    def _process_segment(self, segment_dir, segment_index, total_segments):
        # 获取排序后的帧列表
        frames = get_sorted_frames(segment_dir)
        if not frames:
            return
            
        # 计算进度
        progress = (segment_index / total_segments) * 100
        self.progress_callback(progress, f"处理分段 {segment_index + 1}/{total_segments}")
        
        # 处理帧序列
        keep_frames = []
        last_kept_frame = None
        
        for frame in frames:
            if self.stop_flag:
                break
                
            frame_path = os.path.join(segment_dir, frame)
            
            if last_kept_frame is None:
                # 保留第一帧
                keep_frames.append(frame)
                last_kept_frame = frame_path
            else:
                # 比较当前帧与上一保留帧
                if not self.comparator.is_similar(frame_path, last_kept_frame):
                    keep_frames.append(frame)
                    last_kept_frame = frame_path
                    
        # 根据模式处理结果
        if self.mode == 1:
            self._delete_redundant_frames(segment_dir, frames, keep_frames)
        elif self.mode in [2, 3]:
            self._copy_kept_frames(segment_dir, keep_frames, segment_index)
            
    def _process_cross_segments(self, segment_dirs):
        """全量扫描去重"""
        self.log_callback("开始全量跨片段去重...")
        
        # 从目标文件夹中获取所有文件
        all_frames = []
        for filename in os.listdir(self.output_dir):
            if filename.startswith("frame_") and filename.endswith(".png"):
                try:
                    # 解析文件名中的片段索引和帧号
                    parts = filename.split("_")
                    segment_idx = int(parts[1])
                    frame_num = int(parts[2].split(".")[0])
                    all_frames.append((filename, segment_idx, frame_num))
                except (ValueError, IndexError):
                    continue
                    
        # 按片段索引和帧号排序
        all_frames.sort(key=lambda x: (x[1], x[2]))
        
        if not all_frames:
            self.log_callback("没有找到需要处理的文件")
            return
            
        # 初始化基准帧
        keep_frames = []
        last_kept_frame = None
        
        # 遍历所有帧进行去重
        for frame_info in all_frames:
            if self.stop_flag:
                break
                
            filename, segment_idx, frame_num = frame_info
            current_frame = os.path.join(self.output_dir, filename)
            
            if last_kept_frame is None:
                # 保留第一帧
                keep_frames.append(filename)
                last_kept_frame = current_frame
            else:
                # 比较当前帧与上一保留帧
                if not self.comparator.is_similar(current_frame, last_kept_frame):
                    keep_frames.append(filename)
                    last_kept_frame = current_frame
                    
        # 删除冗余帧
        for frame_info in all_frames:
            filename, _, _ = frame_info
            if filename not in keep_frames:
                frame_path = os.path.join(self.output_dir, filename)
                os.remove(frame_path)
                self.log_callback(f"删除冗余帧: {filename}")
                
        self.log_callback(f"跨片段去重完成，保留 {len(keep_frames)} 帧，删除 {len(all_frames) - len(keep_frames)} 帧")
        
    def _delete_redundant_frames(self, segment_dir, all_frames, keep_frames):
        for frame in all_frames:
            if frame not in keep_frames:
                frame_path = os.path.join(segment_dir, frame)
                os.remove(frame_path)
                self.log_callback(f"删除冗余帧: {frame}")
                
    def _copy_kept_frames(self, segment_dir, keep_frames, segment_index):
        # 使用全局帧计数器
        global_frame_index = 1
        for frame in keep_frames:
            if self.stop_flag:
                break
                
            src_path = os.path.join(segment_dir, frame)
            # 使用更长的文件名格式，包含原始片段信息
            dst_name = f"frame_{segment_index:03d}_{global_frame_index:06d}.png"
            dst_path = os.path.join(self.output_dir, dst_name)
            
            shutil.copy2(src_path, dst_path)
            self.log_callback(f"复制帧: {frame} -> {dst_name}")
            global_frame_index += 1
            
    def stop(self):
        self.stop_flag = True
        self.log_callback("正在停止处理...") 