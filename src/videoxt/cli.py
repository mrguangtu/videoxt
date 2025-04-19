"""命令行入口模块。"""
import argparse
import sys
from pathlib import Path

from .controllers import ExtractionConfig, VideoExtractor


def main():
    """命令行入口函数。"""
    parser = argparse.ArgumentParser(description="视频关键帧提取工具")
    parser.add_argument("video_path", type=str, help="视频文件路径")
    parser.add_argument("--output-dir", type=str, help="输出目录路径")
    parser.add_argument("--segment-duration", type=float, default=30.0,
                      help="每个片段的时长（秒）")
    parser.add_argument("--workers", type=int, help="工作进程数")
    parser.add_argument("--format", type=str, default="png",
                      help="输出图像格式")
    parser.add_argument("--audio-format", type=str, default="mp3",
                      help="输出音频格式")
    parser.add_argument("--quality", type=int, default=95,
                      help="输出质量（1-100）")

    args = parser.parse_args()

    # 创建配置
    config = ExtractionConfig(
        segment_duration=args.segment_duration,
        n_workers=args.workers,
        output_format=args.format,
        audio_format=args.audio_format,
        quality=args.quality
    )

    # 创建提取器
    extractor = VideoExtractor(config)

    try:
        # 执行提取
        result = extractor.extract(args.video_path, args.output_dir)
        
        # 打印结果摘要
        print("\n处理完成！")
        print(f"总处理时间: {result.processing_time}")
        print(f"提取关键帧数: {len(result.keyframes)}")
        print(f"提取音频片段数: {len(result.audio_segments)}")
        if result.error_log:
            print(f"错误数: {len(result.error_log)}")
        
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 