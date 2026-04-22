# 部署指南

## 前置要求

1. 安装 Docker 和 Docker Compose
2. 配置 Git 用户信息
3. 登录 GitHub Container Registry

## 步骤 1: 配置 Git（首次使用）

```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

## 步骤 2: 提交并推送代码

```bash
# 提交代码
git commit -m "feat: add response_format support for url and b64_json"

# 推送到 GitHub
git push origin main
```

## 步骤 3: 登录 GitHub Container Registry

```bash
# 使用 GitHub Personal Access Token 登录
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

创建 Personal Access Token:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限: `write:packages`, `read:packages`, `delete:packages`
4. 生成并保存 token

## 步骤 4: 构建 Docker 镜像

### 方式 1: 使用脚本（推荐）

Windows PowerShell:
```powershell
.\build-and-push.ps1
```

Linux/Mac:
```bash
chmod +x build-and-push.sh
./build-and-push.sh
```

### 方式 2: 手动构建

```bash
# 构建镜像
docker build -t ghcr.io/basketikun/chatgpt2api:latest .

# 推送镜像
docker push ghcr.io/basketikun/chatgpt2api:latest
```

### 方式 3: 多平台构建（支持 ARM64 和 AMD64）

```bash
# 创建 buildx builder（首次使用）
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap

# 构建并推送多平台镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/basketikun/chatgpt2api:latest \
  --push .
```

## 步骤 5: 部署运行

### 使用 Docker Compose（推荐）

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker 命令

```bash
# 拉取最新镜像
docker pull ghcr.io/basketikun/chatgpt2api:latest

# 运行容器
docker run -d \
  --name chatgpt2api \
  --restart unless-stopped \
  -p 3000:80 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.json:/app/config.json:ro \
  ghcr.io/basketikun/chatgpt2api:latest

# 查看日志
docker logs -f chatgpt2api

# 停止容器
docker stop chatgpt2api
docker rm chatgpt2api
```

## 步骤 6: 验证部署

```bash
# 检查服务状态
curl http://localhost:3000/version

# 测试图片生成（URL 格式）
curl -X POST "http://localhost:3000/v1/images/generations" \
  -H "Authorization: Bearer YOUR_AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a cute cat",
    "model": "gpt-image-1",
    "n": 1,
    "response_format": "url"
  }'
```

## 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建并推送镜像
docker build -t ghcr.io/basketikun/chatgpt2api:latest .
docker push ghcr.io/basketikun/chatgpt2api:latest

# 更新运行中的容器
docker-compose pull
docker-compose up -d
```

## 故障排查

### 网络连接问题

如果遇到 "Could not resolve host: github.com" 错误：
1. 检查网络连接
2. 检查 DNS 设置
3. 尝试使用 VPN 或代理

### Docker 构建失败

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker build --no-cache -t ghcr.io/basketikun/chatgpt2api:latest .
```

### 容器无法启动

```bash
# 查看详细日志
docker logs chatgpt2api

# 检查配置文件
cat config.json

# 检查端口占用
netstat -ano | findstr :3000  # Windows
lsof -i :3000                  # Linux/Mac
```

## GitHub Actions 自动构建（可选）

在 `.github/workflows/docker-build.yml` 中配置自动构建：

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ghcr.io/basketikun/chatgpt2api:latest
```

这样每次推送到 main 分支时，GitHub Actions 会自动构建并推送 Docker 镜像。
