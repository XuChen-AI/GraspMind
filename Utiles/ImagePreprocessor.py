"""
图像预处理工具模块

该模块提供图像预处理功能，包括：
1. 图像尺寸调整至最大 1024x1024 像素
2. 转换为 RGB 色彩空间
3. 使用质量系数为 85 的 JPEG 压缩算法优化数据传输效率
"""

from PIL import Image
import io
import os
from typing import Union, Tuple


class ImagePreprocessor:
    """
    图像预处理器类
    
    提供图像预处理功能，包括尺寸调整、色彩空间转换和压缩优化
    """
    
    MAX_SIZE = 1024
    JPEG_QUALITY = 85
    
    def __init__(self):
        """初始化图像预处理器"""
        self.original_size = None  # 保存原图尺寸
        self.processed_size = None  # 保存处理后尺寸
        self.scale_factor = None   # 保存缩放比例
    
    def resize_image(self, image: Image.Image, max_size: int = MAX_SIZE) -> Image.Image:
        """
        调整图像尺寸，保持宽高比
        
        Args:
            image (Image.Image): 输入图像
            max_size (int): 最大尺寸，默认为1024
            
        Returns:
            Image.Image: 调整尺寸后的图像
        """
        width, height = image.size
        self.original_size = (width, height)  # 保存原图尺寸
        
        # 如果图像已经在限制范围内，直接返回
        if width <= max_size and height <= max_size:
            self.processed_size = (width, height)
            self.scale_factor = 1.0  # 无缩放
            return image
        
        # 计算缩放比例，保持宽高比
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
            self.scale_factor = max_size / width
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
            self.scale_factor = max_size / height
        
        self.processed_size = (new_width, new_height)
        
        # 使用高质量重采样算法
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image
    
    def convert_to_rgb(self, image: Image.Image) -> Image.Image:
        """
        转换图像为 RGB 色彩空间
        
        Args:
            image (Image.Image): 输入图像
            
        Returns:
            Image.Image: RGB 格式的图像
        """
        if image.mode != 'RGB':
            # 处理不同的色彩模式
            if image.mode == 'RGBA':
                # 创建白色背景处理透明通道
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # 使用 alpha 通道作为蒙版
                return background
            else:
                return image.convert('RGB')
        return image
    
    def compress_image(self, image: Image.Image, quality: int = JPEG_QUALITY) -> bytes:
        """
        使用 JPEG 压缩算法压缩图像
        
        Args:
            image (Image.Image): 输入图像
            quality (int): JPEG 质量系数，默认为85
              Returns:
            bytes: 压缩后的图像字节数据
        """
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        return buffer.getvalue()
    
    def preprocess_image(self, 
                        image_input: Union[str, Image.Image], 
                        max_size: int = MAX_SIZE,
                        quality: int = JPEG_QUALITY) -> Tuple[Image.Image, bytes, dict]:
        """
        完整的图像预处理流程
        
        Args:
            image_input (Union[str, Image.Image]): 图像文件路径或 PIL Image 对象
            max_size (int): 最大尺寸，默认为1024
            quality (int): JPEG 质量系数，默认为85
            
        Returns:
            Tuple[Image.Image, bytes, dict]: 预处理后的图像对象、压缩字节数据和缩放信息
            
        Raises:
            FileNotFoundError: 当图像文件不存在时
            ValueError: 当输入参数无效时
        """
        # 加载图像
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"图像文件不存在: {image_input}")
            image = Image.open(image_input)
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ValueError("输入必须是图像文件路径或 PIL Image 对象")
        
        # 预处理步骤
        # 1. 转换为 RGB 色彩空间
        rgb_image = self.convert_to_rgb(image)
        
        # 2. 调整图像尺寸
        resized_image = self.resize_image(rgb_image, max_size)
        
        # 3. JPEG 压缩
        compressed_data = self.compress_image(resized_image, quality)
        
        # 4. 获取缩放信息
        scale_info = self.get_scale_info()
        
        return resized_image, compressed_data, scale_info
    
    def save_preprocessed_image(self, 
                               image_input: Union[str, Image.Image],
                               output_path: str,
                               max_size: int = MAX_SIZE,
                               quality: int = JPEG_QUALITY) -> bool:
        """
        预处理图像并保存到指定路径
        
        Args:
            image_input (Union[str, Image.Image]): 图像文件路径或 PIL Image 对象
            output_path (str): 输出文件路径
            max_size (int): 最大尺寸，默认为1024
            quality (int): JPEG 质量系数，默认为85
              Returns:
            bool: 保存成功返回 True，失败返回 False
        """
        try:
            preprocessed_image, _, scale_info = self.preprocess_image(image_input, max_size, quality)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 保存预处理后的图像
            preprocessed_image.save(output_path, format='JPEG', quality=quality, optimize=True)
            return True
            
        except Exception as e:
            print(f"保存预处理图像时发生错误: {e}")
            return False
    
    def get_image_info(self, image: Image.Image) -> dict:
        """
        获取图像信息
        
        Args:
            image (Image.Image): 图像对象
            
        Returns:
            dict: 包含图像信息的字典
        """
        return {
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'format': image.format
        }
    
    def get_scale_info(self) -> dict:
        """
        获取缩放信息
        
        Returns:
            dict: 包含原图尺寸、处理后尺寸和缩放比例的字典
        """
        return {
            'original_size': self.original_size,
            'processed_size': self.processed_size,
            'scale_factor': self.scale_factor
        }
    
    def convert_coordinates_to_original(self, bbox: list) -> list:
        """
        将处理后图片的坐标转换回原图坐标
        
        Args:
            bbox (list): 处理后图片的边界框坐标 [x1, y1, x2, y2]
            
        Returns:
            list: 转换到原图的边界框坐标 [x1, y1, x2, y2]
            
        Raises:
            ValueError: 当缩放信息不可用时
        """
        if self.scale_factor is None or self.original_size is None:
            raise ValueError("缩放信息不可用，请先调用preprocess_image方法")
        
        if len(bbox) != 4:
            raise ValueError("边界框坐标必须包含4个值: [x1, y1, x2, y2]")
        
        x1, y1, x2, y2 = bbox
        
        # 将坐标转换回原图尺寸
        original_x1 = x1 / self.scale_factor
        original_y1 = y1 / self.scale_factor
        original_x2 = x2 / self.scale_factor
        original_y2 = y2 / self.scale_factor
        
        # 确保坐标在原图范围内
        original_width, original_height = self.original_size
        original_x1 = max(0, min(original_x1, original_width))
        original_y1 = max(0, min(original_y1, original_height))
        original_x2 = max(0, min(original_x2, original_width))
        original_y2 = max(0, min(original_y2, original_height))
        
        return [original_x1, original_y1, original_x2, original_y2]
    
    def convert_coordinates_list_to_original(self, bbox_list: list) -> list:
        """
        批量将处理后图片的坐标转换回原图坐标
        
        Args:
            bbox_list (list): 包含多个边界框的列表，每个边界框格式为 [x1, y1, x2, y2]
            
        Returns:
            list: 转换到原图的边界框列表
        """
        return [self.convert_coordinates_to_original(bbox) for bbox in bbox_list]


