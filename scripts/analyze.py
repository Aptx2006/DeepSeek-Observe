#!/usr/bin/env python3
"""
DeepSeek Observe

调用阿里云百炼 DashScope 视觉模型，将图片转成结构化 Markdown。
默认模型: qwen3.6-27b
"""

import argparse
import base64
import json
import os
import sys

import requests

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
DEFAULT_MODEL = "qwen3.6-27b"
TIMEOUT_SECONDS = 60


def validate_image(image_path):
    if not os.path.exists(image_path):
        return False, f"❌ 图片文件不存在: {image_path}"
    if not os.path.isfile(image_path):
        return False, f"❌ 路径不是文件: {image_path}"
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        return False, f"❌ 不支持的图片格式: {ext}，仅支持 {', '.join(SUPPORTED_FORMATS)}"
    return True, None


def build_prompt(mode: str) -> str:
    base = [
        "请先识别图片类型：截图 / 文档 / 图表 / 照片 / 其他。",
        "请提取图片中的所有文字信息。",
        "请描述关键视觉元素。",
        "如有表格、列表、层级结构，请整理为 Markdown。",
        "不确定的内容要明确写出不确定，不要猜。",
    ]
    if mode == "frontend" or mode == "frontend-check":
        base += [
            "如果这是前端页面截图，请额外输出：页面类型、主要区域、布局关系、响应式风险、可访问性风险。",
            "前端补充观察只基于截图和文字证据，不要编造像素级结论。",
        ]
    if mode == "frontend-check":
        base += [
            "请额外检查重复文字：同一页面是否出现两次相同的标题、名称或核心文案。",
            "请额外检查视觉不均衡：是否存在明显的内边距/外边距比例失衡，尤其是标签、按钮、卡片标题等紧凑元素。",
            "请额外检查潜在裁剪：是否有带 transform 的元素出现在 overflow 容器中，是否可能被裁掉。",
            "请额外检查对比异常：是否存在与页面主色调差异明显的孤立色块、按钮或提示块。",
            "请额外检查对齐问题：是否存在左右错位、基线不齐、组件边缘参差或栅格不一致。",
            "请把每条检查结果单独列出，并标注证据位置或“不确定”。",
        ]
    return "请用 Markdown 输出，按条理清晰的结构回答。\n" + "\n".join(f"- {x}" for x in base)


def analyze_image(image_path, api_key, model=DEFAULT_MODEL, mode="general"):
    valid, error = validate_image(image_path)
    if not valid:
        return error

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    file_size = os.path.getsize(image_path)
    file_name = os.path.basename(image_path)
    print(f"[INFO] 图片: {file_name} ({file_size/1024:.1f}KB)", file=sys.stderr)
    print(f"[INFO] 正在调用 {model} 解析...", file=sys.stderr)

    payload = {
        "model": model,
        "input": {
            "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": f"data:image;base64,{image_data}"},
                        {"text": build_prompt(mode)},
                        ],
                    }
            ]
        },
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            DASHSCOPE_URL,
            headers=headers,
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )

        if response.status_code == 200:
            result = response.json()
            text = None

            choices = result.get("output", {}).get("choices", [])
            if choices:
                content_list = choices[0].get("message", {}).get("content", [])
                for item in content_list:
                    if isinstance(item, dict) and item.get("text"):
                        text = item["text"]
                        break
                    if isinstance(item, str):
                        text = item
                        break

            if not text:
                text = result.get("output", {}).get("text", "")

            if text:
                print("[INFO] 解析成功", file=sys.stderr)
                usage = result.get("usage", {})
                if usage:
                    print(
                        "[INFO] Token消耗: "
                        f"图片={usage.get('image_tokens', '?')} "
                        f"输入={usage.get('input_tokens', '?')} "
                        f"输出={usage.get('output_tokens', '?')} "
                        f"总计={usage.get('total_tokens', '?')}",
                        file=sys.stderr,
                    )
                return text

            return f"⚠️ 返回格式异常:\n{json.dumps(result, ensure_ascii=False, indent=2)}"

        error_info = response.text
        try:
            err_json = response.json()
            error_info = json.dumps(err_json, ensure_ascii=False)
        except Exception:
            pass
        return f"❌ 图片解析失败 (HTTP {response.status_code}):\n{error_info}"

    except requests.exceptions.Timeout:
        return "⏱️ 图片解析超时，请稍后重试"
    except requests.exceptions.ConnectionError:
        return "🔌 无法连接到 DashScope API，请检查网络连接"
    except Exception as e:
        return f"💥 图片解析异常: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="把图片转成结构化文本")
    parser.add_argument("--image_path", "-p", required=True, help="要分析的图片路径")
    parser.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        choices=["qwen3.6-27b"],
        help=f"模型名，默认 {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--mode",
        "-t",
        default="general",
        choices=["general", "frontend", "frontend-check"],
        help="分析模式",
    )
    parser.add_argument(
        "--image_type",
        dest="mode",
        choices=["general", "frontend"],
        help="旧参数兼容，和 --mode 一样",
    )
    args = parser.parse_args()

    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到 DASHSCOPE_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    result = analyze_image(args.image_path, api_key, args.model, args.mode)
    print(result)


if __name__ == "__main__":
    main()
