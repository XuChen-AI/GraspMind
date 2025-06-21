"""
GraspMind 需求理解测试程序
使用RequirementUnderstandingAgent进行需求理解

功能：
- 需求理解测试

使用方法：
直接运行此文件即可
"""

import os
import json
from Agents.RequirementUnderstandingAgent import RequirementUnderstandingAgent
from Utiles.ResultSaver import get_next_run_number, extract_and_save_json


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
    if not isinstance(sentence, str):
        return {}
    
    # 清理可能的markdown格式
    cleaned_sentence = clean_json_from_markdown(sentence)
      # 解析JSON
    result = json.loads(cleaned_sentence)
    return result


def simple_test():
    """简单测试函数"""
    print("🚀 GraspMind 智能需求理解系统")
    print("=" * 50)
    
    # 获取下一个运行序号
    run_number = get_next_run_number()
    print(f"📁 运行序号: {run_number:03d}")
    
    print("\n🤖 初始化需求理解AI代理...")
    agent = RequirementUnderstandingAgent()
    
    # 为inputMessage添加items字典
    agent.inputMessage.add_dict({"items": '["Water cup", "spoon", "notebook", "glasses", "book"]'})
    
    print(f"📋 配置内容: {agent.inputMessage.text}")
    
    print("\n🤖 正在处理，请稍候...")
    
    # 调用需求理解AI模型
    answer = agent.understand_requirement()
    
    if not answer:
        print("❌ 未获得有效回答")
        return
    
    print("\n✅ 获得回答:")
    print("-" * 50)
    print(answer)
    print("-" * 50)
    
    # 创建运行目录并保存原始回答
    run_dir = f"Output/{run_number:03d}Run"
    os.makedirs(run_dir, exist_ok=True)
    
    # 总是保存原始回答
    with open(f"{run_dir}/raw_response.txt", "w", encoding="utf-8") as f:
        f.write(answer)
    print(f"💾 原始回答保存到: {run_dir}/raw_response.txt")
    
    # 解析AI回答为字典格式
    print("\n🔄 尝试解析AI回答为字典格式...")
    json_file = None
    
    result_dict = sentence_to_dict(answer)
    print(f"🔍 解析结果: {result_dict}")
    if result_dict:
        print(f"✅ 成功解析为字典: {result_dict}")
        
        # 保存解析后的字典
        json_file = f"{run_dir}/requirement_results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        print(f"💾 字典结果保存到: {json_file}")
        
    else:
        print("⚠️ 解析返回空字典，尝试原来的方法")
        # 如果解析失败，尝试原来的方法
        json_file = extract_and_save_json(answer, run_number)
    
    # 保存需求分析汇总
    if json_file:
        print(f"📊 JSON文件: {json_file}")
        
        # 创建需求分析汇总
        print("\n📋 生成需求分析汇总...")
        summary_file = f"{run_dir}/requirement_summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("需求理解分析汇总\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"原始需求: {agent.inputMessage.text[0].get('user_requirements', 'N/A')}\n")
            f.write(f"输出格式要求: {agent.inputMessage.text[0].get('output_format', 'N/A')}\n")
            f.write(f"约束条件: {agent.inputMessage.text[0].get('Constraint', 'N/A')}\n")
            f.write(f"可选项目: {agent.inputMessage.text[1].get('items', 'N/A')}\n\n")
            f.write("AI分析结果:\n")
            f.write("-" * 20 + "\n")
            f.write(answer)
        print(f"💾 需求分析汇总保存到: {summary_file}")
    
    print(f"\n🎉 处理完成！结果保存在: Output/{run_number:03d}Run/")

def main():
    """主函数"""
    simple_test()


if __name__ == "__main__":
    main()