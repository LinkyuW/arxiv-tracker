# 部署指南

## 前后端架构

```
GitHub Pages (静态前端)
    ↓ HTTP API 请求
后端服务器 (Flask + Python)
    ↓
arXiv API + Google Gemini API
```

## 🎨 前端部署 (GitHub Pages)

### 1. 启用 GitHub Pages

1. 进入你的 GitHub 仓库设置
2. 访问 **Settings** → **Pages**
3. 在 **Source** 中选择 **Deploy from a branch**
4. 选择分支: **main**
5. 文件夹: **/docs**
6. 点击 **Save**

### 2. 配置前端 API 端点

编辑 `docs/config.js`:

```javascript
const API_CONFIG = {
  // 改为你的后端服务器地址
  baseURL: 'https://your-backend-server.com/api',
  timeout: 30000,
};
```

### 3. 前端部署完成

等待几分钟，访问: **https://LinkyuW.github.io/arxiv-tracker**

---

## 🖥️ 后端部署 (4 种方案)

### 方案 A: Heroku (简单，免费额度已取消)

**费用**: 付费
**优点**: 一键部署，自动化

```bash
# 1. 安装 Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. 登录
heroku login

# 3. 创建应用
heroku create your-app-name

# 4. 设置环境变量
heroku config:set GEMINI_API_KEY=your-key-here
heroku config:set FLASK_ENV=production

# 5. 部署
git push heroku main

# 6. 查看日志
heroku logs --tail
```

### 方案 B: Railway (推荐，简单易用)

**费用**: 免费 $5/月额度，超出后按量计费
**优点**: GitHub 集成，自动部署

```bash
# 1. 访问 https://railway.app
# 2. 用 GitHub 账号登录
# 3. 创建新项目，选择 "Deploy from GitHub repo"
# 4. 选择本仓库
# 5. 在 Variables 中添加环境变量:
#    GEMINI_API_KEY=your-key-here
#    FLASK_ENV=production
# 6. 自动部署完成
```

**获取后端地址**:
- Railway 会生成一个类似 `https://projectname-production.up.railway.app` 的 URL
- 你的 API 地址是: `https://projectname-production.up.railway.app/api`

### 方案 C: Render (另一个好选择)

**费用**: 免费层可用
**优点**: 无需信用卡，支持免费后端

```
1. 访问 https://render.com
2. 连接 GitHub
3. 创建 Web Service
4. 选择本仓库
5. 配置:
   - Runtime: Python 3.11
   - Build Command: pip install -r backend/requirements.txt
   - Start Command: cd backend && gunicorn app:app
6. 添加环境变量
7. Deploy
```

### 方案 D: 阿里云/腾讯云函数计算

**费用**: 按使用量付费
**优点**: 国内服务器，速度快

这需要将 Flask 应用改造为函数式，比较复杂，不推荐初期使用。

---

## 📋 部署检查清单

### 前端检查
- [ ] docs/ 文件夹已推送到 GitHub
- [ ] GitHub Pages 已启用
- [ ] config.js 中的 baseURL 指向正确的后端地址
- [ ] 访问 https://LinkyuW.github.io/arxiv-tracker 可以打开页面

### 后端检查
- [ ] requirements.txt 包含所有依赖
- [ ] .env.example 已创建
- [ ] 后端部署平台已配置环境变量
- [ ] 后端服务已启动
- [ ] CORS 已启用

### API 检查
- [ ] 在浏览器控制台测试: `fetch('https://your-backend/api')`
- [ ] 前端搜索功能正常工作
- [ ] AI 总结功能正常工作

---

## 🔑 环境变量配置

### 必需的环境变量

```
GEMINI_API_KEY=你的Google Gemini API密钥
FLASK_ENV=production
SECRET_KEY=随机生成的强密钥
```

### 如何生成 SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## ⚠️ 常见问题

### Q: CORS 错误?
A: 确保后端的 CORS 已启用，允许来自 GitHub Pages 的请求

### Q: API 超时?
A: 检查网络连接，或增加 timeout 值在 config.js 中

### Q: 后端显示 500 错误?
A: 检查环境变量是否正确设置，查看后端日志

### Q: 如何调试前端?
A: 打开浏览器控制台 (F12)，查看 Console 和 Network 标签

---

## 🔄 持续更新

每次更新代码后:

1. **前端**: 自动部署到 GitHub Pages (推送到 main 分支的 docs/ 后)
2. **后端**: 根据部署平台的设置自动部署

---

## 📊 成本估算 (每月)

| 方案 | 前端 | 后端 | 总计 |
|------|------|------|------|
| GitHub Pages + Railway | 免费 | $5 | $5 |
| GitHub Pages + Render | 免费 | 免费 | 免费 |
| GitHub Pages + Heroku | 免费 | $7+ | $7+ |

**推荐**: GitHub Pages + Railway 或 Render

---

## 🚀 本地开发

本地开发时，后端和前端都在本地运行:

```bash
# 终端 1: 启动后端
cd backend
python app.py
# 运行在 http://localhost:5000

# 终端 2: 打开前端
# 直接打开 frontend/index.html
# 或使用 Python 服务器:
cd frontend
python -m http.server 8000
# 访问 http://localhost:8000
```

此时 docs/config.js 中的 baseURL 应该指向 `http://localhost:5000/api`

