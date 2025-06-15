"""
交互策略师智能体

负责理解用户意图，制定安全的交互策略，决定应该抓取物体的哪个功能性部分
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from crewai import Agent
from langchain_openai import ChatOpenAI
from loguru import logger

from ..models.data_models import (
    SceneAnalysisResult, UserIntent, DetectedObject, 
    FunctionalPart, InteractionStrategy, ObjectCategory
)
from ..utils.model_client import ModelClient


class InteractionStrategist:
    """
    交互策略师智能体
    
    专门负责理解用户意图并制定安全的交互策略
    """
    
    def __init__(self, model_client: ModelClient):
        """
        初始化交互策略师
        
        Args:
            model_client: 模型客户端
        """
        self.model_client = model_client
        self.agent = self._create_agent()
        
        # 功能性部件知识库
        self.functional_parts_knowledge = self._build_functional_parts_knowledge()
    
    def _create_agent(self) -> Agent:
        """
        创建CrewAI智能体实例
        
        Returns:
            交互策略师智能体
        """
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key="dummy"  # 实际由model_client处理
        )
        
        agent = Agent(
            role="人机交互安全与策略规划师 (Interaction Strategist)",
            goal="""
            根据用户需求和场景信息，制定最佳的交互策略。
            决定应该抓取哪个物体的哪个功能性部分，确保操作安全、符合人体工学。
            """,
            backstory="""
            你是机器人团队的"智慧大脑"，一位深思熟虑的策略专家。
            你不仅能精准理解用户的语言表达和真实意图，更深谙人机交互中的安全准则。
            你具备丰富的常识知识，了解各种物体的功能性部件和正确的使用方式。
            你的每一个决策都以安全为第一要务，同时兼顾效率和用户体验。
            你总是能在复杂的场景中找到最优的解决方案。
            """,
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
        return agent
    
    def _build_functional_parts_knowledge(self) -> Dict[ObjectCategory, List[FunctionalPart]]:
        """
        构建功能性部件知识库
        
        Returns:
            功能性部件知识字典
        """
        knowledge = {
            ObjectCategory.CUP: [
                FunctionalPart(
                    part_name="杯柄",
                    function="提供安全的抓握点，避免接触热液体",
                    safety_score=0.95,
                    ergonomic_score=0.9,
                    grasp_priority=1
                ),
                FunctionalPart(
                    part_name="杯身",
                    function="容纳液体的主体部分",
                    safety_score=0.3,  # 可能烫手
                    ergonomic_score=0.5,
                    grasp_priority=3
                )
            ],
            ObjectCategory.SCISSORS: [
                FunctionalPart(
                    part_name="握柄",
                    function="手指插入的环形把手，提供安全抓握",
                    safety_score=0.9,
                    ergonomic_score=0.95,
                    grasp_priority=1
                ),
                FunctionalPart(
                    part_name="刀刃",
                    function="切割部分",
                    safety_score=0.1,  # 危险
                    ergonomic_score=0.1,
                    grasp_priority=5
                )
            ],
            ObjectCategory.KNIFE: [
                FunctionalPart(
                    part_name="刀柄",
                    function="手持部分，提供安全控制",
                    safety_score=0.85,
                    ergonomic_score=0.9,
                    grasp_priority=1
                ),
                FunctionalPart(
                    part_name="刀刃",
                    function="切割部分",
                    safety_score=0.05,  # 极其危险
                    ergonomic_score=0.1,
                    grasp_priority=5
                )
            ],
            ObjectCategory.BOTTLE: [
                FunctionalPart(
                    part_name="瓶颈",
                    function="便于抓握的细窄部分",
                    safety_score=0.9,
                    ergonomic_score=0.85,
                    grasp_priority=1
                ),
                FunctionalPart(
                    part_name="瓶身",
                    function="容纳液体的主体",
                    safety_score=0.7,
                    ergonomic_score=0.6,
                    grasp_priority=2
                )
            ]
        }
        
        return knowledge
    
    def analyze_user_intent(self, instruction: str, scene_result: SceneAnalysisResult) -> UserIntent:
        """
        分析用户意图
        
        Args:
            instruction: 用户指令
            scene_result: 场景分析结果
            
        Returns:
            用户意图分析结果
        """
        try:
            logger.info(f"分析用户意图: {instruction}")
            
            # 构建意图分析提示词
            prompt = self._build_intent_analysis_prompt(instruction, scene_result)
            
            # 调用LLM分析意图
            response = self.model_client.analyze_image(
                image_b64="",  # 纯文本分析，不需要图像
                prompt=prompt,
                response_format="json"
            )
            
            # 解析响应
            intent_data = self._parse_intent_response(response, instruction)
            
            logger.info(f"意图分析完成: {intent_data['intent_type']}")
            return intent_data
            
        except Exception as e:
            logger.error(f"用户意图分析失败: {str(e)}")
            # 返回默认意图
            return UserIntent(
                raw_instruction=instruction,
                intent_type="未知意图",
                priority_level=1,
                safety_requirements=["确保操作安全"]
            )
    
    def create_interaction_strategy(self, user_intent: UserIntent, 
                                   scene_result: SceneAnalysisResult) -> Optional[InteractionStrategy]:
        """
        制定交互策略
        
        Args:
            user_intent: 用户意图
            scene_result: 场景分析结果
            
        Returns:
            交互策略，如果无法制定则返回None
        """
        try:
            logger.info("开始制定交互策略")
            
            # 1. 选择目标物体
            target_object = self._select_target_object(user_intent, scene_result)
            if not target_object:
                logger.warning("未找到合适的目标物体")
                return None
            
            # 2. 选择功能性部件
            target_part = self._select_functional_part(target_object, user_intent)
            if not target_part:
                logger.warning("未找到合适的功能性部件")
                return None
            
            # 3. 生成策略推理
            reasoning = self._generate_strategy_reasoning(user_intent, target_object, target_part)
            
            # 4. 制定安全考量
            safety_considerations = self._generate_safety_considerations(target_object, target_part)
            
            # 5. 生成执行指令
            execution_instructions = self._generate_execution_instructions(target_object, target_part)
            
            # 创建交互策略
            strategy = InteractionStrategy(
                target_object=target_object,
                target_part=target_part,
                strategy_reasoning=reasoning,
                safety_considerations=safety_considerations,
                execution_instructions=execution_instructions
            )
            
            logger.info(f"交互策略制定完成: 抓取{target_object.label}的{target_part.part_name}")
            return strategy
            
        except Exception as e:
            logger.error(f"交互策略制定失败: {str(e)}")
            return None
    
    def _build_intent_analysis_prompt(self, instruction: str, scene_result: SceneAnalysisResult) -> str:
        """构建意图分析提示词"""
        objects_info = []
        for obj in scene_result.objects:
            objects_info.append(f"- {obj.label} (ID: {obj.object_id})")
        
        objects_text = "\n".join(objects_info) if objects_info else "无物体"
        
        return f"""
