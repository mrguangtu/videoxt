#!/usr/bin/env python
"""GUI启动器脚本。

此脚本用于启动视频关键帧提取工具的图形界面。
"""
import sys
from videoxt.gui import main

def launch():
    """启动GUI应用程序。"""
    return main()

if __name__ == "__main__":
    sys.exit(launch()) 