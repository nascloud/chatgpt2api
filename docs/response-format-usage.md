# Response Format 使用说明

API 现在支持两种图片返回格式：`b64_json`（默认）和 `url`。

## 图片生成 API

### 返回 Base64 格式（默认）

```bash
curl -X POST "http://localhost:8000/v1/images/generations" \
  -H "Authorization: Bearer YOUR_AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a cute cat",
    "model": "gpt-image-1",
    "n": 1,
    "response_format": "b64_json"
  }'
```

响应示例：
```json
{
  "created": 1234567890,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAA...",
      "revised_prompt": "a cute cat"
    }
  ]
}
```

### 返回 URL 格式

```bash
curl -X POST "http://localhost:8000/v1/images/generations" \
  -H "Authorization: Bearer YOUR_AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a cute cat",
    "model": "gpt-image-1",
    "n": 1,
    "response_format": "url"
  }'
```

响应示例：
```json
{
  "created": 1234567890,
  "data": [
    {
      "url": "https://files.oaiusercontent.com/...",
      "revised_prompt": "a cute cat"
    }
  ]
}
```

## 图片编辑 API

### 返回 Base64 格式（默认）

```bash
curl -X POST "http://localhost:8000/v1/images/edits" \
  -H "Authorization: Bearer YOUR_AUTH_KEY" \
  -F "image=@input.png" \
  -F "prompt=add a hat" \
  -F "model=gpt-image-1" \
  -F "n=1" \
  -F "response_format=b64_json"
```

### 返回 URL 格式

```bash
curl -X POST "http://localhost:8000/v1/images/edits" \
  -H "Authorization: Bearer YOUR_AUTH_KEY" \
  -F "image=@input.png" \
  -F "prompt=add a hat" \
  -F "model=gpt-image-1" \
  -F "n=1" \
  -F "response_format=url"
```

## 参数说明

- `response_format`: 可选值为 `"b64_json"` 或 `"url"`
  - `b64_json`: 返回 Base64 编码的图片数据（默认）
  - `url`: 返回图片的下载 URL

## 注意事项

1. URL 格式返回的链接是临时的，建议及时下载保存
2. Base64 格式适合直接在前端展示或保存到数据库
3. URL 格式可以减少响应体积，适合需要下载或转发的场景
