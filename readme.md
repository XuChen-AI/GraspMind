# 🤖 GraspMind
> *智能机械臂的面向人机交互功能性抓取系统*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Framework-green.svg)](https://crewai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 项目概述

GraspMind 是一个基于多智能体协作的智能机械臂抓取系统，能够理解自然语言指令，识别场景中的物体，并以安全、友好的方式将物体递给用户。

### ✨ 核心特性

- 🧠 **多模态场景理解** - 融合RGB图像和点云数据的场景感知
- 🗣️ **自然语言交互** - 理解用户意图并精准关联目标物体  
- 💡 **功能性抓取** - 基于安全性和人体工学的智能部件选择
- 🤝 **人机协作** - 面向人机交互的安全递送机制

## 🏗️ 系统架构

### 四阶段处理流程

```
📸 多模态感知 → 🎯 意图识别 → 🔍 功能分析 → 🤖 安全执行
```

1. **多模态场景感知** - VLM驱动的物体识别与三维定位
2. **用户意图识别** - LLM解析指令并关联目标物体
3. **功能区域分析** - 基于常识的功能性部件分割
4. **运动规划执行** - 无碰撞路径规划与安全递送

### 三智能体协作架构

| 智能体 | 职责 | 核心功能 |
|--------|------|----------|
| 🔍 **场景分析师** | 视觉感知 | 物体识别与位置检测 |
| 🧠 **交互策略师** | 决策推理 | 意图理解与安全策略制定 |
| ✂️ **精准分割师** | 视觉定位 | 功能部件的像素级分割 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- CrewAI Framework
- RGB-D 相机 (Intel RealSense / Azure Kinect)
- 机械臂硬件平台

### 安装依赖

```bash
# 安装Python依赖包
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入您的API密钥
```

## 🎮 快速开始

### 方法1: 一键启动 (Windows)
```cmd
# 运行启动脚本
run.bat
```

### 方法2: 演示模式
```bash
# 交互式演示
python demo.py
```

### 方法3: 命令行模式
```bash
# 系统测试
python main.py --test

# 处理图像
python main.py --image input_images/scene.jpg --instruction "我想喝水"
```

## 📁 项目结构

```
GraspMind/
├── src/                     # 源代码
│   ├── agents/             # 智能体模块
│   │   ├── scene_analyst.py          # 场景分析师
│   │   ├── interaction_strategist.py # 交互策略师
│   │   └── precision_segmenter.py    # 精准分割师
│   ├── core/               # 核心模块
│   │   └── pipeline.py     # 主流水线
│   ├── models/             # 数据模型
│   │   └── data_models.py  # 数据结构定义
│   ├── tools/              # 工具模块
│   │   └── vision_tool.py  # 视觉分析工具
│   └── utils/              # 工具类
│       ├── config.py       # 配置管理
│       ├── image_utils.py  # 图像处理
│       └── model_client.py # 模型客户端
├── input_images/           # 输入图像目录
├── output_masks/           # 输出掩码目录
├── logs/                   # 日志目录
├── main.py                 # 主程序入口
├── demo.py                 # 演示脚本
├── run.bat                 # Windows启动脚本
├── requirements.txt        # 依赖列表
├── .env.example           # 环境配置模板
└── QUICKSTART.md          # 快速开始指南
```

## 🔧 配置说明

系统支持多种AI模型:

| 模型类型 | 推荐模型 | 用途 | API配置 |
|---------|---------|------|---------|
| VLM | GPT-4o | 视觉分析与分割 | OPENAI_API_KEY |
| VLM | Qwen-VL-Max | 国内替代方案 | QWEN_API_KEY |
| LLM | GPT-4o-mini | 推理与策略制定 | OPENAI_API_KEY |

## 🎯 使用示例

### 示例1: 饮水场景
```python
# 输入图像: 包含杯子的桌面场景
# 用户指令: "我想喝水"
# 系统输出: 杯柄部分的精确分割掩码
```

### 示例2: 工具使用
```python
# 输入图像: 包含剪刀的场景
# 用户指令: "帮我拿剪刀"  
# 系统输出: 剪刀握柄部分的分割掩码
```

### 示例3: 用餐场景
```python
# 输入图像: 餐桌场景
# 用户指令: "我要吃饭"
# 系统输出: 餐具握柄部分的分割掩码
```

## 📊 系统特性

### 🧠 智能化程度
- **多模态理解**: 融合视觉与语言信息
- **意图推理**: 从自然语言推断用户真实需求
- **安全优先**: 基于常识的安全抓取策略
- **自适应**: 支持未见过的物体类型

### 🔍 技术亮点
- **三智能体协作**: 专业化分工，高效协作
- **分层处理**: 从场景理解到精确分割的递进式处理
- **质量验证**: 多层次的结果质量检查
- **可扩展**: 模块化设计，易于扩展新功能

## 🛠️ 开发指南

### 添加新的物体类型
1. 在 `data_models.py` 中添加新的 `ObjectCategory`
2. 在 `interaction_strategist.py` 中定义功能性部件
3. 更新意图映射规则

### 集成新的AI模型
1. 在 `model_client.py` 中实现新的客户端类
2. 更新配置管理器支持新模型
3. 测试模型兼容性

### 自定义分割策略
1. 扩展 `FunctionalPart` 数据结构
2. 修改安全评估逻辑
3. 优化分割提示词

## 🔍 故障排除

### 常见问题
- **API连接失败**: 检查网络和密钥配置
- **物体检测失败**: 提高图像质量和光线条件
- **分割精度低**: 确保目标部件清晰可见

详细解决方案请参考 [QUICKSTART.md](QUICKSTART.md)

## 📚 技术文档

- [系统设计文档](SchemeDesign.md) - 详细的技术架构
- [问题描述文档](ProblemDescription.md) - 问题背景与挑战
- [快速开始指南](QUICKSTART.md) - 安装和使用指南

## 🤝 贡献指南

我们欢迎社区贡献! 请遵循以下步骤:

1. Fork 本项目
2. 创建特性分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 团队

- **技术架构**: 多智能体协作框架设计
- **算法实现**: 计算机视觉与自然语言处理
- **系统集成**: 端到端流水线开发

## 🎉 致谢

感谢以下开源项目的支持:
- [CrewAI](https://crewai.com) - 多智能体协作框架
- [OpenAI](https://openai.com) - 先进的AI模型
- [LangChain](https://langchain.com) - AI应用开发框架

---

**GraspMind** - 让机器人更懂人类的需求 🤖❤️

```bash
pip install crewai
pip install langchain-openai
# 根据选择的VLM安装相应依赖
```

### 基础使用

```python
from crewai import Crew, Process
from agents import scene_analyst, interaction_strategist, precision_segmenter
from tasks import task_analyze_scene, task_strategize_interaction, task_segment_target

# 初始化智能体团队
smart_grasping_crew = Crew(
    agents=[scene_analyst, interaction_strategist, precision_segmenter],
    tasks=[task_analyze_scene, task_strategize_interaction, task_segment_target],
    process=Process.sequential
)

# 执行抓取任务
result = smart_grasping_crew.kickoff()
```

## 💡 使用案例

### 示例 1: 饮水场景
```
用户指令: "我口渴了，想喝水"
系统识别: 马克杯 → 选择杯柄抓取 → 安全递送
```

### 示例 2: 工具使用
```
用户指令: "帮我拿一下剪刀"  
系统识别: 剪刀 → 选择握柄抓取 → 避免尖端朝向用户
```

## 🔧 技术栈

- **框架**: CrewAI 多智能体协作框架
- **视觉模型**: Qwen-VL-Max / GPT-4o
- **语言模型**: GPT-4o / Claude 3 Opus / ERNIE 4.0
- **运动规划**: ROS MoveIt
- **硬件**: RGB-D相机 + 机械臂

## 📊 核心优势

- ✅ **安全优先** - 基于常识的功能性抓取策略
- ✅ **高度泛化** - 支持未见过物体的合理推理
- ✅ **模块化设计** - 清晰的职责分离与数据流
- ✅ **易于扩展** - 支持新智能体和功能模块集成

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来完善项目！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">
  <sub>Built with ❤️ using CrewAI Framework</sub>
</div>
