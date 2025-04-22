import json
import os
from typing import Dict, Any

class Config:
    def __init__(self):
        self.config_file = "seqpurge_config.json"
        self.default_config = {
            "mode": 1,
            "threshold": 5.0,
            "algorithm": "hash",
            "last_input_dir": "",
            "last_output_dir": ""
        }
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {str(e)}")
                return self.default_config.copy()
        return self.default_config.copy()
        
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value
        self.save_config()
        
    def update_last_dirs(self, input_dir: str, output_dir: str) -> None:
        """更新最后使用的目录"""
        self.set("last_input_dir", input_dir)
        self.set("last_output_dir", output_dir)
        
    def get_last_input_dir(self) -> str:
        """获取最后使用的输入目录"""
        return self.get("last_input_dir", "")
        
    def get_last_output_dir(self) -> str:
        """获取最后使用的输出目录"""
        return self.get("last_output_dir", "") 