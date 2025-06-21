"""
GraspMind 目标检测测试程序
使用ObjectDetectionAgent进行目标检测

功能：
- 目标检测测试
- 自定义问题测试

使用方法：
直接运行此文件即可
"""

import os
import json
from Agents.ObjectDetectionAgent import ObjectDetectionAgent
from Utiles.ResultSaver import get_next_run_number, extract_and_save_json
from Utiles.Visualizer import quick_visualize


def clean_json_from_markdown(text: str) -> str:
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


def sentence_to_dict(sentence: str):
    """本地实现的JSON解析函数"""
    try:
        if not isinstance(sentence, str):
            return {}
        
        if not sentence.strip():
            return {}
        
        # 清理markdown格式
        cleaned_text = clean_json_from_markdown(sentence)
        
        # 解析JSON
        parsed_result = json.loads(cleaned_text)
        
        # 如果是列表，包装成字典格式
        if isinstance(parsed_result, list):
            return {"detection_results": parsed_result}
        else:
            return parsed_result
            
    except json.JSONDecodeError as e:
        print(f"JSON格式解析失败: {e}")
        return {}
    except Exception as e:
        print(f"字符串转换失败: {e}")
        return {}


def test_detection():
    """目标检测测试"""
    print("🚀 GraspMind 目标检测测试")
    print("=" * 40)
    
    # 设置图片路径
    image_path = "InputPicture/test11.jpg"
    print(f"📸 测试图片: {image_path}")
      # 创建agent并执行检测
    agent = ObjectDetectionAgent()
    print("🤖 Agent初始化完成")
      # 设置图片路径
    agent.set_image(image_path)
    print(f"📸 图片已设置: {image_path}")
    
    print("\n🔍 正在检测...")
    result = agent.ask_about_image_with_coordinate_conversion()
    
    if result:
        print("\n✅ 检测结果（坐标已转换到原图）:")
        print("-" * 40)
        print(result)
        print("-" * 40)
          # 保存结果
        save_result(result, image_path)
    else:
        print("❌ 检测失败")


def save_result(result: str, image_path: str):
    """保存检测结果"""
    run_number = get_next_run_number()
    run_dir = f"Output/{run_number:03d}Run"
    os.makedirs(run_dir, exist_ok=True)    # 保存原始结果
    with open(f"{run_dir}/raw_response.txt", "w", encoding="utf-8") as f:
        f.write(result)
    
    print(f"💾 结果已保存: {run_dir}/raw_response.txt")
    
    # 解析和可视化
    result_dict = sentence_to_dict(result)
    
    if result_dict:
        # 保存JSON
        json_file = f"{run_dir}/detection_results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        # 可视化
        if quick_visualize(json_file, image_path):
            basename = os.path.splitext(os.path.basename(image_path))[0]
            print(f"🖼️ 标注图片: {run_dir}/{basename}_annotated.jpg")
            print(f"📋 检测汇总: {run_dir}/detection_summary.txt")
    else:
        # 备用解析方法
        extract_and_save_json(result, run_number)


def main():
    """主函数 - 直接运行检测"""
    test_detection()


if __name__ == "__main__":
    main()