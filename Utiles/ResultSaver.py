"""
结果保存工具模块
提供各种格式的结果保存功能
"""

import os
import json
import re
from typing import Optional, Dict, Any


class ResultSaver:
    """结果保存工具类"""
    
    def __init__(self, output_base_dir: str = "Output"):
        """
        初始化结果保存器
        
        Args:
            output_base_dir: 输出基础目录
        """
        self.output_base_dir = output_base_dir
    
    def get_next_run_number(self) -> int:
        """获取下一个运行序号"""
        if not os.path.exists(self.output_base_dir):
            os.makedirs(self.output_base_dir)
            return 0
        
        # 找到最大的Run序号
        max_num = -1
        for item in os.listdir(self.output_base_dir):
            if item.endswith("Run") and os.path.isdir(os.path.join(self.output_base_dir, item)):
                try:
                    num = int(item.replace("Run", ""))
                    max_num = max(max_num, num)
                except ValueError:
                    continue
        
        return max_num + 1
    
    def create_run_directory(self, run_number: int) -> str:
        """创建运行目录"""
        run_dir = os.path.join(self.output_base_dir, f"{run_number:03d}Run")
        os.makedirs(run_dir, exist_ok=True)
        return run_dir
      
    def extract_and_save_json(self, answer: str, run_number: int) -> Optional[str]:
        """
        从回答中提取JSON内容并保存为JSON文件
        
        Args:
            answer: AI回答内容
            run_number: 运行序号
            
        Returns:
            JSON文件路径，如果提取失败返回None
        """
        run_dir = self.create_run_directory(run_number)
        
        try:
            # 使用正则表达式提取JSON内容
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, answer, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # 如果没有找到```json```标记，尝试直接解析整个回答
                json_str = answer.strip()
                # 如果以```开始，移除markdown标记
                if json_str.startswith('```'):
                    json_str = re.sub(r'^```[a-zA-Z]*\s*', '', json_str)
                    json_str = re.sub(r'\s*```$', '', json_str)
            
            # 尝试解析JSON
            detection_results = json.loads(json_str)
            
            # 保存JSON文件
            json_file = os.path.join(run_dir, "detection_results.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(detection_results, f, indent=2, ensure_ascii=False)
            
            return json_file
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析失败: {e}")
            print("原始回答内容:")
            print(answer)
            return None
        except Exception as e:
            print(f"⚠️ 保存JSON时发生错误: {e}")
            return None
    
    def save_session_info(self, question: str, image_path: str, run_number: int) -> str:
        """
        保存会话信息
        
        Args:
            question: 用户问题
            image_path: 图片路径
            run_number: 运行序号
            
        Returns:
            会话信息文件路径
        """
        run_dir = self.create_run_directory(run_number)
        
        session_info = {
            "run_number": run_number,
            "question": question,
            "image_path": image_path,
            "timestamp": self._get_timestamp()
        }
        
        session_file = os.path.join(run_dir, "session_info.json")
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2, ensure_ascii=False)
        
        return session_file
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



    
    @staticmethod
    def load_prompt_from_txt(prompt_file: str = "prompt.txt") -> Optional[str]:
        """
        从txt文件中加载prompt
        
        Args:
            prompt_file: prompt文件路径
            
        Returns:
            prompt字符串，如果加载失败返回None
        """
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"❌ Prompt文件不存在: {prompt_file}")
            return None
        except Exception as e:
            print(f"❌ 读取Prompt文件失败: {e}")
            return None


# 便捷函数
def get_next_run_number(output_dir: str = "Output") -> int:
    """便捷函数：获取下一个运行序号"""
    saver = ResultSaver(output_dir)
    return saver.get_next_run_number()

def extract_and_save_json(answer: str, run_number: int) -> Optional[str]:
    """便捷函数：提取并保存JSON"""
    saver = ResultSaver()
    return saver.extract_and_save_json(answer, run_number)

