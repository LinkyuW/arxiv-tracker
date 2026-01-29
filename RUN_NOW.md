# 🚀 立即运行项目 - 完整步骤指南

## 前提条件检查

在开始之前，确保你有：
- ✅ Python 3.8+ （检查：`python --version`）
- ✅ Git（检查：`git --version`）
- ✅ 互联网连接
- ✅ 现代浏览器 (Chrome, Firefox, Safari 等)

---

## 方案 A: 完全本地运行 (最简单，推荐)

### 步骤 1: 准备项目

```bash
# 如果还没有克隆，先克隆项目
git clone https://github.com/LinkyuW/arxiv-tracker.git
cd arxiv-tracker

# 查看项目结构
ls -la
```

### 步骤 2: 安装后端依赖

```bash
# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 验证安装成功
pip list | grep -i flask
```

**可能的错误及解决**：
```
❌ 错误: pip: command not found
✅ 解决: 使用 pip3 install -r requirements.txt

❌ 错误: ModuleNotFoundError
✅ 解决: pip install -r requirements.txt --upgrade
```

### 步骤 3: 配置环境变量 (可选但推荐)

```bash
# 返回到项目根目录
cd ..

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# 如果要启用 AI 总结功能，需要添加 Google Gemini API 密钥
# 现在先不管，可以留空，搜索功能仍然可用
```

### 步骤 4: 启动后端服务

```bash
# 进入后端目录
cd backend

# 启动 Flask 服务
python app.py
```

**你应该看到**:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**不要关闭这个窗口！** ⚠️

### 步骤 5: 在新的终端窗口启动前端

```bash
# 打开新的终端/命令行窗口
# 进入前端目录
cd arxiv-tracker/frontend

# 启动 Python HTTP 服务器
python -m http.server 8000
```

**你应该看到**:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### 步骤 6: 打开浏览器

在浏览器中访问：
```
http://localhost:8000
```

**成功标志**：
- 看到蓝色导航栏 "📚 arXiv 论文追踪器"
- 搜索框可以输入
- 界面完全加载

---

## 现在就试试看！

### 首次测试

1. **在搜索框中输入**: `machine learning`
2. **取消勾选** "使用AI总结" (因为还没配置 API 密钥)
3. **点击搜索**
4. **等待 2-3 秒**
5. **看到论文卡片了吗？** ✅

### 如果成功，你会看到：
```
找到 100 篇论文
┌─────────────────────────────────┐
│ Paper ID: 2301.xxxxx            │
│ 标题: ...                        │
│ 作者: ...                        │
│ 摘要: ...                        │
│ [View] [PDF]                    │
└─────────────────────────────────┘
```

---

## 方案 B: 直接打开 HTML 文件 (最快，但功能受限)

如果只想看界面，不想启动后端：

```bash
# 用浏览器打开 HTML 文件
# Windows: 右键 frontend/index.html → 用浏览器打开
# Mac: open frontend/index.html
# Linux: xdg-open frontend/index.html
```

**但是**：
- ❌ 搜索功能不工作（因为没有后端）
- ❌ 看不到论文数据
- ✅ 可以看到 UI 界面

**不推荐用这个方式**，建议还是用方案 A。

---

## 方案 C: 使用 GitHub Pages（已经部署的版本）

如果你想看已经部署的版本：

```
访问: https://LinkyuW.github.io/arxiv-tracker
```

**但是**：
- ❌ 后端还没部署，所以搜索功能不工作
- ✅ 可以看到前端界面
- 需要后端部署到 Railway/Render 才能完整使用

---

## 常见问题及解决

### Q1: 后端无法启动，显示 "Port 5000 already in use"

```bash
# 原因: 5000 端口被占用

# 解决方案 1: 杀死占用端口的进程
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :5000
kill -9 <PID>

# 解决方案 2: 改变端口号
# 编辑 backend/app.py 最后一行：
# app.run(host='0.0.0.0', port=5001)  # 改为 5001
```

### Q2: 后端启动后出现 ImportError

```
❌ ModuleNotFoundError: No module named 'flask'

✅ 解决:
pip install -r backend/requirements.txt

# 如果还是不行，尝试:
pip install Flask==2.3.0
pip install flask-cors
pip install requests
pip install feedparser
pip install python-dotenv
```

### Q3: 搜索没有结果

```
原因可能：
1. 后端没有启动 → 重新启动后端
2. 关键词太复杂 → 试试 "AI" 或 "deep learning"
3. 网络问题 → 检查网络连接

排查步骤：
1. 打开浏览器控制台 (F12)
2. 查看 Network 标签，看是否有请求到 http://localhost:5000
3. 查看 Console 标签，看是否有错误信息
```

