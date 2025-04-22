"""FFmpeg 操作封装模块。

此模块封装了所有与 FFmpeg 相关的操作，包括视频元数据获取、关键帧提取等。
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import ffmpeg
from ffmpeg.nodes import Stream

from .models import AudioSegment, KeyframeInfo, VideoMetadata, ExtractionTask


class FFmpegError(Exception):
    """FFmpeg 操作异常。"""
    pass


class FFmpegWrapper:
    """FFmpeg 操作封装类。"""

    def __init__(self, video_path: Path):
        """初始化 FFmpeg 封装类。

        Args:
            video_path: 视频文件路径
        """
        self.video_path = video_path
        self._metadata: Optional[VideoMetadata] = None

    def get_metadata(self) -> VideoMetadata:
        """获取视频元数据。

        Returns:
            VideoMetadata: 视频元数据信息

        Raises:
            FFmpegError: 当无法获取元数据时抛出
        """
        if self._metadata is not None:
            return self._metadata

        try:
            probe = ffmpeg.probe(str(self.video_path))
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)

            self._metadata = VideoMetadata(
                duration=float(probe['format']['duration']),
                width=int(video_info['width']),
                height=int(video_info['height']),
                fps=eval(video_info['r_frame_rate']),  # 如 "30000/1001"
                audio_codec=audio_info['codec_name'] if audio_info else 'none',
                video_codec=video_info['codec_name'],
                total_frames=int(video_info.get('nb_frames', 0))
            )
            return self._metadata
        except Exception as e:
            raise FFmpegError(f"获取视频元数据失败: {str(e)}")

    def extract_keyframes(self, output_dir: Path, start_time: float, end_time: float, interval_seconds: float = 0.5) -> List[KeyframeInfo]:
        """提取指定时间段的帧。

        Args:
            output_dir: 输出目录
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            interval_seconds: 提取帧的时间间隔（秒），默认0.5秒

        Returns:
            List[KeyframeInfo]: 帧信息列表

        Raises:
            FFmpegError: 当提取失败时抛出
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        frames: List[KeyframeInfo] = []

        try:
            # 获取视频帧率并计算帧间隔
            metadata = self.get_metadata()
            fps = metadata.fps
            frame_interval = int(fps * interval_seconds)  # 每隔多少帧提取一帧

            # 使用 ffmpeg 提取帧
            stream = (
                ffmpeg
                .input(str(self.video_path), ss=start_time, t=end_time-start_time)
                .filter('select', f'not(mod(n,{frame_interval}))')  # 按间隔提取帧
                .filter('setpts', 'N/FRAME_RATE/TB')  # 修正时间戳
                .output(str(output_dir / 'frame_%d.png'), 
                       vsync='1',                      # 使用 CFR 模式确保帧序
                       **{
                           'qscale:v': '1',           # 最高质量
                           'pix_fmt': 'rgb24'         # RGB24格式
                       })
                .overwrite_output()
                .global_args('-loglevel', 'error')
            )

            # 执行命令并获取输出
            process = stream.run_async(pipe_stdout=True, pipe_stderr=True)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise FFmpegError(f"提取帧失败: {stderr.decode()}")

            # 解析输出获取帧信息
            for frame_file in sorted(output_dir.glob('frame_*.png')):
                frame_num = int(frame_file.stem.split('_')[1])
                pts = start_time + (frame_num * interval_seconds)  # 使用间隔计算实际时间戳
                frames.append(KeyframeInfo(
                    pts=pts,
                    frame_type='F',  # 使用 'F' 表示这是按间隔提取的帧
                    file_path=frame_file,
                    quality=1.0  # 最高质量
                ))

            return frames
        except Exception as e:
            raise FFmpegError(f"提取帧失败: {str(e)}")

    def extract_audio(self, output_dir: Path, start_time: float, end_time: float) -> AudioSegment:
        """提取指定时间段的音频。

        Args:
            output_dir: 输出目录
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）

        Returns:
            AudioSegment: 音频片段信息

        Raises:
            FFmpegError: 当提取失败时抛出
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / f'audio_{start_time:.3f}_{end_time:.3f}.mp3'

        try:
            # 提取音频
            stream = (
                ffmpeg
                .input(str(self.video_path), ss=start_time, t=end_time-start_time)
                .output(str(audio_path), acodec='libmp3lame', loglevel='error')
                .overwrite_output()
            )
            stream.run(capture_stdout=True, capture_stderr=True)

            # 获取音频信息
            probe = ffmpeg.probe(str(audio_path))
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')

            return AudioSegment(
                start_time=start_time,
                end_time=end_time,
                file_path=audio_path,
                sample_rate=int(audio_info['sample_rate']),
                channels=int(audio_info['channels'])
            )
        except Exception as e:
            raise FFmpegError(f"提取音频失败: {str(e)}")

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
                interval_seconds=interval_seconds  # 添加这个参数
            ))
            
            current_time = end_time
            
        return tasks