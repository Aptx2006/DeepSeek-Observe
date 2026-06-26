# DeepSeek Observe

你还在苦于DeepSeek-V4缺少多模态带来的不便吗，快来使用deepseek-observe吧！

用于把图片转成结构化文本，给 DeepSeek-V4-flash / DeepSeek-V4-pro 做后续推理。

前端截图会额外输出布局观察。

默认使用的是阿里云百炼的 qwen-3.6-27b 模型，兼顾经济和性能 如果你颇有财力，可以试试 gemini-3.1-pro、glm-5v-trubo 等视觉理解能力高的模型。

使用非阿里云百炼的模型请调整 skill 配置，更换 url。

## 使用前配置

设置环境变量：

```bash
export DASHSCOPE_API_KEY=你的阿里云百炼API密钥
```

## 用法

```bash
python3 scripts/analyze_image.py --image_path <图片路径>
```

## 依赖

- requests（通常已预装）
