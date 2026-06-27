# DeepSeek Observe

把图片先转成结构化文本，再交给 DeepSeek-V4-flash / DeepSeek-V4-pro 做后续推理。

前端截图会额外输出布局观察，适合给纯文本模型补图片理解能力。

## 使用前配置

设置环境变量：

```bash
export DASHSCOPE_API_KEY=你的阿里云百炼API密钥
```

Windows PowerShell：

```powershell
$env:DASHSCOPE_API_KEY="你的阿里云百炼API密钥"
```

如果你在 Windows 终端里遇到 `UnicodeEncodeError: 'gbk'`，可以直接用：

```bash
python -X utf8 scripts/analyze.py --image_path <图片路径>
```

或者让脚本输出自动切到 UTF-8（脚本已内置处理）。

## 用法

```bash
python3 scripts/analyze.py --image_path <图片路径>
python3 scripts/analyze.py --image_path <图片路径> --mode frontend
python3 scripts/analyze.py --image_path <图片路径> --mode frontend-check
```

示例：

```bash
python3 scripts/analyze.py --image_path ./demo/screenshot.png --mode frontend-check
```

输出会直接返回 Markdown，便于继续喂给纯文本模型。
调用结束后，终端会在错误输出里显示本次使用的模型和 token 消耗。

## 更换模型

如果你还是用阿里云百炼平台，直接把 `--model` 后面的模型名换掉就行。
例如：

```bash
python3 scripts/analyze.py --image_path ./demo/screenshot.png --model qwen3.1-vl-max
```

前提是这个模型名在你当前账号和平台里可用。

## 为什么默认用 `qwen3.6-27b`

- 阿里云百炼新用户通常会有免费 token，可先用它做低成本试跑
- 这是 Dense 模型，视觉理解能力和综合表现比较稳，适合作为默认值
- 成本、效果和可用性之间比较均衡，适合大多数图片解析场景

## 缓存

脚本会在本地保存一份结果缓存。只要图片内容、模式和模型没变，第二次运行会直接复用上次的 Markdown。
缓存文件位于 `scripts/.observe_cache.json`。
默认最多保留 500 条缓存，超过后会自动裁掉旧记录；把 `CACHE_MAX_ENTRIES` 设为 `0` 就是无限制。

## 参数说明

- `--image_path`, `-p`：图片文件路径
- `--mode`, `-t`：运行模式，`general`、`frontend` 或 `frontend-check`
- `--image_type`：旧参数兼容，等同于 `--mode`
- `--model`, `-m`：视觉模型名，默认 `qwen3.6-27b`

## 依赖

- `requests`
- Python 3.7+

## 常见问题

### 1. 图片解析失败

先检查：

- `DASHSCOPE_API_KEY` 是否已设置
- 图片路径是否存在
- 图片格式是否为 `png/jpg/jpeg/webp/bmp`

### 2. Windows 终端报 `gbk` 编码错误

这是因为脚本输出里包含 emoji，而默认 GBK 终端无法编码。当前脚本已增加 UTF-8 输出兼容。
如果你用的是旧版脚本，优先用 `python -X utf8 ...`，或者把输出重定向到文件再查看。
