# VideoXT

VideoXT 是一个高效并行的视频关键帧提取与音视频对齐工具。它提供了命令行界面和图形用户界面，支持批量处理视频文件，并能够智能提取关键帧。

## 功能特点

- 支持批量处理视频文件
- 智能关键帧提取
- 音视频同步对齐
- 提供命令行和图形界面两种使用方式
- 多线程并行处理，提高效率

## 安装要求

- Python 3.8 或更高版本
- FFmpeg

## 安装方法

1. 克隆仓库：
```bash
git clone https://github.com/mrguangtu/videoxt.git
cd videoxt
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行界面

```bash
python -m videoxt.cli <视频文件路径> [可选参数]
```

必需参数：
- `视频文件路径`：要处理的视频文件的路径

可选参数：
- `--output-dir`：输出目录路径，如果不指定则使用默认目录
- `--segment-duration`：每个片段的时长（秒），默认为30.0秒
- `--workers`：工作进程数，用于并行处理
- `--format`：输出图像格式，默认为"png"，可选值包括：png、jpg、bmp
- `--audio-format`：输出音频格式，默认为"mp3"，可选值包括：mp3、wav、aac
- `--quality`：输出质量，范围1-100，默认为95

使用示例：
```bash
# 基本用法
python -m videoxt.cli video.mp4

# 指定输出目录和片段时长
python -m videoxt.cli video.mp4 --output-dir ./output --segment-duration 20.0

# 使用4个工作进程，输出jpg格式
python -m videoxt.cli video.mp4 --workers 4 --format jpg

# 完整参数示例
python -m videoxt.cli video.mp4 --output-dir ./output --segment-duration 15.0 --workers 4 --format jpg --audio-format wav --quality 90
```

处理完成后，程序会显示：
- 总处理时间
- 提取的关键帧数量
- 提取的音频片段数量
- 如果有错误，会显示错误数量

### 图形界面

```bash
python -m videoxt.gui_launcher
```

## 开发环境设置

1. 安装开发依赖：
```bash
pip install -e ".[dev]"
```

2. 运行测试：
```bash
pytest
```

## 许可证

MIT License

## 作者

mrguangtu (mrguangtu@163.com) 