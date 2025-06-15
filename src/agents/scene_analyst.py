"""
场景分析师智能体

负责分析输入图像，识别场景中的所有物体并返回结构化信息
"""

from typing import Dict, Any, List
from datetime import datetime

from crewai import Agent
from langchain_openai import ChatOpenAI
from loguru import logger

from ..models.data_models import DetectedObject, SceneAnalysisResult, BoundingBox, ObjectCategory
from ..tools.vision_tool import VisionAnalysisTool
from ..utils.model_client import ModelClient
from ..utils.image_utils import ImageProcessor


class SceneAnalyst:
    """
    场景分析师智能体
    
    专门负责图像场景分析，识别所有可见物体
    """
    
    def __init__(self, model_client: ModelClient, image_processor: ImageProcessor):
        """
        初始化场景分析师
        
        Args:
            model_client: 模型客户端
            image_processor: 图像处理器
        """
        self.model_client = model_client
        self.image_processor = image_processor
        self.vision_tool = VisionAnalysisTool(model_client, image_processor)
        
        # 创建CrewAI智能体
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        创建CrewAI智能体实例
        
        Returns:
            场景分析师智能体
        """
        # 创建LLM实例（这里使用一个包装器）
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0,
            api_key="dummy"  # 这里用dummy，实际由vision_tool处理
        )
        
        agent = Agent(
            role="图像场景分析专家 (Scene Analyst)",
            goal="""
            识别并列出图像中的所有主要物体及其边界框位置，以结构化的JSON格式输出场景信息。
            需要特别关注可能与人机交互相关的物体，如杯子、工具、餐具等。
            """,
            backstory="""
            你是一位经验丰富的计算机视觉专家，拥有敏锐的图像分析能力。
            你精通物体检测、定位和分类，能够快速准确地识别复杂场景中的各种物体。
            你的分析为后续的智能抓取决策提供了重要的基础信息。
            你总是以科学严谨的态度工作，确保检测结果的准确性和完整性。
            """,
            tools=[self.vision_tool],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
        return agent
    
    def analyze_scene(self, image_path: str) -> SceneAnalysisResult:
        """
        分析场景中的物体
        
        Args:
            image_path: 输入图像路径
            
        Returns:
            场景分析结果
        """
        try:
            logger.info(f"开始分析场景图像: {image_path}")
            
            # 验证图像质量
            image = self.image_processor.load_image(image_path)
            if image is None:
                raise Exception(f"无法加载图像: {image_path}")
            
            quality_info = self.image_processor.validate_image_quality(image)
            if not quality_info.get("is_good_quality", False):
                logger.warning(f"图像质量较低: {quality_info}")
            
            # 使用视觉工具检测物体
            detection_result = self.vision_tool._run("detect_objects", image_path)
            
            if not detection_result.get("success", False):
                error_msg = detection_result.get("error", "检测失败")
                raise Exception(error_msg)
            
            # 转换为标准数据结构
            objects = []
            for obj_data in detection_result.get("objects", []):
                try:
                    # 解析边界框
                    bbox_data = obj_data["bounding_box"]
                    bbox = BoundingBox(
                        x1=bbox_data["x1"],
                        y1=bbox_data["y1"], 
                        x2=bbox_data["x2"],
                        y2=bbox_data["y2"],
                        confidence=bbox_data.get("confidence", 1.0)
                    )
                    
                    # 解析物体类别
                    category = ObjectCategory(obj_data.get("category", ObjectCategory.UNKNOWN))
                    
                    # 创建检测物体
                    detected_obj = DetectedObject(
                        object_id=obj_data["object_id"],
                        label=obj_data["label"],
                        category=category,
                        bounding_box=bbox,
                        confidence=obj_data.get("confidence", 1.0),
                        description=obj_data.get("description")
                    )
                    
                    objects.append(detected_obj)
                    
                except Exception as e:
                    logger.warning(f"解析物体数据失败: {str(e)}")
                    continue
            
            # 创建场景分析结果
            scene_result = SceneAnalysisResult(
                image_path=image_path,
                objects=objects,
                analysis_timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"场景分析完成，检测到 {len(objects)} 个物体")
            
            # 输出检测摘要
            self._log_detection_summary(objects)
            
            return scene_result
            
        except Exception as e:
            logger.error(f"场景分析失败: {str(e)}")
            # 返回空结果但包含错误信息
            return SceneAnalysisResult(
                image_path=image_path,
                objects=[],
                analysis_timestamp=datetime.now().isoformat()
            )
    
    def _log_detection_summary(self, objects: List[DetectedObject]) -> None:
        """
        记录检测摘要
        
        Args:
            objects: 检测到的物体列表
        """
        if not objects:
            logger.info("未检测到任何物体")
            return
        
        logger.info("=== 场景分析摘要 ===")
        
        # 按类别统计
        category_count = {}
        for obj in objects:
            category = obj.category
            category_count[category] = category_count.get(category, 0) + 1
        
        for category, count in category_count.items():
            logger.info(f"{category}: {count}个")
        
        # 显示具体物体信息
        logger.info("=== 检测到的物体 ===")
        for obj in objects:
            center_x, center_y = obj.bounding_box.center()
            logger.info(f"- {obj.label} (ID: {obj.object_id}) "
                       f"位置: ({center_x}, {center_y}) "
                       f"置信度: {obj.confidence:.2f}")
    
    def get_objects_by_category(self, scene_result: SceneAnalysisResult, 
                               category: ObjectCategory) -> List[DetectedObject]:
        """
        根据类别筛选物体
        
        Args:
            scene_result: 场景分析结果
            category: 物体类别
            
        Returns:
            指定类别的物体列表
        """
        return [obj for obj in scene_result.objects if obj.category == category]
    
    def find_object_by_description(self, scene_result: SceneAnalysisResult, 
                                  keywords: List[str]) -> List[DetectedObject]:
        """
        根据描述关键词查找物体
        
        Args:
            scene_result: 场景分析结果
            keywords: 搜索关键词列表
            
        Returns:
            匹配的物体列表
        """
        matched_objects = []
        
        for obj in scene_result.objects:
            # 检查标签和描述中是否包含关键词
            text_to_search = f"{obj.label} {obj.description or ''}".lower()
            
            for keyword in keywords:
                if keyword.lower() in text_to_search:
                    matched_objects.append(obj)
                    break
        
        return matched_objects
    
    def validate_detection_quality(self, scene_result: SceneAnalysisResult) -> Dict[str, Any]:
        """
        验证检测质量
        
        Args:
            scene_result: 场景分析结果
            
        Returns:
            质量评估结果
        """
        total_objects = len(scene_result.objects)
        
        if total_objects == 0:
            return {
                "quality_score": 0,
                "confidence_avg": 0,
                "issues": ["未检测到任何物体"],
                "suggestions": ["检查图像质量", "调整照明条件", "重新拍摄图像"]
            }
        
        # 计算平均置信度
        avg_confidence = sum(obj.confidence for obj in scene_result.objects) / total_objects
        
        # 检查问题
        issues = []
        suggestions = []
        
        if avg_confidence < 0.7:
            issues.append("整体检测置信度较低")
            suggestions.append("提高图像清晰度")
        
        low_confidence_objects = [obj for obj in scene_result.objects if obj.confidence < 0.5]
        if low_confidence_objects:
            issues.append(f"{len(low_confidence_objects)}个物体置信度过低")
            suggestions.append("重新调整拍摄角度")
        
        # 计算质量分数
        quality_score = min(100, avg_confidence * 80 + (total_objects / 10) * 20)
        
        return {
            "quality_score": round(quality_score, 2),
            "confidence_avg": round(avg_confidence, 3),
            "total_objects": total_objects,
            "low_confidence_count": len(low_confidence_objects),
            "issues": issues,
            "suggestions": suggestions
        }