### Q4: 浏览器显示 "Cannot GET /"

```
❌ 错误: 访问了错误的端口或地址

✅ 确保访问:
http://localhost:8000      ✅ 正确 (前端)
NOT http://localhost:5000  (这是后端 API)
```

### Q5: 前端启动失败 "Address already in use"

```bash
# 原因: 8000 端口被占用

# 改用其他端口:
python -m http.server 9000

# 然后访问:
http://localhost:9000
```

---

## 调试技巧

### 查看浏览器控制台 (F12)

```
按键: F12 或 右键 → 检查 → Console 标签

可以看到:
- JavaScript 错误
- API 请求和响应
- 日志信息
```

### 查看后端日志

后端运行的终端会显示：
```
127.0.0.1 - - [30/Jan/2024 10:30:00] "GET /api/search?query=... HTTP/1.1" 200 -
```

- `200` = 成功
- `400` = 请求错误
- `500` = 服务器错误

### 测试 API (直接在浏览器访问)

```
测试搜索 API:
http://localhost:5000/api/search?query=machine+learning&max_results=5

你应该看到 JSON 响应，包含论文列表
```

---

## 完整示例 - 从零开始

### Windows 用户

```batch
@REM 1. 打开命令行
@REM 2. 进入项目目录
cd D:\path\to\arxiv-tracker

@REM 3. 安装依赖
cd backend
pip install -r requirements.txt

@REM 4. 启动后端
python app.py

@REM 5. 打开新的命令行窗口 (Win+R, cmd, Enter)
cd D:\path\to\arxiv-tracker\frontend
python -m http.server 8000

@REM 6. 打开浏览器访问
http://localhost:8000
```

### Mac/Linux 用户

```bash
# 1. 打开终端
# 2. 进入项目目录
cd ~/path/to/arxiv-tracker

# 3. 安装依赖
cd backend
pip install -r requirements.txt

# 4. 启动后端
python app.py

# 5. 打开新的终端 (Cmd+T 或 Ctrl+Alt+T)
cd ~/path/to/arxiv-tracker/frontend
python -m http.server 8000

# 6. 打开浏览器访问
open http://localhost:8000
```

---

## 下一步：启用 AI 总结功能

如果想要 AI 论文总结功能：

### 步骤 1: 获取 API 密钥

1. 访问: https://aistudio.google.com/app/apikeys
2. 登录 Google 账号
3. 点击 "Create API Key"
4. 复制生成的密钥

### 步骤 2: 配置到项目

```bash
# 编辑 .env 文件
nano .env

# 添加以下行:
GEMINI_API_KEY=你复制的密钥

# 保存文件 (Ctrl+O, Enter, Ctrl+X)
```

### 步骤 3: 重启后端

```bash
# 关闭当前后端 (Ctrl+C)
# 重新启动
python app.py
```

### 步骤 4: 再次搜索

1. 在搜索框输入关键词
2. **勾选** "使用AI总结"
3. 点击搜索
4. 等待 3-5 秒看到 AI 总结

---

## 关键要点总结

✅ **后端** 运行在 `http://localhost:5000`
✅ **前端** 运行在 `http://localhost:8000`
✅ **不要关闭任何终端窗口** (除非想停止服务)
✅ **打开浏览器访问**: `http://localhost:8000`
✅ **搜索功能** 无需 API 密钥也能用
✅ **AI 总结** 需要配置 Google Gemini API 密钥

---

## 性能预期

| 操作 | 时间 |
|------|------|
| 首次加载页面 | ~1-2 秒 |
| 搜索论文 | ~1-2 秒 |
| 显示结果 | 立即 |
| AI 总结 | 3-5 秒 (100 篇论文) |
| 缓存命中 | ~0.5 秒 |

---

## 卡住了？

1. **查看浏览器控制台** (F12)
2. **查看后端日志** (运行的终端)
3. **试试访问** http://localhost:5000/api
4. **重启所有服务** (关闭并重新启动)

---

## 现在就开始！

**方案 A 步骤总结** (复制粘贴式):

```bash
# 终端 1
cd arxiv-tracker/backend
pip install -r requirements.txt
python app.py

# 终端 2
cd arxiv-tracker/frontend
python -m http.server 8000

# 浏览器
http://localhost:8000
```

**需要 5 分钟** ⏱️

---

**准备好了吗？开始吧！** 🎉

