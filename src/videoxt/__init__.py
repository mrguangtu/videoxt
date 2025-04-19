"""视频关键帧提取工具。

此包提供了高效的视频关键帧提取和音视频对齐功能。
"""

__version__ = "0.1.0"

from .controllers import ExtractionConfig, VideoExtractor
from .models import (
    AudioSegment,
    ExtractionResult,
    ExtractionTask,
    KeyframeInfo,
    VideoMetadata,
)

# 导出GUI相关接口
from .gui import VideoExtractorGUI, main as gui_main

__all__ = [
    "ExtractionConfig",
    "VideoExtractor",
    "AudioSegment",
    "ExtractionResult",
    "ExtractionTask",
    "KeyframeInfo",
    "VideoMetadata",
    "VideoExtractorGUI",
    "gui_main",
] 