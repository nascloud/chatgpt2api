#!/bin/bash

# 配置 Git 用户信息（首次使用需要）
# git config --global user.email "your-email@example.com"
# git config --global user.name "Your Name"

# 提交代码
echo "提交代码到 Git..."
git commit -m "feat: add response_format support for url and b64_json

- Add response_format parameter to image generation and edit APIs
- Support both 'url' and 'b64_json' response formats
- Update generate_image_result and edit_image_result functions
- Add documentation for response format usage"

# 推送到 GitHub
echo "推送到 GitHub..."
git push origin main

# 构建 Docker 镜像
echo "构建 Docker 镜像..."
docker build -t ghcr.io/basketikun/chatgpt2api:latest .

# 推送 Docker 镜像到 GitHub Container Registry
echo "推送 Docker 镜像..."
docker push ghcr.io/basketikun/chatgpt2api:latest

echo "完成！"
