"""
GraspMind主程序入口

使用示例:
python main.py --image input_images/scene.jpg --instruction "我想喝水"
"""

import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from loguru import logger
from src.core.pipeline import GraspMindPipeline
from src.utils.config import ConfigManager


def setup_logging(config_manager: ConfigManager) -> None:
    """
    设置日志系统
    
    Args:
        config_manager: 配置管理器
    """
    log_config = config_manager.get_log_config()
    
    # 移除默认的logger
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        level=log_config["level"],
        format=log_config["format"],
        colorize=True
    )
    
    # 添加文件输出
    log_file = Path(log_config["file"])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        level=log_config["level"],
        format=log_config["format"],
        rotation=log_config["rotation"],
        retention=log_config["retention"]
    )


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="GraspMind - 智能机械臂功能性抓取系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --image input_images/cup.jpg --instruction "我想喝水"
  python main.py --image input_images/scissors.jpg --instruction "帮我拿剪刀"
  python main.py --test  # 运行系统测试
        """
    )
    
    parser.add_argument(
        "--image", "-i",
        type=str,
        help="输入图像路径"
    )
    
    parser.add_argument(
        "--instruction", "-t",
        type=str,
        help="用户指令"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=".env",
        help="配置文件路径 (默认: .env)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行系统测试"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="显示系统状态"
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager(args.config)
        
        # 设置日志
        setup_logging(config_manager)
        
        logger.info("🤖 GraspMind系统启动")
        logger.info(f"📁 工作目录: {Path.cwd()}")
        logger.info(f"⚙️ 配置文件: {args.config}")
        
        # 初始化主流水线
        pipeline = GraspMindPipeline(config_manager)
        
        # 根据参数执行不同操作
        if args.test:
            # 运行系统测试
            logger.info("🧪 运行系统测试...")
            if pipeline.test_system():
                logger.info("✅ 系统测试通过")
                return 0
            else:
                logger.error("❌ 系统测试失败")
                return 1
        
        elif args.status:
            # 显示系统状态
            status = pipeline.get_status()
            logger.info("📊 系统状态:")
            for key, value in status.items():
                logger.info(f"  {key}: {value}")
            return 0
        
        elif args.image and args.instruction:
            # 执行主要功能
            image_path = Path(args.image)
            
            # 验证图像文件
            if not image_path.exists():
                logger.error(f"❌ 图像文件不存在: {image_path}")
                return 1
            
            logger.info(f"📸 处理图像: {image_path}")
            logger.info(f"💬 用户指令: {args.instruction}")
            
            # 执行处理流程
            result = pipeline.process(str(image_path), args.instruction)
            
            if result.success:
                logger.info("🎉 处理成功完成!")
                logger.info(f"📄 输出掩码: {result.output_mask_path}")
                logger.info(f"⏱️ 处理耗时: {result.processing_time:.2f}秒")
                
                # 显示分割信息
                mask = result.mask
                logger.info(f"🎯 分割目标: {mask.target_object_id} - {mask.target_part_name}")
                logger.info(f"📐 掩码尺寸: {mask.width} x {mask.height}")
                logger.info(f"🎚️ 置信度: {mask.mask_confidence:.3f}")
                
                return 0
            else:
                logger.error("❌ 处理失败")
                logger.error(f"🚫 错误信息: {result.error_message}")
                return 1
        
        else:
            # 显示帮助信息
            parser.print_help()
            return 0
    
    except KeyboardInterrupt:
        logger.info("⏹️ 用户中断程序")
        return 130
    
    except Exception as e:
        logger.error(f"💥 系统错误: {str(e)}")
        logger.exception("详细错误信息:")
        return 1
    
    finally:
        logger.info("👋 GraspMind系统关闭")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
