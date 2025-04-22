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
        mode_frame = ttk.LabelFrame(self, text="处理模式", padding="5")
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.mode_var = tk.IntVar(value=self.config.get("mode", 1))
        ttk.Radiobutton(mode_frame, text="模式1-原地删除", variable=self.mode_var, value=1).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="模式2-新建复制", variable=self.mode_var, value=2).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="模式3-新建删除", variable=self.mode_var, value=3).pack(anchor=tk.W)
        
        # 处理模式说明
        mode_help = ttk.Label(mode_frame, text="模式1：直接在原文件夹中删除冗余帧\n"
                                              "模式2：复制保留的帧到新文件夹，使用全局编号\n"
                                              "模式3：复制保留的帧到新文件夹后删除原文件夹",
                             justify=tk.LEFT, wraplength=400)
        mode_help.pack(anchor=tk.W, pady=5)
        
        # 算法选择
        algo_frame = ttk.LabelFrame(self, text="比对算法", padding="5")
        algo_frame.pack(fill=tk.X, pady=5)
        
        self.algorithm_var = tk.StringVar(value=self.config.get("algorithm", "hash"))
        ttk.Radiobutton(algo_frame, text="哈希比对", variable=self.algorithm_var, value="hash").pack(anchor=tk.W)
        ttk.Radiobutton(algo_frame, text="像素比对", variable=self.algorithm_var, value="pixel").pack(anchor=tk.W)
        ttk.Radiobutton(algo_frame, text="混合模式", variable=self.algorithm_var, value="hybrid").pack(anchor=tk.W)
        
        # 算法说明
        algo_help = ttk.Label(algo_frame, text="哈希比对：使用感知哈希算法，速度快但可能误判\n"
                                              "像素比对：使用SSIM算法，准确度高但速度较慢\n"
                                              "混合模式：先使用哈希快速筛选，再用像素比对确认",
                             justify=tk.LEFT, wraplength=400)
        algo_help.pack(anchor=tk.W, pady=5)
        
        # 阈值设置
        threshold_frame = ttk.LabelFrame(self, text="相似度阈值", padding="5")
        threshold_frame.pack(fill=tk.X, pady=5)
        
        self.threshold_var = tk.DoubleVar(value=self.config.get("threshold", 5.0))
        threshold_scale = ttk.Scale(threshold_frame, from_=1, to=10, variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.pack(fill=tk.X, padx=5)
        
        # 阈值说明
        threshold_help = ttk.Label(threshold_frame, text="设置图像相似度阈值（1-10%），值越小越严格",
                                 justify=tk.LEFT, wraplength=400)
        threshold_help.pack(anchor=tk.W, pady=5)
        
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