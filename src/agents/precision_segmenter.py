"""
精准分割师智能体

负责对指定物体的特定部分进行精确的像素级分割
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json

from crewai import Agent
from langchain_openai import ChatOpenAI
from loguru import logger

from ..models.data_models import (
    InteractionStrategy, SegmentationMask, SegmentationResult
)
from ..tools.vision_tool import VisionAnalysisTool
from ..utils.model_client import ModelClient
from ..utils.image_utils import ImageProcessor


class PrecisionSegmenter:
    """
    精准分割师智能体
    
    专门负责对目标物体的功能性部件进行精确分割
    """
    
    def __init__(self, model_client: ModelClient, image_processor: ImageProcessor):
        """
        初始化精准分割师
        
        Args:
            model_client: 模型客户端
            image_processor: 图像处理器
        """
        self.model_client = model_client
        self.image_processor = image_processor
        self.vision_tool = VisionAnalysisTool(model_client, image_processor)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        创建CrewAI智能体实例
        
        Returns:
            精准分割师智能体
        """
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0,
            api_key="dummy"  # 实际由vision_tool处理
        )
        
        agent = Agent(
            role="视觉目标分割专家 (Precision Segmenter)",
            goal="""
            根据明确的指令，对指定物体的特定部分进行精确的像素级分割。
            生成高质量的二值掩码，为后续的抓取位姿生成提供准确的定位信息。
            """,
            backstory="""
            你是一位像素级的"手术刀"，是团队里的视觉执行专家。
            你拥有精湛的图像分割技术，能够在复杂的场景中准确识别和分割目标区域。
            你的工作就像外科医生一样精确，每一个像素的判断都关乎最终结果的成败。
            你深知分割质量的重要性，因为下游的抓取规划完全依赖于你的输出。
            你总是追求完美，不容忍任何模糊或不准确的分割边界。
            """,
            tools=[self.vision_tool],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
        return agent
    
    def segment_target_part(self, image_path: str, strategy: InteractionStrategy) -> SegmentationResult:
        """
        分割目标部件
        
        Args:
            image_path: 输入图像路径
            strategy: 交互策略
            
        Returns:
            分割结果
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"开始分割 {strategy.target_object.label} 的 {strategy.target_part.part_name}")
            
            # 验证输入
            if not self._validate_inputs(image_path, strategy):
                raise Exception("输入验证失败")
            
            # 执行分割
            segmentation_data = self._perform_segmentation(image_path, strategy)
            
            if not segmentation_data.get("success", False):
                error_msg = segmentation_data.get("error", "分割失败")
                raise Exception(error_msg)
            
            # 解析分割结果
            mask = self._parse_segmentation_mask(segmentation_data, strategy)
            
            # 验证分割质量
            quality_info = self._validate_segmentation_quality(mask)
            
            # 生成输出掩码图像
            output_path = self._save_segmentation_mask(image_path, mask)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 创建分割结果
            result = SegmentationResult(
                image_path=image_path,
                mask=mask,
                strategy_used=strategy,
                processing_time=processing_time,
                success=True,
                output_mask_path=output_path
            )
            
            logger.info(f"分割完成，耗时 {processing_time:.2f}秒")
            self._log_segmentation_summary(mask, quality_info)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"分割失败: {str(e)}")
            
            # 返回失败结果
            return SegmentationResult(
                image_path=image_path,
                mask=SegmentationMask(
                    mask_array=[],
                    width=0,
                    height=0,
                    target_object_id=strategy.target_object.object_id,
                    target_part_name=strategy.target_part.part_name
                ),
                strategy_used=strategy,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def _validate_inputs(self, image_path: str, strategy: InteractionStrategy) -> bool:
        """
        验证输入参数
        
        Args:
            image_path: 图像路径
            strategy: 交互策略
            
        Returns:
            是否有效
        """
        try:
            # 检查图像文件
            from pathlib import Path
            if not Path(image_path).exists():
                logger.error(f"图像文件不存在: {image_path}")
                return False
            
            # 检查策略完整性
            if not strategy.target_object or not strategy.target_part:
                logger.error("交互策略不完整")
                return False
            
            # 检查目标部件信息
            if not strategy.target_part.part_name:
                logger.error("目标部件名称为空")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"输入验证失败: {str(e)}")
            return False
    
    def _perform_segmentation(self, image_path: str, strategy: InteractionStrategy) -> Dict[str, Any]:
        """
        执行分割操作
        
        Args:
            image_path: 图像路径
            strategy: 交互策略
            
        Returns:
            分割数据
        """
        try:
            # 调用视觉工具执行分割
            result = self.vision_tool._run(
                operation="segment_part",
                image_path=image_path,
                target_object=strategy.target_object.label,
                target_part=strategy.target_part.part_name
            )
            
            return result
            
        except Exception as e:
            logger.error(f"分割操作失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_segmentation_mask(self, segmentation_data: Dict[str, Any], 
                                strategy: InteractionStrategy) -> SegmentationMask:
        """
        解析分割掩码
        
        Args:
            segmentation_data: 分割数据
            strategy: 交互策略
            
        Returns:
            分割掩码对象
        """
        try:
            mask_info = segmentation_data.get("mask", {})
            
            return SegmentationMask(
                mask_array=mask_info.get("mask_array", []),
                width=mask_info.get("width", 0),
                height=mask_info.get("height", 0),
                target_object_id=strategy.target_object.object_id,
                target_part_name=strategy.target_part.part_name,
                mask_confidence=mask_info.get("mask_confidence", 1.0)
            )
            
        except Exception as e:
            logger.error(f"分割掩码解析失败: {str(e)}")
            # 返回空掩码
            return SegmentationMask(
                mask_array=[],
                width=0,
                height=0,
                target_object_id=strategy.target_object.object_id,
                target_part_name=strategy.target_part.part_name,
                mask_confidence=0.0
            )
    
    def _validate_segmentation_quality(self, mask: SegmentationMask) -> Dict[str, Any]:
        """
        验证分割质量
        
        Args:
            mask: 分割掩码
            
        Returns:
            质量评估信息
        """
        try:
            if not mask.mask_array or mask.width == 0 or mask.height == 0:
                return {
                    "quality_score": 0,
                    "target_pixels": 0,
                    "coverage_ratio": 0,
                    "issues": ["掩码为空"],
                    "is_valid": False
                }
            
            # 统计目标像素
            target_pixels = sum(sum(row) for row in mask.mask_array)
            total_pixels = mask.width * mask.height
            coverage_ratio = target_pixels / total_pixels if total_pixels > 0 else 0
            
            # 评估质量
            issues = []
            if target_pixels == 0:
                issues.append("未检测到目标区域")
            elif coverage_ratio < 0.01:
                issues.append("目标区域过小")
            elif coverage_ratio > 0.8:
                issues.append("目标区域过大，可能包含背景")
            
            # 计算质量分数
            quality_score = min(100, mask.mask_confidence * 50 + 
                              min(coverage_ratio * 100, 50))
            
            return {
                "quality_score": round(quality_score, 2),
                "target_pixels": target_pixels,
                "total_pixels": total_pixels,
                "coverage_ratio": round(coverage_ratio, 4),
                "confidence": mask.mask_confidence,
                "issues": issues,
                "is_valid": target_pixels > 0 and len(issues) == 0
            }
            
        except Exception as e:
            logger.error(f"分割质量验证失败: {str(e)}")
            return {
                "quality_score": 0,
                "issues": [f"质量验证失败: {str(e)}"],
                "is_valid": False
            }
    
    def _save_segmentation_mask(self, image_path: str, mask: SegmentationMask) -> Optional[str]:
        """
        保存分割掩码
        
        Args:
            image_path: 原始图像路径
            mask: 分割掩码
            
        Returns:
            输出掩码文件路径
        """
        try:
            import numpy as np
            from pathlib import Path
            
            # 生成输出文件名
            input_path = Path(image_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{input_path.stem}_{mask.target_part_name}_{timestamp}.png"
            output_path = Path("output_masks") / output_filename
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换掩码为numpy数组
            mask_np = mask.to_numpy()
            
            # 保存掩码
            success = self.image_processor.save_mask(mask_np, output_path)
            
            if success:
                logger.info(f"掩码已保存: {output_path}")
                return str(output_path)
            else:
                logger.error("掩码保存失败")
                return None
                
        except Exception as e:
            logger.error(f"保存分割掩码失败: {str(e)}")
            return None
    
    def _log_segmentation_summary(self, mask: SegmentationMask, quality_info: Dict[str, Any]) -> None:
        """
        记录分割摘要
        
        Args:
            mask: 分割掩码
            quality_info: 质量信息
        """
        logger.info("=== 分割结果摘要 ===")
        logger.info(f"目标物体: {mask.target_object_id}")
        logger.info(f"目标部件: {mask.target_part_name}")
        logger.info(f"掩码尺寸: {mask.width} x {mask.height}")
        logger.info(f"目标像素: {quality_info.get('target_pixels', 0)}")
        logger.info(f"覆盖率: {quality_info.get('coverage_ratio', 0):.2%}")
        logger.info(f"质量分数: {quality_info.get('quality_score', 0):.1f}/100")
        logger.info(f"置信度: {mask.mask_confidence:.3f}")
        
        if quality_info.get("issues"):
            logger.warning(f"质量问题: {', '.join(quality_info['issues'])}")
        
        if quality_info.get("is_valid", False):
            logger.info("✅ 分割质量良好")
        else:
            logger.warning("⚠️ 分割质量需要改进")
    
    def create_visualization(self, image_path: str, mask: SegmentationMask, 
                           output_path: Optional[str] = None) -> Optional[str]:
        """
        创建分割可视化图像
        
        Args:
            image_path: 原始图像路径
            mask: 分割掩码
            output_path: 输出路径
            
        Returns:
            可视化图像路径
        """
        try:
            # 加载原始图像
            image = self.image_processor.load_image(image_path)
            if image is None:
                return None
            
            # 转换掩码为numpy数组
            mask_np = mask.to_numpy()
            
            # 创建覆盖图像
            overlay = self.image_processor.create_mask_overlay(
                image, mask_np, alpha=0.3, color=(255, 0, 0)
            )
            
            # 生成输出路径
            if output_path is None:
                from pathlib import Path
                input_path = Path(image_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{input_path.stem}_visualization_{timestamp}.png"
                output_path = Path("output_masks") / output_filename
            
            # 保存可视化图像
            import cv2
            cv2.imwrite(str(output_path), cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
            
            logger.info(f"可视化图像已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"创建可视化失败: {str(e)}")
            return None