# 便捷函数
def preprocess_image_file(input_path: str, 
                         output_path: str = None,
                         max_size: int = 1024,
                         quality: int = 85) -> Union[Tuple[Image.Image, bytes, dict], bool]:
    """
    便捷的图像预处理函数
    
    Args:
        input_path (str): 输入图像文件路径
        output_path (str, optional): 输出文件路径，如果提供则保存文件
        max_size (int): 最大尺寸，默认为1024
        quality (int): JPEG 质量系数，默认为85
        
    Returns:
        Union[Tuple[Image.Image, bytes, dict], bool]: 
            如果 output_path 为 None，返回 (预处理后的图像, 压缩字节数据, 缩放信息)
            如果提供 output_path，返回保存是否成功的布尔值
    """
    preprocessor = ImagePreprocessor()
    
    if output_path:
        return preprocessor.save_preprocessed_image(input_path, output_path, max_size, quality)
    else:
        return preprocessor.preprocess_image(input_path, max_size, quality)


if __name__ == "__main__":
    # 示例用法
    preprocessor = ImagePreprocessor()
      # 示例1: 预处理图像并获取结果
    try:
        image_path = "test.jpg"  # 替换为实际图像路径
        processed_image, compressed_data, scale_info = preprocessor.preprocess_image(image_path)
        
        print(f"预处理完成:")
        print(f"图像尺寸: {processed_image.size}")
        print(f"压缩数据大小: {len(compressed_data)} 字节")
        print(f"缩放信息: {scale_info}")
        
    except FileNotFoundError:
        print("示例图像文件不存在，请提供有效的图像路径")
    
    # 示例2: 使用便捷函数
    # success = preprocess_image_file("input.jpg", "output.jpg")
    # print(f"保存结果: {success}")
