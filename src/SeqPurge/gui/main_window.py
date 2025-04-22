import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gui.widgets import DirectorySelector, ParameterFrame, ProgressFrame, LogFrame
from core.deduplicator import Deduplicator
import threading

class MainWindow:
    def __init__(self, root, config, logger):
        self.root = root
        self.config = config
        self.logger = logger
        self.deduplicator = None
        self.processing = False
        
        self._create_widgets()
        self._setup_layout()
        
    def _create_widgets(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # 创建各个功能区域
        self.dir_selector = DirectorySelector(self.main_frame)
        self.param_frame = ParameterFrame(self.main_frame, self.config)
        self.progress_frame = ProgressFrame(self.main_frame)
        self.log_frame = LogFrame(self.main_frame)
        
        # 创建控制按钮
        self.control_frame = ttk.Frame(self.main_frame)
        self.start_button = ttk.Button(self.control_frame, text="开始处理", command=self.start_processing)
        self.stop_button = ttk.Button(self.control_frame, text="停止处理", command=self.stop_processing, state=tk.DISABLED)
        
    def _setup_layout(self):
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 布局各个组件
        self.dir_selector.pack(fill=tk.X, pady=5)
        self.param_frame.pack(fill=tk.X, pady=5)
        self.control_frame.pack(fill=tk.X, pady=5)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.progress_frame.pack(fill=tk.X, pady=5)
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def start_processing(self):
        if self.processing:
            return
            
        # 获取参数
        input_dir = self.dir_selector.get_input_dir()
        output_dir = self.dir_selector.get_output_dir()
        mode = self.param_frame.get_mode()
        threshold = self.param_frame.get_threshold()
        algorithm = self.param_frame.get_algorithm()
        
        if not input_dir:
            messagebox.showerror("错误", "请选择输入目录")
            return
            
        if mode in [2, 3] and not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
            
        # 更新UI状态
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 创建去重器实例
        self.deduplicator = Deduplicator(
            input_dir=input_dir,
            output_dir=output_dir,
            mode=mode,
            threshold=threshold,
            algorithm=algorithm,
            progress_callback=self.progress_frame.update_progress,
            log_callback=self.log_frame.add_log
        )
        
        # 在新线程中启动处理
        self.processing_thread = threading.Thread(target=self._process)
        self.processing_thread.start()
        
    def _process(self):
        try:
            self.deduplicator.process()
        except Exception as e:
            self.logger.error(f"处理过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"处理过程中发生错误: {str(e)}")
        finally:
            self._processing_complete()
            
    def stop_processing(self):
        if self.deduplicator:
            self.deduplicator.stop()
            self.processing = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
    def _processing_complete(self):
        self.processing = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        messagebox.showinfo("完成", "处理完成") 