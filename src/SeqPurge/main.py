import tkinter as tk
from gui.main_window import MainWindow
from utils.logger import setup_logger
from utils.config import Config

def main():
    # 初始化配置
    config = Config()
    
    # 设置日志
    logger = setup_logger()
    logger.info("程序启动")
    
    # 创建主窗口
    root = tk.Tk()
    root.title("图像序列去重工具")
    root.geometry("800x600")
    
    # 创建主窗口实例
    app = MainWindow(root, config, logger)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main() 