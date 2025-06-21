# ImagePreprocessor 图像预处理工具

## 概述

`ImagePreprocessor` 是一个强大的图像预处理工具，位于 `Utiles/ImagePreprocessor.py`，专门用于优化图像以便进行高效的数据传输和处理。

## 主要功能

### 1. 图像尺寸调整
- 自动将图像调整至最大 1024x1024 像素
- 保持原始宽高比
- 使用高质量的 LANCZOS 重采样算法

### 2. 色彩空间转换
- 统一转换为 RGB 色彩空间
- 智能处理 RGBA 透明通道（使用白色背景）
- 支持各种输入格式

### 3. JPEG 压缩优化
- 默认使用质量系数 85 进行压缩
- 可自定义压缩质量（1-100）
- 启用优化算法以获得最佳压缩效果

## 类和方法

### ImagePreprocessor 类

```python
from Utiles.ImagePreprocessor import ImagePreprocessor

preprocessor = ImagePreprocessor()
```

#### 主要方法

1. **preprocess_image(image_input, max_size=1024, quality=85)**
   - 完整的预处理流程
   - 返回：(处理后的图像对象, 压缩字节数据)

2. **save_preprocessed_image(image_input, output_path, max_size=1024, quality=85)**
   - 预处理并保存图像
   - 返回：保存成功的布尔值

3. **resize_image(image, max_size=1024)**
   - 调整图像尺寸

4. **convert_to_rgb(image)**
   - 转换为 RGB 色彩空间

5. **compress_image(image, quality=85)**
   - JPEG 压缩

6. **get_image_info(image)**
   - 获取图像详细信息

### 便捷函数

```python
from Utiles.ImagePreprocessor import preprocess_image_file

# 预处理并获取结果
image, data = preprocess_image_file("input.jpg")

# 预处理并保存
success = preprocess_image_file("input.jpg", "output.jpg")
```

## 使用示例

### 基本用法

```python
from Utiles.ImagePreprocessor import ImagePreprocessor

# 创建预处理器
preprocessor = ImagePreprocessor()

# 处理图像
processed_image, compressed_data = preprocessor.preprocess_image("input.jpg")

# 保存结果
success = preprocessor.save_preprocessed_image("input.jpg", "output.jpg")
```

### 自定义参数

```python
# 调整最大尺寸为 512px，质量为 90
processed_image, data = preprocessor.preprocess_image(
    "input.jpg", 
    max_size=512, 
    quality=90
)
```

### 批量处理

```python
import os
from Utiles.ImagePreprocessor import preprocess_image_file

input_dir = "InputPicture"
output_dir = "Output"

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"processed_{filename}")
        
        success = preprocess_image_file(input_path, output_path)
        print(f"处理 {filename}: {'成功' if success else '失败'}")
```

## 技术规格

- **最大尺寸**: 1024x1024 像素（可配置）
- **色彩空间**: RGB
- **压缩格式**: JPEG
- **默认质量**: 85（可配置 1-100）
- **重采样算法**: LANCZOS
- **支持格式**: JPEG, PNG, BMP, TIFF 等

## 性能优化

### 压缩效果示例
根据测试结果，该工具能显著减少文件大小：

- PNG 转 JPEG: 压缩比可达 95%+
- 大尺寸图像: 平均压缩比 60-70%
- 总体批量处理: 平均压缩比 68%

### 质量对比
不同质量设置的文件大小示例（基于 860x573 图像）：

| 质量 | 文件大小 | 压缩比 |
|------|----------|--------|
| 60   | 43.9 KB  | 最小   |
| 75   | 54.9 KB  | 标准   |
| 85   | 87.9 KB  | 推荐   |
| 95   | 127.1 KB | 高质量 |

## 错误处理

工具包含完整的错误处理机制：

- **FileNotFoundError**: 图像文件不存在
- **ValueError**: 输入参数无效
- **IOError**: 文件读写错误
- **PermissionError**: 文件权限问题

## 依赖要求

```txt
Pillow>=10.0.0  # 图像处理库
```

## 测试

运行测试文件验证功能：

```bash
python ImagePreprocessorTest.py
```

运行使用示例：

```bash
python ImagePreprocessorExample.py
```

## 与现有代码集成

该工具设计为独立模块，不影响现有代码结构：

- 位于 `Utiles/` 目录下
- 遵循项目命名规范（大写驼峰命名法）
- 可与其他 Agent 和工具无缝集成

## 适用场景

1. **数据传输优化**: 减少网络传输时间
2. **存储空间节省**: 降低存储成本
3. **API 调用准备**: 为视觉 API 准备标准格式图像
4. **批量图像处理**: 统一处理大量图像文件
5. **移动端优化**: 为移动设备准备轻量级图像

## 注意事项

1. 原始图像文件不会被修改
2. 输出始终为 JPEG 格式
3. 透明背景将转换为白色背景
4. 建议在生产环境中测试压缩质量设置
