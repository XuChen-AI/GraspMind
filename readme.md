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
