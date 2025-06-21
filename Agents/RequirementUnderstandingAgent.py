"""
Requirement Understanding Agent - 需求理解AI代理模块
支持使用deepseek/deepseek-chat:free模型进行用户需求分析和理解
"""

import requests
import json
import yaml
import os
from typing import Optional, Dict, Any, List
from Message.InputMsg import InputMessage

RequirementUnderstandingAgentPrompt = {
    "user_requirements": "I'm a bit thirsty",
    "output_format": '[{"Items needed": items name}]',
    "Constraint": "Strictly output in the specified format, without any additional content.",
    # "items": '["Water cup", "spoon", "notebook", "glasses", "book"]'
}


class RequirementUnderstandingAgent:
    """需求理解AI代理客户端"""
    
    def __init__(self, config_path: str = "Config/Config.yaml"):
        """
        初始化需求理解AI代理
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.api_key = self.config['RequirementUnderstandingAgent']['api_key']
        self.base_url = self.config['RequirementUnderstandingAgent']['base_url']
        self.model = self.config['RequirementUnderstandingAgent']['model']
        
        # 初始化prompt实例并设置全局变量的内容
        self.inputMessage = InputMessage()
        self.inputMessage.add_dict(RequirementUnderstandingAgentPrompt)
        
        # 验证API密钥
        if self.api_key == "YOUR_OPENROUTER_API_KEY":
            raise ValueError("请在Config/Config.yaml中设置正确的OpenRouter API密钥")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {config_path} 未找到")
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")    
    def understand_requirement(self) -> str:
        """
        理解和分析用户需求
        
        Returns:
            需求分析结果
        """
        # 使用InputMessage中的prompt
        question = self.inputMessage.to_sentence()
        print(f"🔍 发送问题: {question}")
        
        # 准备请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        
        # 准备请求数据
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ],
            "max_tokens": self.config['RequirementUnderstandingAgent'].get('max_tokens', 2000),
            "temperature": self.config['RequirementUnderstandingAgent'].get('temperature', 0.7)
        }
        
        # 发送请求
        response = requests.post(
            self.base_url,
            headers=headers,
            data=json.dumps(data),
            timeout=60  # 60秒超时
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            raise Exception("API返回格式异常：未找到回答内容")

