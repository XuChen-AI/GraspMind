"""
Object Detection Agent - 目标检测AI代理模块
支持使用qwen/qwen2.5-vl-32b-instruct:free模型进行图像理解和目标检测
"""

import requests
import json
import base64
import yaml
import os
from typing import Optional, Dict, Any
from Message.InputMsg import InputMessage
from Utiles.ImagePreprocessor import ImagePreprocessor

ObjectDetectionAgentPrompt = {
    "laguage": "English",
    "user_requirements": "Detect all items on the desktop and return their position in coordinate form.",
    "output_format": '[{"bbox_2d": [x1, y1, x2, y2], "label": Item name},...]',
    "Constraint": "Strictly output in the specified format, without any additional content."
}


class ObjectDetectionAgent:
    """目标检测AI代理客户端"""
    
    def __init__(self, config_path: str = "Config/Config.yaml"):
        """
        初始化目标检测AI代理
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.api_key = self.config['ObjectDetectionAgent']['api_key']
        self.base_url = self.config['ObjectDetectionAgent']['base_url']
        self.model = self.config['ObjectDetectionAgent']['model']
        
        # 初始化prompt实例并设置全局变量的内容
        self.inputMessage = InputMessage()
        self.inputMessage.add_dict(ObjectDetectionAgentPrompt)
        
        # 初始化图像预处理器
        self.image_preprocessor = ImagePreprocessor()
        self.scale_info = None  # 保存图像缩放信息
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
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        将本地图片转换为base64格式，使用ImagePreprocessor进行预处理
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的图片数据URL
        """
        try:
            # 使用ImagePreprocessor预处理图像
            processed_image, compressed_data, scale_info = self.image_preprocessor.preprocess_image(image_path)
            
            # 保存缩放信息用于后续坐标转换
            self.scale_info = scale_info
            
            # 将压缩后的数据转换为base64
            base64_string = base64.b64encode(compressed_data).decode('utf-8')
            
            return f"data:image/jpeg;base64,{base64_string}"
            
        except FileNotFoundError:
            raise FileNotFoundError(f"图片文件 {image_path} 未找到")
        except Exception as e:
            raise Exception(f"图片编码失败: {e}")
    
    def convert_coordinates_to_original(self, detection_results: list) -> list:
        """
        将检测结果的坐标转换回原图坐标
        
        Args:
            detection_results: 检测结果列表，每个元素包含bbox_2d和label
            
        Returns:
            转换后的检测结果列表
        """
        if self.scale_info is None:
            print("⚠️ 警告: 缺少缩放信息，无法转换坐标到原图")
            return detection_results
            
        converted_results = []
        for result in detection_results:
            if isinstance(result, dict) and 'bbox_2d' in result:
                # 转换坐标
                original_bbox = self.image_preprocessor.convert_coordinates_to_original(result['bbox_2d'])
                
                # 创建新的结果字典
                converted_result = result.copy()
                converted_result['bbox_2d'] = original_bbox
                converted_results.append(converted_result)
            else:
                converted_results.append(result)
                
        return converted_results
    
    def set_image(self, image_path: str) -> None:
        """
        设置要检测的图片路径
        
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
        对已设置的图片进行目标检测
        
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
        
        try:
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
                
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查网络连接或稍后重试")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("API密钥无效，请检查Config/Config.yaml中的api_key")
            elif response.status_code == 429:
                raise Exception("请求频率过高，请稍后重试")
            else:
                raise Exception(f"HTTP错误 {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
        except json.JSONDecodeError:
            raise Exception("API返回数据格式错误")
        except Exception as e:
            raise Exception(f"未知错误: {e}")
    
    def _clean_json_from_markdown(self, text: str) -> str:
        """从markdown代码块中提取JSON内容"""
        text = text.strip()
        
        # 移除markdown代码块标记
        if text.startswith('```json'):
            lines = text.split('\n')
            start_found = False
            json_lines = []
            
            for line in lines:
                if line.strip() == '```json':
                    start_found = True
                    continue
                elif line.strip() == '```' and start_found:
                    break
                elif start_found:
                    json_lines.append(line)
            
            text = '\n'.join(json_lines)
        elif text.startswith('```') and text.endswith('```'):
            text = text[3:-3].strip()
        
        return text

    def ask_about_image_with_coordinate_conversion(self) -> str:
        """
        对已设置的图片进行目标检测，并自动转换坐标到原图
        
        Returns:
            模型的回答文本（坐标已转换到原图）
        """
        # 获取原始检测结果
        raw_result = self.ask_about_image()
          # 尝试解析并转换坐标
        try:
            import json
            # 清理markdown格式
            cleaned_result = self._clean_json_from_markdown(raw_result)
            # 尝试解析JSON格式的检测结果
            detection_results = json.loads(cleaned_result)
            
            if isinstance(detection_results, list):
                # 转换坐标到原图
                converted_results = self.convert_coordinates_to_original(detection_results)
                return json.dumps(converted_results, ensure_ascii=False)
            else:
                print("⚠️ 警告: 检测结果格式不是预期的列表格式")
                return raw_result
                
        except json.JSONDecodeError:
            print("⚠️ 警告: 检测结果不是有效的JSON格式，返回原始结果")
            return raw_result
        except Exception as e:
            print(f"⚠️ 警告: 坐标转换时发生错误: {e}")
            return raw_result


