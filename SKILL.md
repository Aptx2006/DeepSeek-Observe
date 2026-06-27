---
name: deepseek-observe
description: 为纯文本模型提供视觉能力、多模态能力。用 DashScope 把图片、截图、文档和图表转成结构化 Markdown；如果遇到前端截图还会补充布局、适配和可访问性线索，方便文本模型进行前端开发。
---

# DeepSeek Observe

## 一句话定义

把图片先转成结构化文本，再交给 DeepSeek-V4-flash / DeepSeek-V4-pro 推理；前端截图时额外抽取布局证据，助力纯文本模型进行前端开发。

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

## 前端检查模式

当以 `frontend-check` 运行时，除基础观察外，还要额外检查：

- 重复文字：同一页面是否出现两次相同的标题、名称或核心文案
- 视觉不均衡：是否存在明显的内边距 / 外边距比例失衡
- 潜在裁剪：是否有带 `transform` 的元素出现在 `overflow` 容器中
- 对比异常：是否存在与页面主色调差异明显的孤立色块
- 对齐问题：是否存在左右错位、基线不齐、组件边缘参差或栅格不一致

## 规则

- 没有图片就不分析
- 不要只说“看起来不错”
- OCR 和布局观察要分开写
- 不能确定的内容要标注“不确定”

## DashScope 调用

默认使用阿里云百炼 DashScope，模型为 `qwen3.6-27b`。

脚本会按图片内容、模式和模型做本地缓存，重复分析同一张图时会直接复用上次的 Markdown。

```bash
python3 skill开发/deepseek-observe/scripts/analyze.py \
  --image_path <图片文件路径>
```

示例：

```bash
python3 skill开发/deepseek-observe/scripts/analyze.py \
  --image_path ./demo/screenshot.png \
  --mode frontend-check
```

Windows 终端如果遇到 `UnicodeEncodeError: 'gbk'`，可改用：

```bash
python -X utf8 skill开发/deepseek-observe/scripts/analyze.py \
  --image_path ./demo/screenshot.png
```

兼容旧参数：

```bash
python3 skill开发/deepseek-observe/scripts/analyze.py \
  --image_path ./demo/screenshot.png \
  --image_type frontend
```

## 自检清单

- 是否提取了文字
- 是否保留了结构
- 是否识别了图片用途
- 如果是前端截图，是否补了布局观察
- 是否可直接喂给纯文本模型继续推理
