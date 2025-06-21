"""
检测结果可视化工具模块
将检测结果可视化到原始图片上
"""

import json
import cv2
import numpy as np
import os
import colorsys
from pathlib import Path
from typing import List, Dict, Any, Optional


class DetectionVisualizer:
    """检测结果可视化类"""
    
    def __init__(self):
        """初始化可视化器"""
        self.colors = []
        self._generate_colors(20)  # 生成20种不同的颜色
    
    def _generate_colors(self, num_colors: int):
        """生成不同的颜色用于标注不同的对象"""
        for i in range(num_colors):
            hue = i / num_colors
            saturation = 0.8
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)            # 转换为BGR格式（OpenCV使用BGR）
            color = (int(rgb[2] * 255), int(rgb[1] * 255), int(rgb[0] * 255))
            self.colors.append(color)
    
    def load_detection_results(self, json_path: str) -> List[Dict[str, Any]]:
        """
        加载检测结果JSON文件
        
        Args:
            json_path: 检测结果JSON文件路径
            
        Returns:
            检测结果列表
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
              # 处理不同的数据格式
            if isinstance(results, list):
                # 直接是列表格式
                print(f"成功加载检测结果，共 {len(results)} 个对象")
                return results
            elif isinstance(results, dict):
                # 字典格式，查找检测或分割结果
                if 'detection_results' in results:
                    detections = results['detection_results']
                    print(f"成功加载检测结果，共 {len(detections)} 个对象")
                    return detections
                elif 'segmentation_results' in results:
                    detections = results['segmentation_results']
                    print(f"成功加载分割结果，共 {len(detections)} 个对象")
                    return detections
                else:
                    # 假设整个字典就是单个检测结果
                    print("成功加载检测结果，共 1 个对象")
                    return [results]
            else:
                print(f"警告：未知的数据格式: {type(results)}")
                return []
                
        except FileNotFoundError:
            print(f"错误：找不到检测结果文件 {json_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"错误：JSON文件格式错误 - {e}")
            return []
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        加载原始图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            图片数组，如果加载失败返回None
        """
        if not os.path.exists(image_path):
            print(f"错误：找不到图片文件 {image_path}")
            return None
        
        image = cv2.imread(image_path)
        if image is None:
            print(f"错误：无法读取图片文件 {image_path}")
            return None
        
        print(f"成功加载图片，尺寸: {image.shape[1]}x{image.shape[0]}")
        return image
    
    def draw_bounding_boxes(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """
        在图片上绘制边界框和标签
        
        Args:
            image: 原始图片
            detections: 检测结果列表
            
        Returns:
            绘制了标注的图片
        """
        # 复制图片以避免修改原始图片
        annotated_image = image.copy()
        
        for i, detection in enumerate(detections):
            # 获取边界框坐标
            bbox = detection.get('bbox_2d', [])
            label = detection.get('label', 'Unknown')
            
            if len(bbox) != 4:
                print(f"警告：检测结果 {i} 的边界框格式不正确: {bbox}")
                continue
            
            x1, y1, x2, y2 = bbox
            
            # 确保坐标在图片范围内
            h, w = annotated_image.shape[:2]
            x1 = max(0, min(x1, w-1))
            y1 = max(0, min(y1, h-1))
            x2 = max(0, min(x2, w-1))
            y2 = max(0, min(y2, h-1))
            
            # 选择颜色
            color = self.colors[i % len(self.colors)]
            
            # 绘制边界框
            thickness = 2
            cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
            
            # 准备标签文本
            label_text = f"{i+1}: {label}"
            
            # 计算文本尺寸
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            text_thickness = 1
            (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, text_thickness)
            
            # 绘制标签背景
            label_y = max(int(y1), text_height + 5)
            cv2.rectangle(annotated_image, 
                         (int(x1), label_y - text_height - 5), 
                         (int(x1) + text_width + 5, label_y + baseline), 
                         color, -1)
            
            # 绘制标签文本
            cv2.putText(annotated_image, label_text, 
                       (int(x1) + 2, label_y - 2), 
                       font, font_scale, (255, 255, 255), text_thickness)
            
            print(f"绘制对象 {i+1}: {label} at [{x1}, {y1}, {x2}, {y2}]")
        
        return annotated_image
    
    def save_result(self, image: np.ndarray, output_path: str) -> bool:
        """
        保存标注后的图片
        
        Args:
            image: 标注后的图片
            output_path: 输出文件路径
            
        Returns:
            是否保存成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存图片
            success = cv2.imwrite(output_path, image)
            if success:
                print(f"成功保存标注图片到: {output_path}")
                return True
            else:
                print(f"错误：保存图片失败 {output_path}")
                return False
        except Exception as e:
            print(f"错误：保存图片时发生异常 - {e}")
            return False
    
    def create_summary_text(self, detections: List[Dict[str, Any]], output_dir: str):
        """
        创建检测结果汇总文本文件
        
        Args:
            detections: 检测结果列表
            output_dir: 输出目录
        """
        summary_path = os.path.join(output_dir, "detection_summary.txt")
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("检测结果汇总\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"总计检测到 {len(detections)} 个对象:\n\n")
                
                for i, detection in enumerate(detections):
                    bbox = detection.get('bbox_2d', [])
                    label = detection.get('label', 'Unknown')
                    
                    f.write(f"{i+1:2d}. {label}\n")
                    if len(bbox) == 4:
                        x1, y1, x2, y2 = bbox
                        width = x2 - x1
                        height = y2 - y1
                        f.write(f"    位置: ({x1}, {y1}) - ({x2}, {y2})\n")
                        f.write(f"    尺寸: {width} x {height} 像素\n")
                    f.write("\n")                
                # 统计各类别数量
                label_counts = {}
                for detection in detections:
                    label = detection.get('label', 'Unknown')
                    label_counts[label] = label_counts.get(label, 0) + 1
                
                f.write("各类别统计:\n")
                f.write("-" * 30 + "\n")
                for label, count in sorted(label_counts.items()):
                    f.write(f"{label}: {count} 个\n")
            
            print(f"成功创建检测结果汇总: {summary_path}")
            
        except Exception as e:
            print(f"错误：创建汇总文件时发生异常 - {e}")
    
    def visualize(self, json_path: str, image_path: str, output_dir: Optional[str] = None) -> bool:
        """
        完整的可视化流程
        
        Args:
            json_path: 检测结果JSON文件路径
            image_path: 原始图片路径
            output_dir: 输出目录，如果为None则使用JSON文件所在目录
            
        Returns:
            是否成功完成可视化
        """
        # 如果没有指定输出目录，使用JSON文件所在目录
        if output_dir is None:
            output_dir = os.path.dirname(json_path)
        
        print(f"开始可视化处理...")
        print(f"检测结果文件: {json_path}")
        print(f"原始图片: {image_path}")
        print(f"输出目录: {output_dir}")
        print("-" * 50)
        
        # 加载检测结果
        detections = self.load_detection_results(json_path)
        if not detections:
            return False
        
        # 加载图片
        image = self.load_image(image_path)
        if image is None:
            return False
        
        # 绘制标注
        annotated_image = self.draw_bounding_boxes(image, detections)
        
        # 生成输出文件名
        image_name = Path(image_path).stem
        output_image_path = os.path.join(output_dir, f"{image_name}_annotated.jpg")
        
        # 保存标注图片
        success = self.save_result(annotated_image, output_image_path)
        if not success:
            return False
        
        # 创建汇总文件
        self.create_summary_text(detections, output_dir)
        
        print("-" * 50)
        print("可视化完成！")
        return True


class VisualizationManager:
    """可视化管理器"""
    
    def __init__(self):
        """初始化可视化管理器"""
        self.visualizer = DetectionVisualizer()
    def quick_visualize(self, json_path: str = None, image_path: str = None) -> bool:
        """
        快速可视化 - 使用默认路径
        
        Args:
            json_path: JSON文件路径，None则使用默认
            image_path: 图片路径，None则使用默认
            
        Returns:
            是否成功
        """
        # 默认路径
        if json_path is None:
            json_path = "Output/000Run/detection_results.json"
        if image_path is None:
            image_path = "InputPicture/test.png"
        
        # 检查文件
        if not os.path.exists(json_path):
            print(f"❌ 检测结果文件不存在: {json_path}")
            return False
        
        if not os.path.exists(image_path):
            print(f"❌ 原始图片文件不存在: {image_path}")
            return False
        
        print("✅ 找到输入文件，开始处理...")
        
        # 执行可视化
        try:
            success = self.visualizer.visualize(json_path, image_path)
            
            if success:
                print("\n🎉 可视化完成！")
                output_dir = os.path.dirname(json_path)
                print(f"📁 输出目录: {output_dir}")
                print("📄 生成的文件:")
                image_name = Path(image_path).stem
                print(f"   - {image_name}_annotated.jpg (标注图片)")
                print("   - detection_summary.txt (检测汇总)")
                return True
            else:
                print("\n❌ 可视化失败")
                return False
                
        except ImportError as e:
            print(f"\n❌ 缺少依赖包: {e}")
            print("请运行: pip install opencv-python numpy")
            return False
        except Exception as e:
            print(f"\n❌ 处理过程中发生错误: {e}")
            return False


# 便捷函数
def quick_visualize(json_path: str = None, image_path: str = None) -> bool:
    """便捷函数：快速可视化"""
    manager = VisualizationManager()
    return manager.quick_visualize(json_path, image_path)

def visualize_detection_results(json_path: str, image_path: str, output_dir: str = None) -> bool:
    """便捷函数：可视化检测结果"""
    visualizer = DetectionVisualizer()
    return visualizer.visualize(json_path, image_path, output_dir)
