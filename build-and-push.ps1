# PowerShell 脚本用于构建和推送

# 配置 Git 用户信息（首次使用需要，取消注释并填写你的信息）
# git config --global user.email "your-email@example.com"
# git config --global user.name "Your Name"

# 提交代码
Write-Host "提交代码到 Git..." -ForegroundColor Green
git commit -m "feat: add response_format support for url and b64_json

- Add response_format parameter to image generation and edit APIs
- Support both 'url' and 'b64_json' response formats
- Update generate_image_result and edit_image_result functions
- Add documentation for response format usage"

# 推送到 GitHub
Write-Host "推送到 GitHub..." -ForegroundColor Green
git push origin main

# 构建 Docker 镜像
Write-Host "构建 Docker 镜像..." -ForegroundColor Green
docker build -t ghcr.io/basketikun/chatgpt2api:latest .

# 推送 Docker 镜像到 GitHub Container Registry
Write-Host "推送 Docker 镜像..." -ForegroundColor Green
docker push ghcr.io/basketikun/chatgpt2api:latest

Write-Host "完成！" -ForegroundColor Green
