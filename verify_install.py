"""
系统安装验证脚本

验证GraspMind系统的安装和配置是否正确
"""

import sys
import importlib
from pathlib import Path
from typing import List, Tuple


def check_python_version() -> bool:
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要Python 3.8或更高版本")
        return False


def check_dependencies() -> bool:
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        ("crewai", "CrewAI框架"),
        ("langchain", "LangChain框架"),
        ("langchain_openai", "OpenAI集成"),
        ("opencv-python", "OpenCV图像处理", "cv2"),
        ("Pillow", "PIL图像库", "PIL"),
        ("numpy", "NumPy数值计算"),
        ("requests", "HTTP请求库"),
        ("pydantic", "数据验证"),
        ("python-dotenv", "环境变量管理", "dotenv"),
        ("loguru", "日志库")
    ]
    
    success_count = 0
    failed_packages = []
    
    for package_info in required_packages:
        package_name = package_info[0]
        description = package_info[1]
        import_name = package_info[2] if len(package_info) > 2 else package_name
        
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name}: {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {package_name}: {description} - 未安装")
            failed_packages.append(package_name)
    
    print(f"\n📊 依赖检查结果: {success_count}/{len(required_packages)} 个包已安装")
    
    if failed_packages:
        print(f"\n⚠️ 缺少以下依赖包:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 安装命令: pip install " + " ".join(failed_packages))
        return False
    
    return True


def check_directory_structure() -> bool:
    """检查目录结构"""
    print("\n📁 检查目录结构...")
    
    required_dirs = [
        ("src", "源代码目录"),
        ("src/agents", "智能体模块"),
        ("src/core", "核心模块"),
        ("src/models", "数据模型"),
        ("src/tools", "工具模块"),
        ("src/utils", "工具类"),
        ("input_images", "输入图像目录"),
        ("output_masks", "输出掩码目录"),
        ("logs", "日志目录")
    ]
    
    missing_dirs = []
    
    for dir_path, description in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}: {description}")
        else:
            print(f"❌ {dir_path}: {description} - 目录不存在")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️ 缺少以下目录:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        
        # 自动创建缺少的目录
        print(f"\n🔧 正在创建缺少的目录...")
        for dir_path in missing_dirs:
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                print(f"✅ 已创建: {dir_path}")
            except Exception as e:
                print(f"❌ 创建失败 {dir_path}: {str(e)}")
    
    return len(missing_dirs) == 0


def check_config_files() -> bool:
    """检查配置文件"""
    print("\n⚙️ 检查配置文件...")
    
    config_files = [
        (".env.example", "环境配置模板", False),
        (".env", "环境配置文件", True),
        ("requirements.txt", "依赖列表", False),
        ("main.py", "主程序", False),
        ("demo.py", "演示脚本", False)
    ]
    
    missing_files = []
    
    for file_path, description, optional in config_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}: {description}")
        else:
            status = "⚠️" if optional else "❌"
            print(f"{status} {file_path}: {description} - 文件不存在")
            if not optional:
                missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ 缺少以下必要文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True


def check_env_config() -> bool:
    """检查环境配置"""
    print("\n🔑 检查环境配置...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env文件不存在")
        print("💡 请复制.env.example为.env并配置API密钥")
        return False
    
    # 读取环境变量
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        # 检查关键配置
        configs = [
            ("OPENAI_API_KEY", "OpenAI API密钥"),
            ("DEFAULT_VLM_MODEL", "默认VLM模型"),
            ("DEFAULT_LLM_MODEL", "默认LLM模型")
        ]
        
        missing_configs = []
        
        for key, description in configs:
            value = os.getenv(key)
            if value and value != "your_openai_api_key_here":
                print(f"✅ {key}: {description} - 已配置")
            else:
                print(f"⚠️ {key}: {description} - 未配置或使用默认值")
                missing_configs.append(key)
        
        if missing_configs:
            print(f"\n⚠️ 以下配置需要设置:")
            for key in missing_configs:
                print(f"   - {key}")
            print("\n💡 请编辑.env文件填入正确的API密钥")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 环境配置检查失败: {str(e)}")
        return False


def run_basic_import_test() -> bool:
    """运行基本导入测试"""
    print("\n🧪 运行基本导入测试...")
    
    try:
        # 测试核心模块导入
        sys.path.append("src")
        
        print("   测试数据模型导入...")
        from models.data_models import ObjectCategory, DetectedObject
        
        print("   测试工具模块导入...")
        from utils.config import ConfigManager
        from utils.image_utils import ImageProcessor
        
        print("   测试智能体模块导入...")
        from agents.scene_analyst import SceneAnalyst
        
        print("✅ 基本导入测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {str(e)}")
        print("   请检查代码完整性和依赖安装")
        return False


def main():
    """主函数"""
    print("🤖 GraspMind系统安装验证")
    print("=" * 50)
    
    # 运行所有检查
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("目录结构", check_directory_structure),
        ("配置文件", check_config_files),
        ("环境配置", check_env_config),
        ("基本导入", run_basic_import_test)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
        except Exception as e:
            print(f"❌ {check_name}检查出错: {str(e)}")
    
    # 显示总结
    print("\n" + "=" * 50)
    print(f"📊 验证结果: {passed_checks}/{total_checks} 项检查通过")
    
    if passed_checks == total_checks:
        print("🎉 系统安装验证完成! 可以开始使用GraspMind")
        print("\n💡 下一步:")
        print("   1. 在input_images目录放置测试图像")
        print("   2. 运行: python demo.py")
        print("   3. 或运行: python main.py --test")
        return True
    else:
        print("⚠️ 系统安装不完整，请解决上述问题后重新验证")
        print("\n💡 常见解决方案:")
        print("   1. 安装缺少的依赖: pip install -r requirements.txt")
        print("   2. 配置API密钥: 编辑.env文件") 
        print("   3. 检查Python版本: python --version")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