请分析用户的指令并理解其真实意图。

用户指令: "{instruction}"

场景中的物体:
{objects_text}

请分析用户的意图类型，并根据场景中的物体判断用户最可能想要操作哪个物体。

意图类型包括但不限于:
- 饮水: 想要喝水、口渴等
- 用餐: 想要吃东西、用餐具等  
- 写作: 想要写字、记录等
- 剪切: 想要剪纸、剪东西等
- 阅读: 想要看书、阅读等
- 通讯: 想要打电话、发消息等

请以JSON格式回复:
{{
    "intent_type": "意图类型",
    "target_object_id": "目标物体ID或null",
    "confidence": 置信度(0-1),
    "reasoning": "推理过程",
    "priority_level": 优先级(1-5),
    "safety_requirements": ["安全要求列表"]
}}
"""
    
    def _parse_intent_response(self, response: str, instruction: str) -> UserIntent:
        """解析意图分析响应"""
        try:
            import json
            data = json.loads(response)
            
            return UserIntent(
                raw_instruction=instruction,
                intent_type=data.get("intent_type", "未知意图"),
                target_object_id=data.get("target_object_id"),
                priority_level=data.get("priority_level", 1),
                safety_requirements=data.get("safety_requirements", [])
            )
        except:
            return UserIntent(
                raw_instruction=instruction,
                intent_type="解析失败",
                priority_level=1,
                safety_requirements=["确保操作安全"]
            )
    
    def _select_target_object(self, user_intent: UserIntent, 
                             scene_result: SceneAnalysisResult) -> Optional[DetectedObject]:
        """选择目标物体"""
        # 如果用户意图中已指定目标物体ID
        if user_intent.target_object_id:
            for obj in scene_result.objects:
                if obj.object_id == user_intent.target_object_id:
                    return obj
        
        # 根据意图类型匹配物体
        intent_to_category = {
            "饮水": [ObjectCategory.CUP, ObjectCategory.BOTTLE],
            "用餐": [ObjectCategory.FORK, ObjectCategory.SPOON, ObjectCategory.KNIFE],
            "剪切": [ObjectCategory.SCISSORS],
            "写作": [ObjectCategory.PEN],
            "阅读": [ObjectCategory.BOOK],
            "通讯": [ObjectCategory.PHONE]
        }
        
        target_categories = intent_to_category.get(user_intent.intent_type, [])
        
        # 查找匹配的物体
        for category in target_categories:
            for obj in scene_result.objects:
                if obj.category == category:
                    return obj
        
        # 如果没有找到匹配的类别，返回置信度最高的物体
        if scene_result.objects:
            return max(scene_result.objects, key=lambda x: x.confidence)
        
        return None
    
    def _select_functional_part(self, target_object: DetectedObject, 
                               user_intent: UserIntent) -> Optional[FunctionalPart]:
        """选择功能性部件"""
        # 从知识库获取可用部件
        available_parts = self.functional_parts_knowledge.get(target_object.category, [])
        
        if not available_parts:
            # 如果知识库中没有，创建一个默认部件
            return FunctionalPart(
                part_name="主体",
                function="物体的主要部分",
                safety_score=0.7,
                ergonomic_score=0.7,
                grasp_priority=1
            )
        
        # 选择最高优先级且安全的部件
        safe_parts = [part for part in available_parts if part.safety_score > 0.5]
        if safe_parts:
            return min(safe_parts, key=lambda x: x.grasp_priority)
        else:
            # 如果没有安全的部件，选择相对最安全的
            return max(available_parts, key=lambda x: x.safety_score)
    
    def _generate_strategy_reasoning(self, user_intent: UserIntent, 
                                   target_object: DetectedObject,
                                   target_part: FunctionalPart) -> str:
        """生成策略推理"""
        return f"""
