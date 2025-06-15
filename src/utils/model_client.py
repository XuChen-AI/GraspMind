"""
模型客户端模块

提供与各种AI模型的统一接口，支持OpenAI GPT-4o、千问VL等模型
"""

import json
import time
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

import requests
from loguru import logger


class BaseModelClient(ABC):
    """模型客户端基类"""
    
    @abstractmethod
    def analyze_image(self, image_b64: str, prompt: str, **kwargs) -> str:
        """分析图像"""
        pass


class OpenAIClient(BaseModelClient):
    """
    OpenAI模型客户端
    
    支持GPT-4o等具有视觉能力的模型
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", 
                 model: str = "gpt-4o", temperature: float = 0.0):
        """
        初始化OpenAI客户端
        
        Args:
            api_key: OpenAI API密钥
            base_url: API基础URL
            model: 使用的模型名称
            temperature: 温度参数
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_image(self, image_b64: str, prompt: str, 
                     response_format: str = "text", max_tokens: int = 2000) -> str:
        """
        使用OpenAI视觉模型分析图像
        
        Args:
            image_b64: base64编码的图像
            prompt: 分析提示词
            response_format: 响应格式 ("text" 或 "json")
            max_tokens: 最大响应长度
            
        Returns:
            模型响应文本
        """
        try:
            # 构建请求数据
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ]
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": self.temperature
            }
            
            # 如果需要JSON格式响应
            if response_format == "json":
                data["response_format"] = {"type": "json_object"}
                # 确保提示词中包含JSON要求
                if "json" not in prompt.lower():
                    messages[0]["content"][0]["text"] += "\n\n请确保响应为有效的JSON格式。"
            
            # 发送请求
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"OpenAI API请求失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # 解析响应
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 记录使用情况
            usage = result.get("usage", {})
            logger.info(f"OpenAI API调用成功 - 耗时: {processing_time:.2f}s, "
                       f"Token使用: {usage.get('total_tokens', 'N/A')}")
            
            return content
            
        except requests.exceptions.Timeout:
            error_msg = "OpenAI API请求超时"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"OpenAI API网络请求失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise


class QwenVLClient(BaseModelClient):
    """
    千问VL模型客户端
    
    支持通义千问视觉语言模型
    """
    
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/api/v1",
                 model: str = "qwen-vl-max", temperature: float = 0.0):
        """
        初始化千问VL客户端
        
        Args:
            api_key: 千问API密钥
            base_url: API基础URL
            model: 使用的模型名称
            temperature: 温度参数
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_image(self, image_b64: str, prompt: str, 
                     response_format: str = "text", max_tokens: int = 2000) -> str:
        """
        使用千问VL模型分析图像
        
        Args:
            image_b64: base64编码的图像
            prompt: 分析提示词
            response_format: 响应格式
            max_tokens: 最大响应长度
            
        Returns:
            模型响应文本
        """
        try:
            # 构建请求数据
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ]
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": self.temperature
            }
            
            # 发送请求
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"千问VL API请求失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # 解析响应
            result = response.json()
            content = result["output"]["choices"][0]["message"]["content"]
            
            # 记录使用情况
            usage = result.get("usage", {})
            logger.info(f"千问VL API调用成功 - 耗时: {processing_time:.2f}s, "
                       f"Token使用: {usage.get('total_tokens', 'N/A')}")
            
            return content
            
        except requests.exceptions.Timeout:
            error_msg = "千问VL API请求超时"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"千问VL API网络请求失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"千问VL API调用失败: {str(e)}")
            raise


class ModelClient:
    """
    统一的模型客户端
    
    根据配置自动选择合适的模型客户端
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化模型客户端
        
        Args:
            config: 配置字典
        """
        self.config = config
        self._client = self._create_client()
    
    def _create_client(self) -> BaseModelClient:
        """创建具体的客户端实例"""
        model_type = self.config.get("model_type", "openai")
        
        if model_type == "openai":
            return OpenAIClient(
                api_key=self.config["api_key"],
                base_url=self.config.get("base_url", "https://api.openai.com/v1"),
                model=self.config.get("model", "gpt-4o"),
                temperature=self.config.get("temperature", 0.0)
            )
        elif model_type == "qwen":
            return QwenVLClient(
                api_key=self.config["api_key"],
                base_url=self.config.get("base_url", "https://dashscope.aliyuncs.com/api/v1"),
                model=self.config.get("model", "qwen-vl-max"),
                temperature=self.config.get("temperature", 0.0)
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    def analyze_image(self, image_b64: str, prompt: str, **kwargs) -> str:
        """
        分析图像
        
        Args:
            image_b64: base64编码的图像
            prompt: 分析提示词
            **kwargs: 其他参数
            
        Returns:
            模型响应文本
        """
        return self._client.analyze_image(image_b64, prompt, **kwargs)
    
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            连接是否正常
        """
        try:
            # 使用一个简单的测试图像（1x1像素的白色图像）
            test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            test_prompt = "这是一个测试。请简单回复'测试成功'。"
            
            response = self._client.analyze_image(test_image_b64, test_prompt)
            
            logger.info("模型连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"模型连接测试失败: {str(e)}")
            return False
