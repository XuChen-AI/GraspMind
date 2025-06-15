"""
GraspMind源代码模块

智能机械臂的面向人机交互功能性抓取系统
"""

from .core.pipeline import GraspMindPipeline
from .utils.config import ConfigManager
from .models.data_models import SegmentationResult

__version__ = "1.0.0"
__author__ = "GraspMind Team"

__all__ = [
    "GraspMindPipeline",
    "ConfigManager", 
    "SegmentationResult"
]
