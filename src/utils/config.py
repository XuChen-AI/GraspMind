"""
配置管理模块

负责系统配置的加载、验证和管理
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from ..models.data_models import SystemConfig


class ConfigManager:
    """
    配置管理器
    
    负责加载和管理系统配置
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            env_file: 环境变量文件路径
        """
        self.env_file = env_file or ".env"
        self.config = self._load_config()
    
    def _load_config(self) -> SystemConfig:
        """
        加载系统配置
        
        Returns:
            系统配置对象
        """
        # 加载环境变量
        if Path(self.env_file).exists():
            load_dotenv(self.env_file)
            logger.info(f"已加载环境变量文件: {self.env_file}")
        else:
            logger.warning(f"环境变量文件不存在: {self.env_file}")
        
        # 构建配置
        config = SystemConfig(
            max_image_size=int(os.getenv("IMAGE_MAX_SIZE", "1024")),
            supported_formats=os.getenv("SUPPORTED_FORMATS", "jpg,jpeg,png,bmp").split(","),
            vlm_model=os.getenv("DEFAULT_VLM_MODEL", "gpt-4o"),
            llm_model=os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini"),
            vlm_temperature=float(os.getenv("VLM_TEMPERATURE", "0.0")),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        logger.info("系统配置加载完成")
        return config
    
    def get_model_config(self, model_type: str = "vlm") -> Dict[str, Any]:
        """
        获取模型配置
        
        Args:
            model_type: 模型类型 ("vlm" 或 "llm")
            
        Returns:
            模型配置字典
        """
        # 确定使用的模型
        if model_type == "vlm":
            model_name = self.config.vlm_model
            temperature = self.config.vlm_temperature
        else:
            model_name = self.config.llm_model
            temperature = self.config.llm_temperature
        
        # 根据模型名称确定配置
        if "gpt" in model_name.lower():
            return {
                "model_type": "openai",
                "model": model_name,
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "temperature": temperature
            }
        elif "qwen" in model_name.lower():
            return {
                "model_type": "qwen", 
                "model": model_name,
                "api_key": os.getenv("QWEN_API_KEY"),
                "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"),
                "temperature": temperature
            }
        else:
            raise ValueError(f"不支持的模型: {model_name}")
    
    def validate_config(self) -> bool:
        """
        验证配置完整性
        
        Returns:
            配置是否有效
        """
        try:
            # 检查必要的API密钥
            vlm_config = self.get_model_config("vlm")
            llm_config = self.get_model_config("llm")
            
            if not vlm_config.get("api_key"):
                logger.error("VLM模型API密钥未配置")
                return False
            
            if not llm_config.get("api_key"):
                logger.error("LLM模型API密钥未配置")
                return False
            
            # 检查目录
            required_dirs = ["input_images", "output_masks", "logs"]
            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"创建目录: {dir_path}")
            
            logger.info("配置验证通过")
            return True
            
        except Exception as e:
            logger.error(f"配置验证失败: {str(e)}")
            return False
    
    def get_directories(self) -> Dict[str, Path]:
        """
        获取系统目录配置
        
        Returns:
            目录路径字典
        """
        return {
            "input": Path("input_images"),
            "output": Path("output_masks"),
            "logs": Path("logs"),
            "src": Path("src")
        }
    
    def update_config(self, **kwargs) -> None:
        """
        更新配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"更新配置: {key} = {value}")
            else:
                logger.warning(f"未知配置项: {key}")
    
    def get_log_config(self) -> Dict[str, Any]:
        """
        获取日志配置
        
        Returns:
            日志配置字典
        """
        log_file = os.getenv("LOG_FILE", "logs/graspmind.log")
        log_level = self.config.log_level
        
        return {
            "level": log_level,
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            "rotation": "10 MB",
            "retention": "7 days",
            "file": log_file
        }
