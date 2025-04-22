"""用户入口模块。

此模块提供了视频处理的主要接口，包括配置管理和任务执行。
"""
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

from .models import ExtractionResult
from .scheduler import TaskScheduler


@dataclass
class ExtractionConfig:
    """提取配置。"""
    segment_duration: float = 30.0  # 每个片段的时长（秒）
    n_workers: Optional[int] = None  # 工作进程数
    output_format: str = "png"  # 输出图像格式
    audio_format: str = "mp3"  # 输出音频格式
    quality: int = 95  # 输出质量（1-100）
    interval_seconds: float = 0.5  # 帧提取间隔（秒）


class VideoExtractor:
    """视频提取器。"""

    def __init__(self, config: Optional[Union[ExtractionConfig, Dict]] = None):
        """初始化提取器。

        Args:
            config: 提取配置，可以是ExtractionConfig实例或配置字典
        """
        if isinstance(config, dict):
            self.config = ExtractionConfig(**config)
        else:
            self.config = config or ExtractionConfig()
        
        self.scheduler = TaskScheduler(self.config.n_workers)

    def extract(
        self,
        video_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        config: Optional[Union[ExtractionConfig, Dict]] = None
    ) -> ExtractionResult:
        """提取视频内容。

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录，默认为视频所在目录下的output文件夹
            config: 可选的提取配置

        Returns:
            ExtractionResult: 提取结果
        """
        # 转换路径
        video_path = Path(video_path)
        if output_dir is None:
            output_dir = video_path.parent / "output"
        else:
            output_dir = Path(output_dir)

        # 更新配置
        if config is not None:
            if isinstance(config, dict):
                self.config = ExtractionConfig(**config)
            else:
                self.config = config

        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存配置
        config_path = output_dir / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.config.__dict__, f, indent=2)

        # 处理视频
        result = self.scheduler.process_video(
            video_path, 
            output_dir,
            interval_seconds=self.config.interval_seconds
        )

        # 保存处理报告
        report_path = output_dir / "report.json"
        report = {
            "video_path": str(video_path),
            "output_dir": str(output_dir),
            "config": self.config.__dict__,
            "processing_time": str(result.processing_time),
            "total_keyframes": len(result.keyframes),
            "total_audio_segments": len(result.audio_segments),
            "error_count": len(result.error_log) if result.error_log else 0,
            "timestamp": datetime.now().isoformat()
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return result 