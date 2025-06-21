"""
GraspMind 精确分割测试程序
使用PreciseSegmentationAgent进行精确分割

功能：
- 精确分割测试
- 自定义问题测试

使用方法：
直接运行此文件即可
"""

import os
import json
from Agents.PreciseSegmentationAgent import PreciseSegmentationAgent
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
    """本地实现的JSON解析函数，包含边界框验证"""
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
            # 验证和修复边界框数据
            validated_results = []
            for i, item in enumerate(parsed_result):
                if isinstance(item, dict):
                    # 检查bbox_2d字段
                    bbox = item.get('bbox_2d', [])
                    if not isinstance(bbox, list) or len(bbox) != 4:
                        print(f"警告：分割结果 {i} 的边界框数据无效，已跳过: {bbox}")
                        continue
                    
                    # 检查边界框坐标是否为数值
                    try:
                        x1, y1, x2, y2 = map(float, bbox)
                        # 确保坐标顺序正确
                        if x1 > x2:
                            x1, x2 = x2, x1
                        if y1 > y2:
                            y1, y2 = y2, y1
                        
                        # 更新修正后的坐标
                        item['bbox_2d'] = [int(x1), int(y1), int(x2), int(y2)]
                        validated_results.append(item)
                    except (ValueError, TypeError):
                        print(f"警告：分割结果 {i} 的边界框坐标无效，已跳过: {bbox}")
                        continue
                else:
                    print(f"警告：分割结果 {i} 格式不正确，已跳过")
                    continue
            
            return {"segmentation_results": validated_results}
        else:
            return parsed_result
            
    except json.JSONDecodeError as e:
        print(f"JSON格式解析失败: {e}")
        return {}
    except Exception as e:
        print(f"字符串转换失败: {e}")
        return {}


def test_segmentation():
    """精确分割测试"""
    print("🚀 GraspMind 精确分割测试")
    print("=" * 40)
      # 设置图片路径
    image_path = "InputPicture/333.jpg"
    print(f"📸 测试图片: {image_path}")
      # 创建agent并执行分割
    agent = PreciseSegmentationAgent()
    print("🤖 Agent初始化完成")
    
    # 添加物体和部件信息到输入消息
    agent.inputMessage.add_dict({"object": "Mug", "part": "Handle"})
      # 设置图片路径
    agent.set_image(image_path)
    print(f"📸 图片已设置: {image_path}")
    
    print("\n🔍 正在分割...")
    result = agent.ask_about_image_with_coordinate_conversion()
    
    if result:
        print("\n✅ 分割结果（坐标已转换到原图）:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # 保存结果
        save_result(result, image_path)
    else:
        print("❌ 分割失败")


def save_result(result: str, image_path: str):
    """保存分割结果"""
    run_number = get_next_run_number()
    run_dir = f"Output/{run_number:03d}Run"
    os.makedirs(run_dir, exist_ok=True)    # 保存原始结果
    with open(f"{run_dir}/raw_response.txt", "w", encoding="utf-8") as f:
        f.write(result)
    
    print(f"💾 结果已保存: {run_dir}/raw_response.txt")
    
    # 解析和可视化
    result_dict = sentence_to_dict(result)
    
    if result_dict:
        # 检查是否有有效的分割结果
        segmentation_results = result_dict.get('segmentation_results', [])
        if segmentation_results:
            print(f"✅ 解析到 {len(segmentation_results)} 个有效的分割结果")
            
            # 保存JSON
            json_file = f"{run_dir}/segmentation_results.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, ensure_ascii=False, indent=2)
            
            # 可视化
            if quick_visualize(json_file, image_path):
                basename = os.path.splitext(os.path.basename(image_path))[0]
                print(f"🖼️ 标注图片: {run_dir}/{basename}_annotated.jpg")
                print(f"📋 分割汇总: {run_dir}/segmentation_summary.txt")
        else:
            print("⚠️ 没有找到有效的分割结果")
            # 仍然保存空结果的JSON文件
            json_file = f"{run_dir}/segmentation_results.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, ensure_ascii=False, indent=2)
    else:
        print("❌ JSON解析失败，使用备用方法")
        # 备用解析方法
        extract_and_save_json(result, run_number)


def main():
    """主函数 - 直接运行分割"""
    test_segmentation()


if __name__ == "__main__":
    main()