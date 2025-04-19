#!/usr/bin/env python
"""视频关键帧提取工具 - GUI启动脚本

此脚本用于启动视频关键帧提取工具的图形界面。
"""
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 导入GUI模块
from videoxt.gui import main

if __name__ == "__main__":
    print("启动视频关键帧提取工具GUI...")
    main() 