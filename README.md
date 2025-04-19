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
python -m videoxt.cli [参数]
```

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