基于用户意图"{user_intent.intent_type}"，选择抓取{target_object.label}来满足需求。
选择{target_part.part_name}作为抓取点，因为{target_part.function}。
该部件的安全评分为{target_part.safety_score:.2f}，人体工学评分为{target_part.ergonomic_score:.2f}，
确保了操作的安全性和舒适性。
"""
    
    def _generate_safety_considerations(self, target_object: DetectedObject,
                                      target_part: FunctionalPart) -> List[str]:
        """生成安全考量"""
        considerations = [
            f"抓取{target_part.part_name}以确保安全操作",
            "避免接触物体的危险部位",
            "确保抓取力度适中，避免损坏物体",
            "注意递送时的人体工学姿态"
        ]
        
        # 根据物体类别添加特殊安全考量
        if target_object.category == ObjectCategory.SCISSORS:
            considerations.extend([
                "绝对避免接触刀刃部分",
                "递送时刀尖朝下，握柄朝向用户"
            ])
        elif target_object.category == ObjectCategory.CUP:
            considerations.extend([
                "检查是否有热液体",
                "保持杯子水平，避免洒漏"
            ])
        elif target_object.category == ObjectCategory.KNIFE:
            considerations.extend([
                "严格避免接触刀刃",
                "递送时刀柄朝向用户，刀刃朝下"
            ])
        
        return considerations
    
    def _generate_execution_instructions(self, target_object: DetectedObject,
                                       target_part: FunctionalPart) -> str:
        """生成执行指令"""
        return f"""
目标物体: {target_object.label}
目标部件: {target_part.part_name}
抓取策略: 精确定位并分割{target_object.label}的{target_part.part_name}部分
安全要求: 确保抓取点安全可靠，符合人体工学设计
递送方式: 以适当的姿态将物体递给用户，确保用户能够安全接收
"""
