import cv2
import numpy as np
from PIL import Image
import imagehash

class ImageComparator:
    def __init__(self, algorithm, threshold):
        self.algorithm = algorithm
        self.threshold = threshold
        
    def is_similar(self, img1_path, img2_path):
        if self.algorithm == "hash":
            return self._compare_hash(img1_path, img2_path)
        elif self.algorithm == "pixel":
            return self._compare_pixel(img1_path, img2_path)
        else:  # hybrid
            return self._compare_hybrid(img1_path, img2_path)
            
    def _compare_hash(self, img1_path, img2_path):
        # 使用感知哈希算法
        hash1 = imagehash.average_hash(Image.open(img1_path))
        hash2 = imagehash.average_hash(Image.open(img2_path))
        diff = hash1 - hash2
        
        # 将哈希差异转换为百分比
        similarity = (64 - diff) / 64 * 100
        return similarity > (100 - self.threshold)
        
    def _compare_pixel(self, img1_path, img2_path):
        # 读取图像
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        
        if img1 is None or img2 is None:
            return False
            
        # 确保图像大小相同
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
        # 计算均方误差
        mse = np.mean((img1 - img2) ** 2)
        
        # 将MSE转换为相似度百分比
        max_mse = 255 * 255
        similarity = (1 - mse / max_mse) * 100
        return similarity > (100 - self.threshold)
        
    def _compare_hybrid(self, img1_path, img2_path):
        # 先使用哈希快速比较
        hash_similar = self._compare_hash(img1_path, img2_path)
        
        if not hash_similar:
            return False
            
        # 如果哈希相似，再使用像素比较确认
        return self._compare_pixel(img1_path, img2_path) 