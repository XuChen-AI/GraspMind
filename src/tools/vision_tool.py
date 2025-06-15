"""
视觉分析工具模块

提供图像处理、物体检测和分割的核心工具类。
支持多种视觉模型的统一接口。
"""

import base64
import io
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from crewai_tools import BaseTool
from loguru import logger

from ..models.data_models import DetectedObject, BoundingBox, ObjectCategory, SegmentationMask
from ..utils.image_utils import ImageProcessor
from ..utils.model_client import ModelClient


class VisionAnalysisTool(BaseTool):
    """
    视觉分析工具
    
    统一的视觉分析接口，支持物体检测和分割功能。
    可以配置不同的后端模型（GPT-4o、Qwen-VL等）。
    """
    
    name: str = "Vision Analysis Tool"
    description: str = """
    强大的计算机视觉分析工具，支持以下功能：
    1. detect_objects: 检测图像中的所有物体并返回位置信息
    2. segment_part: 对指定物体的特定部分进行精确分割
    """
    
    def __init__(self, model_client: ModelClient, image_processor: ImageProcessor):
        """
        初始化视觉分析工具
        
        Args:
            model_client: 模型客户端，用于调用VLM
            image_processor: 图像处理器，用于图像预处理
        """
        super().__init__()
        self.model_client = model_client
        self.image_processor = image_processor
        
    def _run(self, operation: str, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        执行视觉分析操作
        
        Args:
            operation: 操作类型 ('detect_objects' 或 'segment_part')
            image_path: 图像文件路径
            **kwargs: 其他参数
            
        Returns:
            操作结果字典
        """
        try:
            # 验证图像路径
            if not Path(image_path).exists():
                return {"error": f"图像文件不存在: {image_path}"}
            
            # 加载和预处理图像
            image = self.image_processor.load_image(image_path)
            if image is None:
                return {"error": f"无法加载图像: {image_path}"}
            
            # 根据操作类型执行相应功能
            if operation == "detect_objects":
                return self._detect_objects(image, image_path)
            elif operation == "segment_part":
                return self._segment_part(image, image_path, **kwargs)
            else:
                return {"error": f"不支持的操作类型: {operation}"}
                
        except Exception as e:
            logger.error(f"视觉分析工具执行失败: {str(e)}")
            return {"error": f"执行失败: {str(e)}"}
    
    def _detect_objects(self, image: np.ndarray, image_path: str) -> Dict[str, Any]:
        """
        检测图像中的物体
        
        Args:
            image: 预处理后的图像数组
            image_path: 原始图像路径
            
        Returns:
            包含检测结果的字典
        """
        try:
            # 将图像转换为base64用于API调用
            image_b64 = self.image_processor.image_to_base64(image)
            
            # 构造检测提示词
            prompt = self._build_detection_prompt()
            
            # 调用VLM进行物体检测
            response = self.model_client.analyze_image(
                image_b64=image_b64,
                prompt=prompt,
                response_format="json"
            )
            
            # 解析检测结果
            detection_result = self._parse_detection_response(response, image.shape)
            
            logger.info(f"成功检测到 {len(detection_result['objects'])} 个物体")
            return detection_result
            
        except Exception as e:
            logger.error(f"物体检测失败: {str(e)}")
            return {"error": f"物体检测失败: {str(e)}"}
    
    def _segment_part(self, image: np.ndarray, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        分割物体的特定部分
        
        Args:
            image: 预处理后的图像数组
            image_path: 原始图像路径
            **kwargs: 包含target_object和target_part的参数
            
        Returns:
            包含分割结果的字典
        """
        try:
            # 获取分割目标
            target_object = kwargs.get("target_object")
            target_part = kwargs.get("target_part")
            
            if not target_object or not target_part:
                return {"error": "缺少分割目标参数 (target_object, target_part)"}
            
            # 将图像转换为base64
            image_b64 = self.image_processor.image_to_base64(image)
            
            # 构造分割提示词
            prompt = self._build_segmentation_prompt(target_object, target_part)
            
            # 调用VLM进行分割
            response = self.model_client.analyze_image(
                image_b64=image_b64,
                prompt=prompt,
                response_format="json"
            )
            
            # 解析分割结果
            segmentation_result = self._parse_segmentation_response(
                response, image.shape, target_object, target_part
            )
            
            logger.info(f"成功分割 {target_object} 的 {target_part} 部分")
            return segmentation_result
            
        except Exception as e:
            logger.error(f"部件分割失败: {str(e)}")
            return {"error": f"部件分割失败: {str(e)}"}
    
    def _build_detection_prompt(self) -> str:
        """构建物体检测提示词"""
        return """
请仔细分析这张图像，识别出其中的所有主要物体。

要求：
1. 识别所有可见的物体，特别关注以下类型：杯子、剪刀、瓶子、刀具、餐具、书籍、文具、电子设备等
2. 对每个物体提供准确的边界框坐标（相对于图像尺寸的像素坐标）
3. 给出详细的物体描述，包括颜色、形状、材质等特征
4. 评估检测的置信度

请严格按照以下JSON格式输出结果：
{
    "objects": [
        {
            "object_id": "obj_1",
            "label": "物体名称",
            "description": "详细描述",
            "bounding_box": {
                "x1": 左上角x坐标,
                "y1": 左上角y坐标,
                "x2": 右下角x坐标,
                "y2": 右下角y坐标,
                "confidence": 置信度(0-1)
            },
            "confidence": 整体置信度(0-1)
        }
    ],
    "total_objects": 物体总数
}
"""
    
    def _build_segmentation_prompt(self, target_object: str, target_part: str) -> str:
        """构建分割提示词"""
        return f"""
请对图像中的"{target_object}"的"{target_part}"部分进行精确的像素级分割。

任务要求：
1. 定位图像中的"{target_object}"
2. 识别并精确分割其"{target_part}"部分
3. 生成二值掩码，其中目标区域为1，背景为0
4. 确保分割边界清晰准确

分割说明：
- 如果是杯子，"杯柄"指的是用于抓握的把手部分
- 如果是剪刀，"握柄"指的是手指插入的环形部分
- 如果是刀具，"握柄"指的是手持部分，与刀刃相对
- 其他物体请根据常识理解功能性部件

请严格按照以下JSON格式输出结果：
{{
    "target_found": true/false,
    "segmentation_mask": [
        [像素行1的0/1值列表],
        [像素行2的0/1值列表],
        ...
    ],
    "mask_info": {{
        "width": 掩码宽度,
        "height": 掩码高度,
        "target_pixels": 目标像素数量,
        "confidence": 分割置信度(0-1)
    }},
    "reasoning": "分割推理过程说明"
}}
"""
    
    def _parse_detection_response(self, response: str, image_shape: Tuple[int, int, int]) -> Dict[str, Any]:
        """
        解析物体检测响应
        
        Args:
            response: VLM响应文本
            image_shape: 图像形状 (H, W, C)
            
        Returns:
            标准化的检测结果
        """
        try:
            # 尝试解析JSON响应
            result_data = json.loads(response)
            
            objects = []
            for obj_data in result_data.get("objects", []):
                try:
                    # 创建边界框对象
                    bbox_data = obj_data.get("bounding_box", {})
                    bbox = BoundingBox(
                        x1=int(bbox_data.get("x1", 0)),
                        y1=int(bbox_data.get("y1", 0)),
                        x2=int(bbox_data.get("x2", image_shape[1])),
                        y2=int(bbox_data.get("y2", image_shape[0])),
                        confidence=float(bbox_data.get("confidence", 1.0))
                    )
                    
                    # 创建检测物体对象
                    detected_obj = DetectedObject(
                        object_id=obj_data.get("object_id", f"obj_{len(objects)}"),
                        label=obj_data.get("label", "未知物体"),
                        category=self._classify_object(obj_data.get("label", "")),
                        bounding_box=bbox,
                        confidence=float(obj_data.get("confidence", 1.0)),
                        description=obj_data.get("description")
                    )
                    
                    objects.append(detected_obj)
                    
                except Exception as e:
                    logger.warning(f"解析单个物体数据失败: {str(e)}")
                    continue
            
            return {
                "objects": [obj.dict() for obj in objects],
                "total_objects": len(objects),
                "success": True
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            return {"error": "响应格式错误", "success": False}
        except Exception as e:
            logger.error(f"检测结果解析失败: {str(e)}")
            return {"error": f"解析失败: {str(e)}", "success": False}
    
    def _parse_segmentation_response(self, response: str, image_shape: Tuple[int, int, int],
                                   target_object: str, target_part: str) -> Dict[str, Any]:
        """
        解析分割响应
        
        Args:
            response: VLM响应文本
            image_shape: 图像形状 (H, W, C)
            target_object: 目标物体
            target_part: 目标部件
            
        Returns:
            标准化的分割结果
        """
        try:
            # 尝试解析JSON响应
            result_data = json.loads(response)
            
            if not result_data.get("target_found", False):
                return {
                    "error": f"未找到指定的 {target_object} 或其 {target_part} 部分",
                    "success": False
                }
            
            # 获取分割掩码
            mask_data = result_data.get("segmentation_mask", [])
            if not mask_data:
                return {
                    "error": "未生成有效的分割掩码",
                    "success": False
                }
            
            # 创建分割掩码对象
            mask = SegmentationMask(
                mask_array=mask_data,
                width=result_data.get("mask_info", {}).get("width", len(mask_data[0]) if mask_data else 0),
                height=result_data.get("mask_info", {}).get("height", len(mask_data)),
                target_object_id=f"seg_{target_object}",
                target_part_name=target_part,
                mask_confidence=float(result_data.get("mask_info", {}).get("confidence", 1.0))
            )
            
            return {
                "mask": mask.dict(),
                "reasoning": result_data.get("reasoning", ""),
                "success": True
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"分割结果JSON解析失败: {str(e)}")
            return {"error": "分割响应格式错误", "success": False}
        except Exception as e:
            logger.error(f"分割结果解析失败: {str(e)}")
            return {"error": f"分割解析失败: {str(e)}", "success": False}
    
    def _classify_object(self, label: str) -> ObjectCategory:
        """
        根据标签分类物体
        
        Args:
            label: 物体标签
            
        Returns:
            物体类别
        """
        label_lower = label.lower()
        
        # 定义关键词映射
        category_keywords = {
            ObjectCategory.CUP: ["杯", "cup", "mug", "马克杯", "茶杯", "咖啡杯"],
            ObjectCategory.SCISSORS: ["剪刀", "scissors", "剪子"],
            ObjectCategory.BOTTLE: ["瓶", "bottle", "水瓶", "饮料瓶"],
            ObjectCategory.KNIFE: ["刀", "knife", "水果刀", "菜刀"],
            ObjectCategory.FORK: ["叉", "fork", "叉子"],
            ObjectCategory.SPOON: ["勺", "spoon", "勺子", "汤勺"],
            ObjectCategory.PLATE: ["盘", "plate", "盘子", "餐盘"],
            ObjectCategory.BOWL: ["碗", "bowl", "汤碗", "饭碗"],
            ObjectCategory.BOOK: ["书", "book", "书籍", "图书"],
            ObjectCategory.PEN: ["笔", "pen", "钢笔", "圆珠笔", "铅笔"],
            ObjectCategory.PHONE: ["手机", "phone", "电话", "smartphone"]
        }
        
        # 匹配关键词
        for category, keywords in category_keywords.items():
            if any(keyword in label_lower for keyword in keywords):
                return category
        
        return ObjectCategory.UNKNOWN
