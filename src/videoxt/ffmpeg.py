"""FFmpeg 操作封装模块。

此模块封装了所有与 FFmpeg 相关的操作，包括视频元数据获取、关键帧提取等。
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import ffmpeg
from ffmpeg.nodes import Stream

from .models import AudioSegment, KeyframeInfo, VideoMetadata


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

    def extract_keyframes(self, output_dir: Path, start_time: float, end_time: float) -> List[KeyframeInfo]:
        """提取指定时间段的关键帧。

        Args:
            output_dir: 输出目录
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）

        Returns:
            List[KeyframeInfo]: 关键帧信息列表

        Raises:
            FFmpegError: 当提取失败时抛出
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        keyframes: List[KeyframeInfo] = []

        try:
            # 使用 ffmpeg 提取关键帧
            stream = (
                ffmpeg
                .input(str(self.video_path), ss=start_time, t=end_time-start_time)
                .filter('select', 'eq(pict_type,I)')
                .output(str(output_dir / 'frame_%d.png'), vsync='0')
                .overwrite_output()
                .global_args('-loglevel', 'error')
            )

            # 执行命令并获取输出
            process = stream.run_async(pipe_stdout=True, pipe_stderr=True)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise FFmpegError(f"提取关键帧失败: {stderr.decode()}")

            # 解析输出获取关键帧信息
            for frame_file in sorted(output_dir.glob('frame_*.png')):
                frame_num = int(frame_file.stem.split('_')[1])
                pts = start_time + (frame_num / self.get_metadata()['fps'])
                keyframes.append(KeyframeInfo(
                    pts=pts,
                    frame_type='I',
                    file_path=frame_file,
                    quality=1.0  # 默认质量分数
                ))

            return keyframes
        except Exception as e:
            raise FFmpegError(f"提取关键帧失败: {str(e)}")

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