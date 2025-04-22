"""并行任务调度模块。

此模块负责管理和调度视频处理任务，实现高效的并行处理。
"""
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from tqdm import tqdm

from .ffmpeg import FFmpegWrapper
from .models import AudioSegment, ExtractionResult, ExtractionTask, KeyframeInfo


@dataclass
class TaskResult:
    """任务处理结果。"""
    task_id: str
    keyframes: List[KeyframeInfo]
    audio_segment: AudioSegment
    error: Optional[str] = None


def process_segment(task: ExtractionTask) -> TaskResult:
    """处理视频片段。

    Args:
        task: 处理任务

    Returns:
        TaskResult: 处理结果
    """
    try:
        ffmpeg = FFmpegWrapper(task.video_path)
        output_dir = task.output_dir / f"segment_{task.task_id}"
        
        # 并行提取关键帧和音频
        keyframes = ffmpeg.extract_keyframes(
            output_dir,
            task.start_time,
            task.end_time,
            interval_seconds=task.interval_seconds
        )
        
        audio_segment = ffmpeg.extract_audio(
            output_dir,
            task.start_time,
            task.end_time
        )
        
        return TaskResult(
            task_id=task.task_id,
            keyframes=keyframes,
            audio_segment=audio_segment
        )
    except Exception as e:
        return TaskResult(
            task_id=task.task_id,
            keyframes=[],
            audio_segment=None,
            error=str(e)
        )


class TaskScheduler:
    """任务调度器。"""

    def __init__(self, n_workers: Optional[int] = None):
        """初始化调度器。

        Args:
            n_workers: 工作进程数，默认为CPU核心数
        """
        self.n_workers = n_workers or mp.cpu_count()

    def _split_tasks(self, video_path: Path, segment_duration: float = 30.0, interval_seconds: float = 0.5) -> List[ExtractionTask]:
        """将视频分割成多个处理任务。

        Args:
            video_path: 视频文件路径
            segment_duration: 每个片段的时长（秒）
            interval_seconds: 帧提取间隔（秒）

        Returns:
            List[ExtractionTask]: 任务列表
        """
        ffmpeg = FFmpegWrapper(video_path)
        metadata = ffmpeg.get_metadata()
        duration = metadata.duration
        
        tasks = []
        current_time = 0.0
        
        while current_time < duration:
            end_time = min(current_time + segment_duration, duration)
            task_id = f"{current_time:.1f}_{end_time:.1f}"
            
            tasks.append(ExtractionTask(
                video_path=video_path,
                start_time=current_time,
                end_time=end_time,
                output_dir=video_path.parent / "output",
                task_id=task_id,
                interval_seconds=interval_seconds
            ))
            
            current_time = end_time
            
        return tasks

    def process_video(self, video_path: Path, output_dir: Path, interval_seconds: float = 0.5) -> ExtractionResult:
        """处理整个视频。

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            interval_seconds: 帧提取间隔（秒），默认0.5秒

        Returns:
            ExtractionResult: 处理结果
        """
        from datetime import datetime
        start_time = datetime.now()
        
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 分割任务
        tasks = self._split_tasks(video_path, interval_seconds=interval_seconds)
        
        # 使用线程池并行处理
        results: List[TaskResult] = []
        with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            futures = [executor.submit(process_segment, task) for task in tasks]
            
            # 使用tqdm显示进度
            for future in tqdm(futures, total=len(tasks), desc="处理视频片段"):
                results.append(future.result())
        
        # 合并结果
        all_keyframes: List[KeyframeInfo] = []
        all_audio_segments: List[AudioSegment] = []
        error_log = {}
        
        for result in results:
            if result.error:
                error_log[result.task_id] = result.error
            else:
                all_keyframes.extend(result.keyframes)
                if result.audio_segment:
                    all_audio_segments.append(result.audio_segment)
        
        # 按时间戳排序
        all_keyframes.sort(key=lambda x: x.pts)
        all_audio_segments.sort(key=lambda x: x.start_time)
        
        return ExtractionResult(
            keyframes=all_keyframes,
            audio_segments=all_audio_segments,
            metadata=FFmpegWrapper(video_path).get_metadata(),
            processing_time=datetime.now() - start_time,
            error_log=error_log if error_log else None
        ) 