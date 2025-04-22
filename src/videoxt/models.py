"""核心数据结构定义模块。

此模块定义了视频提取过程中使用的所有核心数据结构。
"""
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional, TypedDict, Union

import numpy as np


@dataclass
class VideoMetadata:
    """视频元数据信息。"""
    duration: float  # 视频时长（秒）
    width: int  # 视频宽度
    height: int  # 视频高度
    fps: float  # 帧率
    audio_codec: str  # 音频编码
    video_codec: str  # 视频编码
    total_frames: int  # 总帧数


@dataclass
class ExtractionTask:
    """视频提取任务定义。"""
    video_path: Path  # 视频文件路径
    start_time: float  # 开始时间（秒）
    end_time: float  # 结束时间（秒）
    output_dir: Path  # 输出目录
    task_id: str  # 任务ID
    interval_seconds: float  # 帧提取间隔（秒）


@dataclass
class KeyframeInfo:
    """关键帧信息。"""
    pts: float  # 显示时间戳
    frame_type: str  # 帧类型（I/P/B）
    file_path: Path  # 保存路径
    quality: float  # 图像质量分数


@dataclass
class AudioSegment:
    """音频片段信息。"""
    start_time: float  # 开始时间
    end_time: float  # 结束时间
    file_path: Path  # 音频文件路径
    sample_rate: int  # 采样率
    channels: int  # 声道数


@dataclass
class ExtractionResult:
    """提取结果。"""
    keyframes: List[KeyframeInfo]  # 关键帧列表
    audio_segments: List[AudioSegment]  # 音频片段列表
    metadata: VideoMetadata  # 视频元数据
    processing_time: timedelta  # 处理耗时
    error_log: Optional[Dict[str, str]] = None  # 错误日志 