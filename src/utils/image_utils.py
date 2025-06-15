"""
图像处理工具模块

提供图像加载、预处理、格式转换等功能
"""

import base64
import io
from typing import Optional, Tuple, Union
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from loguru import logger


class ImageProcessor:
    """
    图像处理器
    
    提供图像的加载、预处理、格式转换等功能
    """
    
    def __init__(self, max_size: int = 1024, supported_formats: list = None):
        """
        初始化图像处理器
        
        Args:
            max_size: 图像最大尺寸
            supported_formats: 支持的图像格式列表
        """
        self.max_size = max_size
        self.supported_formats = supported_formats or ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        
    def load_image(self, image_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        加载图像文件
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            加载的图像数组，失败时返回None
        """
        try:
            # 转换为Path对象
            path = Path(image_path)
            
            # 检查文件是否存在
            if not path.exists():
                logger.error(f"图像文件不存在: {image_path}")
                return None
            
            # 检查文件格式
            if not self._is_supported_format(path):
                logger.error(f"不支持的图像格式: {path.suffix}")
                return None
            
            # 使用OpenCV加载图像
            image = cv2.imread(str(path))
            if image is None:
                logger.error(f"无法加载图像: {image_path}")
                return None
            
            # 转换为RGB格式（OpenCV默认为BGR）
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 调整图像尺寸
            image = self._resize_image(image)
            
            logger.info(f"成功加载图像: {image_path}, 尺寸: {image.shape}")
            return image
            
        except Exception as e:
            logger.error(f"加载图像失败: {str(e)}")
            return None
    
    def _is_supported_format(self, path: Path) -> bool:
        """
        检查是否为支持的图像格式
        
        Args:
            path: 文件路径
            
        Returns:
            是否支持该格式
        """
        suffix = path.suffix.lower().lstrip('.')
        return suffix in self.supported_formats
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        调整图像尺寸
        
        Args:
            image: 输入图像
            
        Returns:
            调整后的图像
        """
        height, width = image.shape[:2]
        
        # 如果图像尺寸已经在限制内，直接返回
        if max(height, width) <= self.max_size:
            return image
        
        # 计算缩放比例
        if height > width:
            scale = self.max_size / height
        else:
            scale = self.max_size / width
        
        # 计算新尺寸
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # 调整尺寸
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        logger.debug(f"图像尺寸调整: {width}x{height} -> {new_width}x{new_height}")
        return resized_image
    
    def image_to_base64(self, image: np.ndarray, format: str = 'PNG') -> str:
        """
        将图像转换为base64编码
        
        Args:
            image: 输入图像数组
            format: 图像格式
            
        Returns:
            base64编码的图像字符串
        """
        try:
            # 转换为PIL Image
            pil_image = Image.fromarray(image)
            
            # 转换为字节流
            buffer = io.BytesIO()
            pil_image.save(buffer, format=format)
            buffer.seek(0)
            
            # 编码为base64
            image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_b64
            
        except Exception as e:
            logger.error(f"图像base64编码失败: {str(e)}")
            raise
    
    def base64_to_image(self, image_b64: str) -> np.ndarray:
        """
        将base64编码转换为图像数组
        
        Args:
            image_b64: base64编码的图像字符串
            
        Returns:
            图像数组
        """
        try:
            # 解码base64
            image_data = base64.b64decode(image_b64)
            
            # 转换为PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # 转换为numpy数组
            image_array = np.array(pil_image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"base64图像解码失败: {str(e)}")
            raise
    
    def save_mask(self, mask: np.ndarray, output_path: Union[str, Path]) -> bool:
        """
        保存分割掩码
        
        Args:
            mask: 分割掩码数组
            output_path: 输出路径
            
        Returns:
            是否保存成功
        """
        try:
            # 确保掩码为二值图像
            mask_binary = (mask * 255).astype(np.uint8)
            
            # 保存掩码
            cv2.imwrite(str(output_path), mask_binary)
            
            logger.info(f"掩码保存成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"掩码保存失败: {str(e)}")
            return False
    
    def create_mask_overlay(self, image: np.ndarray, mask: np.ndarray, 
                           alpha: float = 0.5, color: Tuple[int, int, int] = (255, 0, 0)) -> np.ndarray:
        """
        创建掩码覆盖图像
        
        Args:
            image: 原始图像
            mask: 分割掩码
            alpha: 透明度
            color: 覆盖颜色 (R, G, B)
            
        Returns:
            带掩码覆盖的图像
        """
        try:
            # 确保图像和掩码尺寸一致
            if image.shape[:2] != mask.shape[:2]:
                mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
            
            # 创建彩色掩码
            colored_mask = np.zeros_like(image)
            colored_mask[mask > 0] = color
            
            # 混合图像和掩码
            overlay = cv2.addWeighted(image, 1 - alpha, colored_mask, alpha, 0)
            
            return overlay
            
        except Exception as e:
            logger.error(f"创建掩码覆盖失败: {str(e)}")
            return image
    
    def validate_image_quality(self, image: np.ndarray) -> dict:
        """
        验证图像质量
        
        Args:
            image: 输入图像
            
        Returns:
            质量评估结果
        """
        try:
            height, width = image.shape[:2]
            
            # 计算图像质量指标
            # 1. 清晰度（使用拉普拉斯算子）
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 2. 亮度
            brightness = np.mean(gray)
            
            # 3. 对比度
            contrast = np.std(gray)
            
            # 质量评估
            quality_score = min(100, (laplacian_var / 100) * 30 + 
                              (min(brightness, 255 - brightness) / 127) * 35 + 
                              (contrast / 127) * 35)
            
            return {
                "quality_score": round(quality_score, 2),
                "sharpness": round(laplacian_var, 2),
                "brightness": round(brightness, 2),
                "contrast": round(contrast, 2),
                "resolution": f"{width}x{height}",
                "is_good_quality": quality_score > 50
            }
            
        except Exception as e:
            logger.error(f"图像质量验证失败: {str(e)}")
            return {"error": str(e)}
