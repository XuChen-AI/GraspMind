"""
GraspMind核心流水线

协调三个智能体完成从图像输入到分割掩码输出的完整流程
"""

import time
from typing import Optional, Dict, Any
from pathlib import Path

from loguru import logger

from ..models.data_models import (
    SceneAnalysisResult, UserIntent, InteractionStrategy, 
    SegmentationResult, ProcessingPipeline
)
from ..agents.scene_analyst import SceneAnalyst
from ..agents.interaction_strategist import InteractionStrategist
from ..agents.precision_segmenter import PrecisionSegmenter
from ..utils.config import ConfigManager
from ..utils.model_client import ModelClient
from ..utils.image_utils import ImageProcessor


class GraspMindPipeline:
    """
    GraspMind主流水线
    
    协调三个智能体按顺序执行任务：
    1. 场景分析师 - 识别场景中的物体
    2. 交互策略师 - 理解用户意图并制定策略
    3. 精准分割师 - 分割目标物体的功能性部件
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化GraspMind流水线
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.config = config_manager.config
        
        # 初始化工具组件
        self._initialize_components()
        
        # 初始化智能体
        self._initialize_agents()
        
        logger.info("GraspMind流水线初始化完成")
    
    def _initialize_components(self) -> None:
        """初始化基础组件"""
        try:
            # 创建图像处理器
            self.image_processor = ImageProcessor(
                max_size=self.config.max_image_size,
                supported_formats=self.config.supported_formats
            )
            
            # 创建VLM客户端（用于视觉任务）
            vlm_config = self.config_manager.get_model_config("vlm")
            self.vlm_client = ModelClient(vlm_config)
            
            # 创建LLM客户端（用于推理任务）
            llm_config = self.config_manager.get_model_config("llm")
            self.llm_client = ModelClient(llm_config)
            
            logger.info("基础组件初始化完成")
            
        except Exception as e:
            logger.error(f"基础组件初始化失败: {str(e)}")
            raise
    
    def _initialize_agents(self) -> None:
        """初始化智能体"""
        try:
            # 场景分析师（使用VLM）
            self.scene_analyst = SceneAnalyst(
                model_client=self.vlm_client,
                image_processor=self.image_processor
            )
            
            # 交互策略师（使用LLM）
            self.interaction_strategist = InteractionStrategist(
                model_client=self.llm_client
            )
            
            # 精准分割师（使用VLM）
            self.precision_segmenter = PrecisionSegmenter(
                model_client=self.vlm_client,
                image_processor=self.image_processor
            )
            
            logger.info("智能体初始化完成")
            
        except Exception as e:
            logger.error(f"智能体初始化失败: {str(e)}")
            raise
    
    def process(self, image_path: str, user_instruction: str) -> SegmentationResult:
        """
        执行完整的处理流程
        
        Args:
            image_path: 输入图像路径
            user_instruction: 用户指令
            
        Returns:
            分割结果
        """
        start_time = time.time()
        
        # 创建流水线状态跟踪
        pipeline = ProcessingPipeline(
            stage="初始化",
            completed_stages=[],
            current_data={}
        )
        
        try:
            logger.info("=" * 60)
            logger.info("🚀 开始GraspMind处理流程")
            logger.info(f"📸 输入图像: {image_path}")
            logger.info(f"💬 用户指令: {user_instruction}")
            logger.info("=" * 60)
            
            # 验证输入
            if not self._validate_inputs(image_path, user_instruction):
                raise Exception("输入验证失败")
            
            # 阶段1: 场景分析
            scene_result = self._stage_scene_analysis(image_path, pipeline)
            
            # 阶段2: 意图理解与策略制定
            strategy = self._stage_strategy_planning(user_instruction, scene_result, pipeline)
            
            # 阶段3: 精准分割
            segmentation_result = self._stage_precision_segmentation(image_path, strategy, pipeline)
            
            # 记录总耗时
            total_time = time.time() - start_time
            
            logger.info("=" * 60)
            logger.info("✅ GraspMind处理流程完成")
            logger.info(f"⏱️ 总耗时: {total_time:.2f}秒")
            logger.info(f"🎯 输出掩码: {segmentation_result.output_mask_path}")
            logger.info("=" * 60)
            
            return segmentation_result
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error("=" * 60)
            logger.error("❌ GraspMind处理流程失败")
            logger.error(f"⏱️ 失败耗时: {total_time:.2f}秒")
            logger.error(f"🚫 错误信息: {str(e)}")
            logger.error("=" * 60)
            
            # 返回失败结果
            from ..models.data_models import SegmentationMask, InteractionStrategy, DetectedObject, FunctionalPart
            
            dummy_strategy = InteractionStrategy(
                target_object=DetectedObject(
                    object_id="error",
                    label="错误", 
                    bounding_box=None,
                    category="未知"
                ),
                target_part=FunctionalPart(
                    part_name="错误",
                    function="错误"
                ),
                strategy_reasoning="处理失败",
                execution_instructions="无法执行"
            )
            
            return SegmentationResult(
                image_path=image_path,
                mask=SegmentationMask(
                    mask_array=[],
                    width=0,
                    height=0,
                    target_object_id="error",
                    target_part_name="error"
                ),
                strategy_used=dummy_strategy,
                processing_time=total_time,
                success=False,
                error_message=str(e)
            )
    
    def _validate_inputs(self, image_path: str, user_instruction: str) -> bool:
        """
        验证输入参数
        
        Args:
            image_path: 图像路径
            user_instruction: 用户指令
            
        Returns:
            是否有效
        """
        try:
            # 检查图像文件
            path = Path(image_path)
            if not path.exists():
                logger.error(f"图像文件不存在: {image_path}")
                return False
            
            if not path.is_file():
                logger.error(f"路径不是文件: {image_path}")
                return False
            
            # 检查文件格式
            if path.suffix.lower().lstrip('.') not in self.config.supported_formats:
                logger.error(f"不支持的图像格式: {path.suffix}")
                return False
            
            # 检查用户指令
            if not user_instruction or not user_instruction.strip():
                logger.error("用户指令不能为空")
                return False
            
            logger.info("✅ 输入验证通过")
            return True
            
        except Exception as e:
            logger.error(f"输入验证失败: {str(e)}")
            return False
    
    def _stage_scene_analysis(self, image_path: str, pipeline: ProcessingPipeline) -> SceneAnalysisResult:
        """
        阶段1: 场景分析
        
        Args:
            image_path: 图像路径
            pipeline: 流水线状态
            
        Returns:
            场景分析结果
        """
        logger.info("🔍 [阶段1] 开始场景分析...")
        pipeline.stage = "场景分析"
        
        try:
            # 执行场景分析
            scene_result = self.scene_analyst.analyze_scene(image_path)
            
            # 验证结果
            if not scene_result.objects:
                logger.warning("⚠️ 未检测到任何物体")
            else:
                logger.info(f"✅ 检测到 {len(scene_result.objects)} 个物体")
            
            # 更新流水线状态
            pipeline.completed_stages.append("场景分析")
            pipeline.current_data["scene_result"] = scene_result
            
            return scene_result
            
        except Exception as e:
            pipeline.errors.append(f"场景分析失败: {str(e)}")
            logger.error(f"❌ 场景分析失败: {str(e)}")
            raise
    
    def _stage_strategy_planning(self, user_instruction: str, scene_result: SceneAnalysisResult,
                               pipeline: ProcessingPipeline) -> InteractionStrategy:
        """
        阶段2: 策略规划
        
        Args:
            user_instruction: 用户指令
            scene_result: 场景分析结果
            pipeline: 流水线状态
            
        Returns:
            交互策略
        """
        logger.info("🧠 [阶段2] 开始意图理解与策略规划...")
        pipeline.stage = "策略规划"
        
        try:
            # 分析用户意图
            user_intent = self.interaction_strategist.analyze_user_intent(
                instruction=user_instruction,
                scene_result=scene_result
            )
            
            logger.info(f"💭 用户意图: {user_intent.intent_type}")
            
            # 制定交互策略
            strategy = self.interaction_strategist.create_interaction_strategy(
                user_intent=user_intent,
                scene_result=scene_result
            )
            
            if not strategy:
                raise Exception("无法制定有效的交互策略")
            
            logger.info(f"✅ 策略制定完成: 抓取 {strategy.target_object.label} 的 {strategy.target_part.part_name}")
            
            # 更新流水线状态
            pipeline.completed_stages.append("策略规划")
            pipeline.current_data["user_intent"] = user_intent
            pipeline.current_data["strategy"] = strategy
            
            return strategy
            
        except Exception as e:
            pipeline.errors.append(f"策略规划失败: {str(e)}")
            logger.error(f"❌ 策略规划失败: {str(e)}")
            raise
    
    def _stage_precision_segmentation(self, image_path: str, strategy: InteractionStrategy,
                                    pipeline: ProcessingPipeline) -> SegmentationResult:
        """
        阶段3: 精准分割
        
        Args:
            image_path: 图像路径
            strategy: 交互策略
            pipeline: 流水线状态
            
        Returns:
            分割结果
        """
        logger.info("✂️ [阶段3] 开始精准分割...")
        pipeline.stage = "精准分割"
        
        try:
            # 执行分割
            segmentation_result = self.precision_segmenter.segment_target_part(
                image_path=image_path,
                strategy=strategy
            )
            
            if not segmentation_result.success:
                raise Exception(segmentation_result.error_message or "分割失败")
            
            logger.info(f"✅ 分割完成: {segmentation_result.output_mask_path}")
            
            # 更新流水线状态
            pipeline.completed_stages.append("精准分割")
            pipeline.current_data["segmentation_result"] = segmentation_result
            
            return segmentation_result
            
        except Exception as e:
            pipeline.errors.append(f"精准分割失败: {str(e)}")
            logger.error(f"❌ 精准分割失败: {str(e)}")
            raise
    
    def test_system(self) -> bool:
        """
        测试系统连接和配置
        
        Returns:
            测试是否通过
        """
        logger.info("🧪 开始系统测试...")
        
        try:
            # 测试配置
            if not self.config_manager.validate_config():
                logger.error("❌ 配置验证失败")
                return False
            
            # 测试模型连接
            if not self.vlm_client.test_connection():
                logger.error("❌ VLM模型连接失败")
                return False
            
            if not self.llm_client.test_connection():
                logger.error("❌ LLM模型连接失败")
                return False
            
            logger.info("✅ 系统测试通过")
            return True
            
        except Exception as e:
            logger.error(f"❌ 系统测试失败: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            系统状态信息
        """
        return {
            "version": "1.0.0",
            "status": "运行中",
            "config": {
                "vlm_model": self.config.vlm_model,
                "llm_model": self.config.llm_model,
                "max_image_size": self.config.max_image_size,
                "supported_formats": self.config.supported_formats
            },
            "components": {
                "scene_analyst": "已加载",
                "interaction_strategist": "已加载", 
                "precision_segmenter": "已加载"
            }
        }
