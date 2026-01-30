# 📚 arXiv 论文追踪器

一个AI驱动的学术论文发现和总结平台。轻松搜索arXiv上的论文，利用Google Gemini AI自动生成论文摘要。

## 功能特性

- **论文搜索**: 从arXiv快速搜索最近5年内的相关论文
- **AI总结**: 使用Google Gemini API自动生成论文的中文总结
- **智能缓存**: 缓存搜索结果和总结，减少API调用
- **漂亮UI**: 响应式设计，支持桌面和移动设备
- **论文详情**: 查看完整的论文信息、摘要、作者和PDF链接
- **收藏功能**: 标记感兴趣的论文（可扩展）

## 技术栈

### 后端
- **框架**: Flask 2.3.0
- **API**: 
  - arXiv 官方API (免费)
  - Google Gemini Pro API (免费配额)
- **数据库**: SQLite/PostgreSQL (可选)
- **缓存**: 文件系统缓存

### 前端
- **HTML/CSS/JavaScript** (原生, 无框架依赖)
- **响应式设计** (移动友好)
- **实时搜索和加载** (异步API调用)

## 项目结构

```
arxiv-tracker/
├── backend/                    # 后端代码
│   ├── app.py                 # Flask主应用
│   ├── config.py              # 配置管理
│   ├── requirements.txt        # Python依赖
│   └── services/              # 服务模块
│       ├── arxiv_service.py   # arXiv API集成
│       ├── ai_service.py      # AI总结服务
│       └── cache_service.py   # 缓存管理
├── database/                   # 数据库模型
│   └── models.py              # SQLAlchemy模型
├── frontend/                   # 前端代码
│   ├── index.html             # 主页面
│   ├── style.css              # 样式表
│   └── src/
│       └── main.js            # 前端JavaScript
├── .env.example               # 环境变量模板
├── .gitignore                 # Git忽略文件
└── README.md                  # 项目文档
```

## 快速开始

### 前置要求

- Python 3.8+
- pip (Python包管理器)
- 现代Web浏览器

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/arxiv-tracker.git
cd arxiv-tracker
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境变量模板并填写配置:

```bash
cp .env.example .env
```

编辑 `.env` 文件:

```env
# Flask配置
FLASK_ENV=development
FLASK_DEBUG=True

# Google Gemini API密钥 (从 https://aistudio.google.com/app/apikeys 获取)
GEMINI_API_KEY=your-api-key-here

# 其他配置保持默认即可
```

### 4. 获取Google Gemini API密钥

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. 点击 "Create API Key"
3. 复制API密钥到 `.env` 文件中的 `GEMINI_API_KEY`

**注意**: Google Gemini 提供免费配额，新用户每月有充足的API调用次数。

### 5. 启动后端服务

```bash
cd backend
python app.py
```

输出示例:
```
 * Running on http://127.0.0.1:5000
```

### 6. 打开前端

在Web浏览器中打开 `frontend/index.html` 或通过本地服务器访问:

```bash
# 使用Python内置服务器
cd frontend
python -m http.server 8000
```

然后访问: `http://localhost:8000`

## 使用指南

### 搜索论文

1. 在搜索框中输入研究领域关键词
   - 示例: "deep learning", "quantum computing", "machine learning"
2. 选择选项:
   - **使用AI总结**: 勾选以获得AI生成的论文总结
   - **最多显示论文数**: 选择返回的论文数量
3. 点击 "搜索" 按钮

### 查看论文详情

1. 点击论文卡片查看完整信息
2. 在弹窗中查看:
   - 论文标题、作者、发布时间
   - 完整摘要
   - AI生成的中文总结
   - PDF和arXiv链接

### 缓存管理

- 搜索结果自动缓存30天
- 点击底部 "缓存统计" 查看缓存信息
- 点击 "清空缓存" 删除所有缓存

## API端点

### 搜索论文
```
GET /api/search?query=keyword&max_results=100&days_back=1825
```

**参数**:
- `query` (必需): 搜索关键词
- `max_results` (可选): 返回论文数, 默认100
- `days_back` (可选): 搜索天数范围, 默认1825天(5年)

**响应**:
```json
{
  "status": "success",
  "data": [
    {
      "arxiv_id": "2301.12345",
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "summary": "Paper abstract...",
      "published": "2023-01-15T00:00:00",
      "url": "https://arxiv.org/abs/2301.12345",
      "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
      "categories": "cs.LG"
    }
  ]
}
```

### 获取单篇论文
```
GET /api/paper/<arxiv_id>
```

### AI总结论文
```
POST /api/summarize
Content-Type: application/json

{
  "papers": [
    {"title": "...", "summary": "..."}
  ],
  "max_length": 200
}
```

### 缓存统计
```
GET /api/cache/stats
```

### 清空缓存
```
POST /api/cache/clear
```

## 免费API方案

### arXiv API
- ✅ 完全免费
- ✅ 无需认证
- ✅ 可靠稳定
- 限制: 单个IP每秒最多3个请求

### Google Gemini API
- ✅ 免费配额充足 (新用户)
- ✅ 高质量的AI模型
- ✅ 支持中文
- 免费层: 每分钟60个请求

**成本估算** (基于免费配额):
- 搜索100篇论文: **$0** (arXiv)
- 总结100篇论文: **$0** (在免费配额内)
- 总成本: **$0**

## 配置选项

编辑 `backend/config.py` 调整:

```python
ARXIV_SEARCH_DAYS = 365 * 5      # 搜索范围 (默认5年)
ARXIV_MAX_RESULTS = 100           # 单次查询最大结果数
CACHE_EXPIRY_DAYS = 30            # 缓存过期时间
REQUEST_TIMEOUT = 30              # 请求超时时间(秒)
```

## 开发指南

### 添加新功能

1. **后端**: 在 `backend/services/` 中添加新服务
2. **路由**: 在 `backend/app.py` 中添加新路由
3. **前端**: 在 `frontend/src/main.js` 中添加对应的前端逻辑

### 本地测试

```bash
# 测试后端API
curl "http://localhost:5000/api/search?query=machine%20learning&max_results=5"

# 查看缓存统计
curl "http://localhost:5000/api/cache/stats"
```

## 常见问题

### Q: 没有Google API密钥也能使用吗?
A: 可以，但不能使用AI总结功能。搜索和查看论文仍然正常。

### Q: 如何在生产环境中部署?
A: 
1. 在生产服务器上克隆项目
2. 配置环境变量 (使用强密钥)
3. 使用Gunicorn运行Flask: `gunicorn app:app`
4. 配置Nginx反向代理
5. 设置HTTPS和防火墙

### Q: 为什么搜索很慢?
A: 可能的原因:
- arXiv服务器响应慢
- AI总结需要时间 (可禁用以加快速度)
- 网络连接问题

### Q: 可以缓存论文吗?
A: 目前使用文件系统缓存。可扩展为使用Redis等。

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request!

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

## 联系方式
- 电子邮件: pxqqwq@qq.com

## 参考资源

- [arXiv API文档](https://arxiv.org/help/api/)
- [Google Gemini API](https://ai.google.dev/)
- [Flask 文档](https://flask.palletsprojects.com/)

## 路线图 (未来计划)

- [ ] 用户账号系统和论文收藏
- [ ] 高级搜索过滤 (按日期、作者、分类)
- [ ] 论文推荐系统
- [ ] 多种AI模型支持 (GPT, Claude等)
- [ ] 论文导出 (PDF, BibTeX)
- [ ] 移动应用 (React Native)
- [ ] 论文订阅提醒功能

---

**最后更新**: 2026年1月
**维护者**: [Linkyu]
