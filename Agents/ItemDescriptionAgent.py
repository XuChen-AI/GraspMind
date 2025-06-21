"""
Item Description Agent - 物品描述AI代理模块
专注于图像中物品的详细描述
"""

import requests
import json
import base64
import yaml
import os
from typing import Optional, Dict, Any
from Message.InputMsg import InputMessage

ItemDescriptionAgentPrompt = {
    "user_requirements": "The image shows the current item, generally speaking, which simple parts make up this current item, output in the following format.Dictionary format",
    "output_format": '[{"Part Name": name, "Description": Description of less than 20 characters},...]',
    "Constraint": "Strictly output in the specified format, without any additional content."
    # "Current_Item": "cup" 
}


class ItemDescriptionAgent:
    """物品描述AI代理客户端"""
    
    def __init__(self, config_path: str = "Config/Config.yaml"):
        """
        初始化物品描述AI代理
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.api_key = self.config['ItemDescriptionAgent']['api_key']
        self.base_url = self.config['ItemDescriptionAgent']['base_url']
        self.model = self.config['ItemDescriptionAgent']['model']
        
        # 初始化prompt实例并设置全局变量的内容
        self.inputMessage = InputMessage()
        self.inputMessage.add_dict(ItemDescriptionAgentPrompt)
        
        # 验证API密钥
        if self.api_key == "YOUR_OPENROUTER_API_KEY":
            raise ValueError("请在Config/Config.yaml中设置正确的OpenRouter API密钥")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        将本地图片转换为base64格式
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的图片数据URL
        """
        with open(image_path, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode('utf-8')
            # 获取文件扩展名来确定MIME类型
            file_ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(file_ext, 'image/jpeg')
            
            return f"data:{mime_type};base64,{base64_string}"
    
    def set_image(self, image_path: str) -> None:
        """
        设置要描述的图片路径
        
        Args:
            image_path: 图片文件路径（支持本地路径或URL）
        """
        if not image_path:
            raise ValueError("图片路径不能为空")
        
        # 验证本地文件是否存在
        if not image_path.startswith(('http://', 'https://')):
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件 {image_path} 未找到")
        
        self.inputMessage.set_image(image_path)
    
    def ask_about_image(self) -> str:
        """
        对已设置的图片进行物品描述
        
        Returns:
            模型的回答文本
        """
        # 检查是否已设置图片
        if not self.inputMessage.image:
            raise ValueError("请先使用set_image()方法设置图片路径")
        
        # question从prompt实例中获取
        question = self.inputMessage.to_sentence()
        image_path = self.inputMessage.image
        print(f"🔍 发送问题: {question}")

        # 准备请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 添加可选的网站信息
        if 'site' in self.config:
            if 'url' in self.config['site']:
                headers["HTTP-Referer"] = self.config['site']['url']
            if 'name' in self.config['site']:
                headers["X-Title"] = self.config['site']['name']
        
        # 准备图片URL（支持本地文件和网络URL）
        if image_path.startswith(('http://', 'https://')):
            image_url = image_path
        else:
            # 本地文件转换为base64
            image_url = self._encode_image_to_base64(image_path)
        
        # 构建消息
        message_content = [
            {
                "type": "text",
                "text": question
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ]
        
        # 准备请求数据
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            "max_tokens": 2000,  # 限制返回长度
            "temperature": 0.7   # 控制回答的创造性
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
