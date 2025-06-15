"""
数据模型定义模块

该模块定义了整个GraspMind系统中使用的数据结构，
包括场景信息、物体信息、用户意图、分割结果等。
"""

from typing import List, Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field
from enum import Enum
import numpy as np


class ObjectCategory(str, Enum):
    """物体类别枚举"""
    CUP = "杯子"
    SCISSORS = "剪刀"
    BOTTLE = "瓶子"
    KNIFE = "刀"
    FORK = "叉子"
    SPOON = "勺子"
    PLATE = "盘子"
    BOWL = "碗"
    BOOK = "书"
    PEN = "笔"
    PHONE = "手机"
    UNKNOWN = "未知物体"


class BoundingBox(BaseModel):
    """边界框数据结构"""
    x1: int = Field(..., description="左上角x坐标")
    y1: int = Field(..., description="左上角y坐标") 
    x2: int = Field(..., description="右下角x坐标")
    y2: int = Field(..., description="右下角y坐标")
    confidence: float = Field(default=1.0, description="检测置信度")
    
    def center(self) -> Tuple[int, int]:
        """计算边界框中心点"""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)
    
    def area(self) -> int:
        """计算边界框面积"""
        return (self.x2 - self.x1) * (self.y2 - self.y1)


class DetectedObject(BaseModel):
    """检测到的物体信息"""
    object_id: str = Field(..., description="物体唯一标识符")
    label: str = Field(..., description="物体标签/名称")
    category: ObjectCategory = Field(default=ObjectCategory.UNKNOWN, description="物体类别")
    bounding_box: BoundingBox = Field(..., description="边界框")
    confidence: float = Field(default=1.0, description="识别置信度")
    description: Optional[str] = Field(default=None, description="物体详细描述")
    
    class Config:
        """Pydantic配置"""
        use_enum_values = True


class SceneAnalysisResult(BaseModel):
    """场景分析结果"""
    image_path: str = Field(..., description="输入图像路径")
    objects: List[DetectedObject] = Field(default_factory=list, description="检测到的物体列表")
    total_objects: int = Field(default=0, description="物体总数")
    analysis_timestamp: str = Field(..., description="分析时间戳")
    
    def model_post_init(self, __context: Any) -> None:
        """模型初始化后处理"""
        self.total_objects = len(self.objects)


class UserIntent(BaseModel):
    """用户意图信息"""
    raw_instruction: str = Field(..., description="用户原始指令")
    intent_type: str = Field(..., description="意图类型（如：饮水、使用工具等）")
    target_object_id: Optional[str] = Field(default=None, description="目标物体ID")
    priority_level: int = Field(default=1, description="优先级（1-5）")
    safety_requirements: List[str] = Field(default_factory=list, description="安全要求列表")


class FunctionalPart(BaseModel):
    """功能性部件信息"""
    part_name: str = Field(..., description="部件名称")
    function: str = Field(..., description="部件功能描述")
    safety_score: float = Field(default=1.0, description="安全评分（0-1）")
    ergonomic_score: float = Field(default=1.0, description="人体工学评分（0-1）")
    grasp_priority: int = Field(default=1, description="抓取优先级（1-5）")


class InteractionStrategy(BaseModel):
    """交互策略信息"""
    target_object: DetectedObject = Field(..., description="目标物体")
    target_part: FunctionalPart = Field(..., description="目标功能部件")
    strategy_reasoning: str = Field(..., description="策略推理过程")
    safety_considerations: List[str] = Field(default_factory=list, description="安全考量")
    execution_instructions: str = Field(..., description="执行指令")


class SegmentationMask(BaseModel):
    """分割掩码数据结构"""
    mask_array: List[List[int]] = Field(..., description="二值掩码数组（0和1）")
    width: int = Field(..., description="掩码宽度")
    height: int = Field(..., description="掩码高度")
    target_object_id: str = Field(..., description="目标物体ID")
    target_part_name: str = Field(..., description="目标部件名称")
    mask_confidence: float = Field(default=1.0, description="掩码置信度")
    
    def to_numpy(self) -> np.ndarray:
        """转换为numpy数组"""
        return np.array(self.mask_array, dtype=np.uint8)
    
    @classmethod
    def from_numpy(cls, mask_np: np.ndarray, target_object_id: str, 
                   target_part_name: str, confidence: float = 1.0) -> 'SegmentationMask':
        """从numpy数组创建掩码"""
        height, width = mask_np.shape[:2]
        mask_list = mask_np.astype(int).tolist()
        
        return cls(
            mask_array=mask_list,
            width=width,
            height=height,
            target_object_id=target_object_id,
            target_part_name=target_part_name,
            mask_confidence=confidence
        )


class SegmentationResult(BaseModel):
    """分割结果"""
    image_path: str = Field(..., description="输入图像路径")
    mask: SegmentationMask = Field(..., description="分割掩码")
    strategy_used: InteractionStrategy = Field(..., description="使用的交互策略")
    processing_time: float = Field(..., description="处理时间（秒）")
    success: bool = Field(default=True, description="是否成功")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    output_mask_path: Optional[str] = Field(default=None, description="输出掩码图像路径")


class SystemConfig(BaseModel):
    """系统配置"""
    max_image_size: int = Field(default=1024, description="最大图像尺寸")
    supported_formats: List[str] = Field(
        default_factory=lambda: ["jpg", "jpeg", "png", "bmp"], 
        description="支持的图像格式"
    )
    vlm_model: str = Field(default="gpt-4o", description="视觉语言模型")
    llm_model: str = Field(default="gpt-4o-mini", description="语言模型")
    vlm_temperature: float = Field(default=0.0, description="VLM温度参数")
    llm_temperature: float = Field(default=0.7, description="LLM温度参数")
    log_level: str = Field(default="INFO", description="日志级别")


class ProcessingPipeline(BaseModel):
    """处理流水线状态"""
    stage: str = Field(..., description="当前阶段")
    completed_stages: List[str] = Field(default_factory=list, description="已完成阶段")
    current_data: Dict[str, Any] = Field(default_factory=dict, description="当前数据")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
