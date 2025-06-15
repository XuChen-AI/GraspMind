# 🚀 GraspMind 快速开始指南

## 📋 系统要求

- Python 3.8+
- Windows 10/11 (当前环境)
- 8GB+ RAM (推荐)
- 网络连接 (用于API调用)

## 🔧 安装步骤

### 1. 安装Python依赖

```powershell
# 安装依赖包
pip install -r requirements.txt
```

### 2. 配置API密钥

复制环境配置文件:
```powershell
copy .env.example .env
```

编辑 `.env` 文件，填入您的API密钥:
```env
# OpenAI API配置 (用于GPT-4o等模型)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 千问VL API配置 (可选，用于国内用户)
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# 其他配置保持默认即可
LOG_LEVEL=INFO
DEFAULT_VLM_MODEL=gpt-4o
DEFAULT_LLM_MODEL=gpt-4o-mini
```

### 3. 准备演示图像

在 `input_images` 目录下放置测试图像。建议包含:
- 杯子场景 (测试饮水指令)
- 剪刀场景 (测试工具使用指令)
- 餐具场景 (测试用餐指令)

## 🎮 使用方法

### 方法1: 命令行模式

```powershell
# 测试系统连接
python main.py --test

# 处理单个场景
python main.py --image input_images/cup.jpg --instruction "我想喝水"

# 查看系统状态
python main.py --status
```

### 方法2: 演示模式 (推荐)

```powershell
# 启动交互式演示
python demo.py
```

演示模式提供友好的菜单界面:
1. 预设演示场景 - 运行内置的测试场景
2. 交互模式 - 自定义图像和指令
3. 系统状态 - 查看当前配置和状态

### 方法3: 程序化调用

```python
from src.core.pipeline import GraspMindPipeline
from src.utils.config import ConfigManager

# 初始化系统
config_manager = ConfigManager()
pipeline = GraspMindPipeline(config_manager)

# 处理图像
result = pipeline.process(
    image_path="input_images/scene.jpg",
    user_instruction="我想喝水"
)

# 检查结果
if result.success:
    print(f"输出掩码: {result.output_mask_path}")
    print(f"目标物体: {result.mask.target_object_id}")
    print(f"目标部件: {result.mask.target_part_name}")
else:
    print(f"处理失败: {result.error_message}")
```

## 📊 输出说明

系统会生成以下输出:

1. **分割掩码** (`output_masks/` 目录)
   - 二值图像文件 (.png格式)
   - 白色区域 = 目标抓取部件
   - 黑色区域 = 背景

2. **处理日志** (`logs/` 目录)
   - 详细的处理过程记录
   - 错误信息和调试信息

3. **结果数据**
   - 目标物体信息
   - 功能性部件名称
   - 置信度分数
   - 处理时间统计

## 🎯 支持的场景

### 物体类别
- ☕ 杯子 (杯柄分割)
- ✂️ 剪刀 (握柄分割)
- 🍴 餐具 (握柄分割) 
- 🔪 刀具 (刀柄分割)
- 🍶 瓶子 (瓶颈分割)
- 📱 手机 (整体抓取)
- 📚 书籍 (边缘抓取)
- ✏️ 笔类 (握持部分)

### 意图类型
- 饮水: "我想喝水"、"我渴了"
- 用餐: "我要吃饭"、"给我餐具"
- 剪切: "帮我拿剪刀"、"我要剪纸"
- 写作: "我要写字"、"给我笔"
- 通讯: "给我手机"、"我要打电话"

## 🔧 故障排除

### 常见问题

1. **API连接失败**
   ```
   解决方案:
   - 检查网络连接
   - 确认API密钥正确
   - 验证API配额是否充足
   ```

2. **图像加载失败**
   ```
   解决方案:
   - 确认图像文件存在
   - 检查文件格式 (支持 jpg, png, bmp)
   - 验证图像完整性
   ```

3. **未检测到物体**
   ```
   解决方案:
   - 提高图像清晰度
   - 确保充足光线
   - 避免物体重叠遮挡
   - 调整拍摄角度
   ```

4. **分割质量差**
   ```
   解决方案:
   - 确保目标部件清晰可见
   - 简化背景环境
   - 增加物体与背景的对比度
   ```

### 调试模式

启用详细日志:
```powershell
# 修改 .env 文件
LOG_LEVEL=DEBUG

# 运行程序会显示更多调试信息
python main.py --image input_images/test.jpg --instruction "测试指令"
```

## 📈 性能优化

1. **图像预处理**
   - 推荐分辨率: 512x512 到 1024x1024
   - 避免过大的图像以节省处理时间

2. **API优化**
   - 使用合适的模型温度参数
   - 避免频繁的API调用

3. **缓存机制**
   - 相同图像会复用分析结果
   - 提高重复测试的效率

## 🆘 获取帮助

如果遇到问题:

1. 查看 `logs/` 目录下的日志文件
2. 运行系统测试: `python main.py --test`
3. 检查配置文件 `.env` 的设置
4. 确认所有依赖包已正确安装

## 🎉 开始使用

现在您可以开始使用GraspMind了! 建议从演示模式开始:

```powershell
python demo.py
```

享受智能抓取的魅力! 🤖✨
