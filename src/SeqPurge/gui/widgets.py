import tkinter as tk
from tkinter import ttk, filedialog
import os

class DirectorySelector(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="目录选择", padding="5")
        self._create_widgets()
        
    def _create_widgets(self):
        # 输入目录
        ttk.Label(self, text="输入目录:").grid(row=0, column=0, sticky=tk.W)
        self.input_entry = ttk.Entry(self, width=50)
        self.input_entry.grid(row=0, column=1, padx=5)
        ttk.Button(self, text="浏览", command=self._browse_input).grid(row=0, column=2)
        
        # 输出目录
        ttk.Label(self, text="输出目录:").grid(row=1, column=0, sticky=tk.W)
        self.output_entry = ttk.Entry(self, width=50)
        self.output_entry.grid(row=1, column=1, padx=5)
        ttk.Button(self, text="浏览", command=self._browse_output).grid(row=1, column=2)
        
    def _browse_input(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, dir_path)
            
    def _browse_output(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)
            
    def get_input_dir(self):
        return self.input_entry.get()
        
    def get_output_dir(self):
        return self.output_entry.get()

class ParameterFrame(ttk.LabelFrame):
    def __init__(self, parent, config):
        super().__init__(parent, text="参数设置", padding="5")
        self.config = config
        self._create_widgets()
        
    def _create_widgets(self):
        # 处理模式选择
        ttk.Label(self, text="处理模式:").grid(row=0, column=0, sticky=tk.W)
        self.mode_var = tk.IntVar(value=1)
        modes = [
            ("原地删除", 1),
            ("新建复制", 2),
            ("新建删除", 3)
        ]
        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(self, text=text, variable=self.mode_var, value=value).grid(row=0, column=i+1)
            
        # 相似度阈值
        ttk.Label(self, text="相似度阈值:").grid(row=1, column=0, sticky=tk.W)
        self.threshold_var = tk.DoubleVar(value=5.0)
        self.threshold_scale = ttk.Scale(self, from_=1, to=10, variable=self.threshold_var, orient=tk.HORIZONTAL)
        self.threshold_scale.grid(row=1, column=1, columnspan=3, sticky=tk.EW)
        self.threshold_label = ttk.Label(self, text="5.0%")
        self.threshold_label.grid(row=1, column=4)
        self.threshold_scale.config(command=self._update_threshold_label)
        
        # 算法选择
        ttk.Label(self, text="比对算法:").grid(row=2, column=0, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value="hash")
        algorithms = [
            ("哈希比对", "hash"),
            ("像素比对", "pixel"),
            ("混合模式", "hybrid")
        ]
        for i, (text, value) in enumerate(algorithms):
            ttk.Radiobutton(self, text=text, variable=self.algorithm_var, value=value).grid(row=2, column=i+1)
            
    def _update_threshold_label(self, value):
        self.threshold_label.config(text=f"{float(value):.1f}%")
        
    def get_mode(self):
        return self.mode_var.get()
        
    def get_threshold(self):
        return self.threshold_var.get()
        
    def get_algorithm(self):
        return self.algorithm_var.get()

class ProgressFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="处理进度", padding="5")
        self._create_widgets()
        
    def _create_widgets(self):
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)
        
        self.status_label = ttk.Label(self, text="就绪")
        self.status_label.pack()
        
    def update_progress(self, progress, status):
        self.progress_var.set(progress)
        self.status_label.config(text=status)

class LogFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="日志信息", padding="5")
        self._create_widgets()
        
    def _create_widgets(self):
        # 创建文本框和滚动条
        self.text = tk.Text(self, wrap=tk.WORD, height=10)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.text.config(yscrollcommand=scrollbar.set)
        
        # 布局
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def add_log(self, message):
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END) 