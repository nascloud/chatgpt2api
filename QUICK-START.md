# 快速开始指南

## 🚀 快速部署步骤

### 1. 配置 Git（首次使用）

```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

### 2. 提交并推送代码

```bash
# 提交代码
git commit -m "feat: add response_format support for url and b64_json"

# 推送到 GitHub（会自动触发 Docker 构建）
git push origin main
```

推送后，GitHub Actions 会自动：
- 构建 Docker 镜像（支持 AMD64 和 ARM64）
- 推送到 GitHub Container Registry
- 查看构建进度：https://github.com/ZuBeri05/chatgpt2api/actions

### 3. 等待构建完成（约 5-10 分钟）

访问 GitHub Actions 页面查看构建状态。

### 4. 部署运行

构建完成后，在服务器上运行：

```bash
# 拉取最新镜像
docker-compose pull

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 📝 测试新功能

### 测试 URL 格式返回

```bash
curl -X POST "http://localhost:3000/v1/images/generations" \
  -H "Authorization: Bearer YOUR_AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful sunset",
    "model": "gpt-image-1",
    "n": 1,
    "response_format": "url"
  }'
```

### 测试 Base64 格式返回（默认）

```bash
curl -X POST "http://localhost:3000/v1/images/generations" \
  -H "Authorization: Bearer YOUR_AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful sunset",
    "model": "gpt-image-1",
    "n": 1,
    "response_format": "b64_json"
  }'
```

## 🔧 本地构建（可选）

如果需要本地构建测试：

```bash
# 构建镜像
docker build -t chatgpt2api:local .

# 运行测试
docker run -d \
  --name chatgpt2api-test \
  -p 3000:80 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.json:/app/config.json:ro \
  chatgpt2api:local

# 查看日志
docker logs -f chatgpt2api-test

# 清理
docker stop chatgpt2api-test
docker rm chatgpt2api-test
```

## ⚠️ 注意事项

1. 确保 `config.json` 中配置了正确的 `auth-key`
2. URL 格式返回的链接是临时的，建议及时下载
3. 首次推送需要配置 Git 用户信息
4. GitHub Actions 需要有 `packages: write` 权限

## 📚 更多文档

- [完整部署指南](DEPLOY.md)
- [Response Format 使用说明](docs/response-format-usage.md)
- [功能状态](docs/feature-status.en.md)
