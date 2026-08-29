---
title: 多模态输入协议
date: 2026-08-29  # date-auto-injected
---

# 🖼️ 多模态输入协议

> 让模型"看图"、"听音频"、"读 PDF"的标准协议。

## 🆚 厂商多模态能力对比

| 厂商 | 图片 | 音频 | 视频 | PDF |
|------|:----:|:----:|:----:|:---:|
| **OpenAI GPT-4o** | ✅ | ✅ (gpt-4o-audio) | ❌ | ❌ |
| **Anthropic Claude** | ✅ | ❌ | ❌ | ✅ |
| **Google Gemini** | ✅ | ✅ | ✅ | ✅ |
| **DeepSeek** | ❌ | ❌ | ❌ | ❌ |
| **Qwen-VL** | ✅ | ✅ | ✅ | ❌ |

## 📐 OpenAI 多模态消息

### 图片（URL 或 base64）

```json
{
  "model": "gpt-4o",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "这张图片里有什么？"},
      {"type": "image_url", "image_url": {
        "url": "https://example.com/cat.jpg",
        "detail": "high"  // "low" | "high" | "auto"
      }}
    ]
  }]
}
```

### 图片（base64）

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
  }
}
```

### 多图对比

```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "比较这两张图的差异："},
    {"type": "image_url", "image_url": {"url": "https://example.com/before.jpg"}},
    {"type": "image_url", "image_url": {"url": "https://example.com/after.jpg"}}
  ]
}
```

## 📐 Anthropic 多模态

### 图片

```json
{
  "model": "claude-sonnet-4-5",
  "max_tokens": 1024,
  "messages": [{
    "role": "user",
    "content": [
      {"type": "image", "source": {
        "type": "base64",
        "media_type": "image/png",
        "data": "iVBORw0KGgoAAAANSUhEUgAA..."
      }},
      {"type": "text", "text": "描述这张图"}
    ]
  }]
}
```

### PDF 文档

```json
{
  "messages": [{
    "role": "user",
    "content": [
      {"type": "document", "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": "JVBERi0xLjQKJeLjz9MK..."
      }},
      {"type": "text", "text": "总结这份 PDF 的核心观点"}
    ]
  }]
}
```

## 📐 Gemini 多模态

Gemini 原生支持更丰富的输入：

```json
{
  "contents": [{
    "parts": [
      {"text": "描述这段视频"},
      {"inline_data": {
        "mime_type": "video/mp4",
        "data": "AAAAGGZ0eXBpc29t..."
      }}
    ]
  }]
}
```

支持的 `mime_type`：

- `image/png`, `image/jpeg`, `image/webp`
- `audio/wav`, `audio/mp3`, `audio/aac`
- `video/mp4`, `video/quicktime`
- `application/pdf`

## 💻 Python 示例

### OpenAI（图片 + 文本）

```python
import base64
from openai import OpenAI

client = OpenAI()

# 方式 1：URL
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "这是什么？"},
            {"type": "image_url", "image_url": {"url": "https://example.com/x.jpg"}}
        ]
    }],
    max_tokens=300,
)

# 方式 2：base64（本地文件）
with open("/tmp/photo.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "OCR 这张图的所有文字"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{b64}",
                "detail": "high"
            }}
        ]
    }],
)
print(response.choices[0].message.content)
```

### Anthropic（PDF 摘要）

```python
import base64
import anthropic

client = anthropic.Anthropic()
with open("/tmp/report.pdf", "rb") as f:
    pdf_b64 = base64.b64encode(f.read()).decode()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {"type": "document", "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": pdf_b64,
            }},
            {"type": "text", "text": "用 3 点总结这份报告的核心结论"},
        ]
    }],
)
```

## ⚠️ 多模态限制

| 限制 | OpenAI | Anthropic | Gemini |
|------|--------|-----------|--------|
| 单图大小 | 20 MB | 5 MB | 20 MB |
| 图片像素 | 2048×2048 自动压缩 | - | 更高 |
| PDF 页数 | - | 100 页（建议）| 1000 页 |
| PDF 文件大小 | - | 32 MB | 50 MB |
| 多图数量 | 受 token 限制 | 受 token 限制 | 受 token 限制 |

## 💰 Token 计费差异

| 厂商 | 计费方式 |
|------|---------|
| OpenAI GPT-4o | 图片按 `detail: low` (85 tokens) 或 `high`（按 512×512 tile 计） |
| Anthropic | 按图像大致像素折算 token |
| Gemini | 直接按图片大小（更便宜） |

## 🔗 关联章节

- [overview](./overview) - 协议全景
- [context-tokens](./context-tokens) - 多模态如何计入 token
- [rate-limit-retry](./rate-limit-retry) - 大文件上传错误处理
