"""
GraspMind演示脚本

提供一个简单的演示界面来测试系统功能
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from loguru import logger
from src.core.pipeline import GraspMindPipeline
from src.utils.config import ConfigManager


class GraspMindDemo:
    """GraspMind演示类"""
    
    def __init__(self):
        """初始化演示"""
        self.config_manager = None
        self.pipeline = None
        self.setup_logging()
        
    def setup_logging(self):
        """设置简单的日志"""
        logger.remove()
        logger.add(
            sys.stdout,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
            colorize=True
        )
    
    def initialize_system(self) -> bool:
        """初始化系统"""
        try:
            print("🚀 正在初始化GraspMind系统...")
            
            # 初始化配置
            self.config_manager = ConfigManager()
            
            # 验证配置
            if not self.config_manager.validate_config():
                print("❌ 配置验证失败，请检查.env文件")
                return False
            
            # 初始化流水线
            self.pipeline = GraspMindPipeline(self.config_manager)
            
            # 测试系统
            if not self.pipeline.test_system():
                print("❌ 系统测试失败，请检查API配置")
                return False
            
            print("✅ 系统初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {str(e)}")
            return False
    
    def get_demo_scenarios(self) -> List[Tuple[str, str]]:
        """获取演示场景"""
        return [
            ("input_images/cup_scene.jpg", "我想喝水"),
            ("input_images/scissors_scene.jpg", "帮我拿剪刀"),
            ("input_images/kitchen_scene.jpg", "我要吃饭"),
            ("input_images/office_scene.jpg", "我要写字"),
        ]
    
    def run_demo_scenario(self, image_path: str, instruction: str) -> bool:
        """运行演示场景"""
        try:
            print(f"\n📸 场景: {image_path}")
            print(f"💬 指令: {instruction}")
            print("-" * 50)
            
            # 检查图像文件
            if not Path(image_path).exists():
                print(f"⚠️ 图像文件不存在: {image_path}")
                print("💡 请将演示图像放在input_images目录下")
                return False
            
            # 执行处理
            start_time = time.time()
            result = self.pipeline.process(image_path, instruction)
            
            # 显示结果
            if result.success:
                print(f"✅ 处理成功! 耗时: {result.processing_time:.2f}秒")
                print(f"🎯 目标: {result.mask.target_object_id} - {result.mask.target_part_name}")
                print(f"📄 输出: {result.output_mask_path}")
            else:
                print(f"❌ 处理失败: {result.error_message}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ 演示失败: {str(e)}")
            return False
    
    def interactive_mode(self):
        """交互模式"""
        print("\n🎮 进入交互模式")
        print("输入 'quit' 退出")
        
        while True:
            try:
                print("\n" + "=" * 50)
                
                # 获取用户输入
                image_path = input("📸 请输入图像路径 (或 'quit' 退出): ").strip()
                if image_path.lower() == 'quit':
                    break
                
                instruction = input("💬 请输入用户指令: ").strip()
                if not instruction:
                    print("⚠️ 指令不能为空")
                    continue
                
                # 运行处理
                self.run_demo_scenario(image_path, instruction)
                
            except KeyboardInterrupt:
                print("\n👋 退出交互模式")
                break
            except Exception as e:
                print(f"❌ 交互模式错误: {str(e)}")
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 60)
        print("🤖 GraspMind 演示系统")
        print("=" * 60)
        print("1. 运行预设演示场景")
        print("2. 交互模式 (自定义输入)")
        print("3. 系统状态")
        print("4. 退出")
        print("=" * 60)
    
    def run(self):
        """运行演示"""
        print("🤖 欢迎使用GraspMind演示系统")
        
        # 初始化系统
        if not self.initialize_system():
            return
        
        while True:
            try:
                self.show_menu()
                choice = input("请选择 (1-4): ").strip()
                
                if choice == "1":
                    # 预设演示场景
                    scenarios = self.get_demo_scenarios()
                    print(f"\n📋 共有 {len(scenarios)} 个演示场景:")
                    
                    for i, (image_path, instruction) in enumerate(scenarios, 1):
                        print(f"{i}. {Path(image_path).name} - {instruction}")
                    
                    print("0. 运行所有场景")
                    
                    try:
                        scenario_choice = int(input("\n请选择场景 (0-{}): ".format(len(scenarios))))
                        
                        if scenario_choice == 0:
                            # 运行所有场景
                            success_count = 0
                            for image_path, instruction in scenarios:
                                if self.run_demo_scenario(image_path, instruction):
                                    success_count += 1
                                time.sleep(1)  # 稍作停顿
                            
                            print(f"\n📊 演示完成: {success_count}/{len(scenarios)} 个场景成功")
                        
                        elif 1 <= scenario_choice <= len(scenarios):
                            # 运行单个场景
                            image_path, instruction = scenarios[scenario_choice - 1]
                            self.run_demo_scenario(image_path, instruction)
                        
                        else:
                            print("❌ 无效选择")
                    
                    except ValueError:
                        print("❌ 请输入有效数字")
                
                elif choice == "2":
                    # 交互模式
                    self.interactive_mode()
                
                elif choice == "3":
                    # 系统状态
                    status = self.pipeline.get_status()
                    print(f"\n📊 系统状态:")
                    print(f"版本: {status['version']}")
                    print(f"状态: {status['status']}")
                    print(f"VLM模型: {status['config']['vlm_model']}")
                    print(f"LLM模型: {status['config']['llm_model']}")
                    print(f"支持格式: {', '.join(status['config']['supported_formats'])}")
                
                elif choice == "4":
                    print("👋 感谢使用GraspMind!")
                    break
                
                else:
                    print("❌ 无效选择，请重新输入")
            
            except KeyboardInterrupt:
                print("\n👋 用户中断，退出系统")
                break
            except Exception as e:
                print(f"❌ 系统错误: {str(e)}")


def create_sample_images_info():
    """创建示例图像说明"""
    input_dir = Path("input_images")
    input_dir.mkdir(exist_ok=True)
    
    readme_content = """# 示例图像说明

请将您的演示图像放在此目录下。建议的图像:

## 推荐的演示场景

1. **cup_scene.jpg** - 包含杯子的桌面场景
   - 用于测试"我想喝水"指令
   - 应该清晰显示杯柄部分

2. **scissors_scene.jpg** - 包含剪刀的场景  
   - 用于测试"帮我拿剪刀"指令
   - 应该能看到剪刀的握柄

3. **kitchen_scene.jpg** - 厨房场景
   - 包含餐具(叉子、勺子等)
   - 用于测试"我要吃饭"指令

4. **office_scene.jpg** - 办公桌场景
   - 包含笔、书等文具
   - 用于测试"我要写字"指令

## 图像要求

- 分辨率: 建议不超过1024x1024
- 格式: JPG, PNG, BMP
- 清晰度: 物体边界清晰
- 光线: 充足的光线，避免过度阴影
- 背景: 尽量简洁，避免杂乱

## 拍摄建议

1. 物体应该完整可见
2. 功能性部件(如杯柄、握把)要清晰
3. 避免物体重叠遮挡
4. 保持合适的拍摄角度和距离
"""
    
    (input_dir / "README.md").write_text(readme_content, encoding="utf-8")


if __name__ == "__main__":
    # 创建示例图像目录和说明
    create_sample_images_info()
    
    # 运行演示
    demo = GraspMindDemo()
    demo.run()
