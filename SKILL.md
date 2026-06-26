---
name: deepseek-observe
description: For DeepSeek-V4-flash and DeepSeek-V4-pro. Use DashScope vision parsing to turn images, screenshots, documents, charts, and UI captures into structured Markdown. Best for image reading first; when the image is a frontend screenshot, also extract layout, responsive, and accessibility clues for later text-only reasoning.
---

# DeepSeek Observe

## 一句话定义

把图片先转成结构化文本，再交给 DeepSeek-V4-flash / DeepSeek-V4-pro 推理；前端截图时额外抽取布局证据。

## 适用场景

- 截图识别
- 文档拍照识别
- 图表解读
- 表格提取
- 二维码 / 公告 / 菜单 / 名片识别
- 前端页面截图分析

## 核心目标

1. 让纯文本模型获得稳定的图片理解输入
2. 把图片内容整理成可复查的 Markdown 证据
3. 前端截图时，补充布局、响应式、可访问性线索

## 输入契约

优先接收：

- 图片文件路径
- 图片用途说明
- 需要关注的目标

支持格式：

- `png`
- `jpg`
- `jpeg`
- `webp`
- `bmp`

## 处理流程

1. 校验图片是否存在和格式是否支持
2. 读取图片并转 base64
3. 调用 DashScope 视觉模型
4. 提取 OCR、内容描述、结构化数据
5. 如果是前端截图，再补充页面结构和布局证据
6. 输出 Markdown 结果给 DeepSeek 继续推理

## 检查标准

至少要检查：

- 图片类型是否识别正确
- 文字是否漏读
- 表格 / 列表是否保留结构
- 截图中的界面元素是否描述清楚
- 前端截图是否提到布局、溢出、重叠、对齐、按钮状态

## 输出格式

固定输出以下五段：

1. `图片类型`
2. `文字内容`
3. `视觉描述`
4. `结构化数据`
5. `前端补充观察`（仅前端截图时输出）

## 前端补充观察

当图片是前端页面截图时，额外输出：

- 页面类型
- 主要区域
- 布局关系
- 响应式风险
- 可访问性风险

## 规则

- 没有图片就不分析
- 不要只说“看起来不错”
- OCR 和布局观察要分开写
- 不能确定的内容要标注“不确定”

## DashScope 调用

默认使用阿里云百炼 DashScope，模型为 `qwen3.6-35b-a3b`。

```bash
python3 /mnt/d/CODE/Major/前端开发/.reasonix/skills/deepseek-observe/scripts/analyze_image.py \
  --image_path <图片文件路径>
```

## 自检清单

- 是否提取了文字
- 是否保留了结构
- 是否识别了图片用途
- 如果是前端截图，是否补了布局观察
- 是否可直接喂给纯文本模型继续推理
