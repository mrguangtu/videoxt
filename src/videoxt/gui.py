"""Tkinter GUI界面模块。

此模块提供了一个简单的图形界面，方便用户调试和使用视频关键帧提取功能。
"""
import os
import threading
import tkinter as tk
from datetime import timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional

from .controllers import ExtractionConfig, VideoExtractor
from .models import ExtractionResult
from .ffmpeg import FFmpegWrapper


class VideoExtractorGUI:
    """视频提取器GUI类。"""

    def __init__(self, root: tk.Tk):
        """初始化GUI。

        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("视频关键帧提取工具")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabel", padding=5)
        self.style.configure("TEntry", padding=5)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建变量
        self.video_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.segment_duration = tk.DoubleVar(value=30.0)
        self.n_workers = tk.IntVar(value=0)  # 0表示自动
        self.output_format = tk.StringVar(value="png")
        self.audio_format = tk.StringVar(value="mp3")
        self.quality = tk.IntVar(value=95)
        
        # 创建界面元素
        self._create_widgets()
        
        # 提取器实例
        self.extractor: Optional[VideoExtractor] = None
        self.result: Optional[ExtractionResult] = None
        
        # 处理线程
        self.processing_thread: Optional[threading.Thread] = None
        self.is_processing = False

    def _create_widgets(self):
        """创建界面元素。"""
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.main_frame, text="文件选择", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="视频文件:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.video_path, width=50).grid(row=0, column=1, sticky=tk.EW)
        ttk.Button(file_frame, text="浏览...", command=self._browse_video).grid(row=0, column=2, padx=5)
        
        ttk.Label(file_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky=tk.EW)
        ttk.Button(file_frame, text="浏览...", command=self._browse_output).grid(row=1, column=2, padx=5)
        
        file_frame.columnconfigure(1, weight=1)
        
        # 参数设置区域
        param_frame = ttk.LabelFrame(self.main_frame, text="参数设置", padding=10)
        param_frame.pack(fill=tk.X, pady=5)
        
        # 第一行
        ttk.Label(param_frame, text="片段时长(秒):").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(param_frame, textvariable=self.segment_duration, width=10).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(param_frame, text="工作进程数(0=自动):").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Entry(param_frame, textvariable=self.n_workers, width=10).grid(row=0, column=3, sticky=tk.W)
        
        # 第二行
        ttk.Label(param_frame, text="图像格式:").grid(row=1, column=0, sticky=tk.W)
        ttk.Combobox(param_frame, textvariable=self.output_format, values=["png", "jpg", "bmp"], width=7).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(param_frame, text="音频格式:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Combobox(param_frame, textvariable=self.audio_format, values=["mp3", "wav", "aac"], width=7).grid(row=1, column=3, sticky=tk.W)
        
        # 第三行
        ttk.Label(param_frame, text="输出质量(1-100):").grid(row=2, column=0, sticky=tk.W)
        ttk.Scale(param_frame, from_=1, to=100, variable=self.quality, orient=tk.HORIZONTAL, length=200).grid(row=2, column=1, columnspan=3, sticky=tk.W)
        
        # 操作区域
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(action_frame, text="开始提取", command=self._start_extraction)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="打开输出目录", command=self._open_output_dir).pack(side=tk.LEFT, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.main_frame, text="处理日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

    def _browse_video(self):
        """浏览视频文件。"""
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.video_path.set(file_path)
            # 自动设置输出目录
            if not self.output_dir.get():
                self.output_dir.set(os.path.join(os.path.dirname(file_path), "output"))

    def _browse_output(self):
        """浏览输出目录。"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir.set(dir_path)

    def _open_output_dir(self):
        """打开输出目录。"""
        output_dir = self.output_dir.get()
        if output_dir and os.path.exists(output_dir):
            os.startfile(output_dir) if os.name == 'nt' else os.system(f'xdg-open "{output_dir}"')
        else:
            messagebox.showwarning("警告", "输出目录不存在")

    def _log(self, message: str):
        """添加日志消息。

        Args:
            message: 日志消息
        """
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def _update_progress(self, value):
        """更新进度条。

        Args:
            value: 进度值（0-100）
        """
        self.progress_var.set(value)
        self.root.update_idletasks()

    def _process_video(self, video_path, output_dir, config):
        """在单独的线程中处理视频。

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            config: 提取配置
        """
        try:
            # 执行提取
            self.result = self.extractor.extract(video_path, output_dir)
            
            # 更新UI（在主线程中）
            self.root.after(0, self._process_complete)
        except Exception as e:
            # 处理错误（在主线程中）
            self.root.after(0, lambda: self._process_error(str(e)))

    def _process_complete(self):
        """处理完成回调。"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.status_var.set("处理完成")
        self.progress_var.set(100)
        
        # 显示结果
        self._log("\n处理完成!")
        self._log(f"总处理时间: {self.result.processing_time}")
        self._log(f"提取关键帧数: {len(self.result.keyframes)}")
        self._log(f"提取音频片段数: {len(self.result.audio_segments)}")
        
        if self.result.error_log:
            self._log(f"错误数: {len(self.result.error_log)}")
            for task_id, error in self.result.error_log.items():
                self._log(f"  - {task_id}: {error}")
        
        messagebox.showinfo("完成", "视频处理完成!")

    def _process_error(self, error_message):
        """处理错误回调。

        Args:
            error_message: 错误消息
        """
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.status_var.set("处理失败")
        self._log(f"\n错误: {error_message}")
        messagebox.showerror("错误", f"处理失败: {error_message}")

    def _start_extraction(self):
        """开始提取过程。"""
        # 检查输入
        video_path = self.video_path.get()
        output_dir = self.output_dir.get()
        
        if not video_path:
            messagebox.showerror("错误", "请选择视频文件")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        if not os.path.exists(video_path):
            messagebox.showerror("错误", "视频文件不存在")
            return
        
        # 创建配置
        config = ExtractionConfig(
            segment_duration=self.segment_duration.get(),
            n_workers=self.n_workers.get() or None,
            output_format=self.output_format.get(),
            audio_format=self.audio_format.get(),
            quality=self.quality.get()
        )
        
        # 创建提取器
        self.extractor = VideoExtractor(config)
        
        # 更新状态
        self.status_var.set("正在处理...")
        self.progress_var.set(0)
        self._log(f"开始处理视频: {video_path}")
        self._log(f"输出目录: {output_dir}")
        self._log(f"配置: {config.__dict__}")
        
        # 禁用开始按钮
        self.start_button.config(state=tk.DISABLED)
        self.is_processing = True
        
        # 在后台线程中处理视频
        def process_thread():
            try:
                # 获取视频总时长
                ffmpeg = FFmpegWrapper(Path(video_path))
                metadata = ffmpeg.get_metadata()
                total_duration = metadata['duration']
                
                # 计算总任务数
                segment_duration = config.segment_duration
                total_segments = int(total_duration / segment_duration) + (1 if total_duration % segment_duration > 0 else 0)
                processed_segments = 0
                
                def update_progress():
                    nonlocal processed_segments
                    if self.is_processing:
                        progress = (processed_segments / total_segments) * 100
                        self.progress_var.set(min(progress, 100))
                        self.root.after(100, update_progress)
                
                # 启动进度更新
                self.root.after(0, update_progress)
                
                # 执行提取
                self.result = self.extractor.extract(video_path, output_dir)
                
                # 处理完成
                self.progress_var.set(100)
                self.root.after(0, self._process_complete)
            except Exception as e:
                self.root.after(0, lambda: self._process_error(str(e)))
        
        # 创建并启动处理线程
        self.processing_thread = threading.Thread(target=process_thread)
        self.processing_thread.daemon = True
        self.processing_thread.start()


def main():
    """GUI入口函数。"""
    root = tk.Tk()
    app = VideoExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 