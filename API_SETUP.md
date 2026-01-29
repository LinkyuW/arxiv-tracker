# API 接入完全指南

## 📌 概览

本项目需要接入两个 API：

| API | 用途 | 成本 | 认证 |
|-----|------|------|------|
| **arXiv** | 搜索论文 | 免费 | 无 |
| **Google Gemini** | AI 总结 | 免费配额 | API 密钥 |

**已集成**: arXiv (无需配置)
**需要配置**: Google Gemini

---

## 🔍 arXiv API (已集成，无需配置)

### 工作原理

```
用户搜索 "deep learning"
  ↓
Python 代码调用:
  http://export.arxiv.org/api/query?search_query=all:"deep learning"...
  ↓
arXiv 返回 RSS XML
  ↓
Python 解析 XML，提取论文信息
  ↓
返回给前端显示
```

### 代码位置

**文件**: `backend/services/arxiv_service.py`

```python
def search_papers(query, days_back=1825, max_results=100):
    """
    搜索 arXiv 论文
    
    query: 搜索关键词 (如: "deep learning")
    days_back: 搜索时间范围 (默认5年=1825天)
    max_results: 最多返回多少篇论文
    
    返回: 论文列表
    """
```

### 限制

- ✅ 每秒最多 3 个请求
- ✅ 单次最多返回 100,000 条结果
- ✅ 完全免费
- ✅ 无需认证

### 搜索示例

```python
from services.arxiv_service import ArxivService

arxiv = ArxivService()

# 搜索 "machine learning" 最近 5 年的论文，最多 50 篇
papers = arxiv.search_papers(
    query="machine learning",
    days_back=365*5,
    max_results=50
)

# 查看结果
for paper in papers:
    print(f"标题: {paper['title']}")
    print(f"作者: {', '.join(paper['authors'])}")
    print(f"摘要: {paper['summary']}")
```

---

## 🤖 Google Gemini API (需要配置)

### 第 1 步: 获取 API 密钥

#### 步骤详解

1. **打开浏览器**
   访问: https://aistudio.google.com/app/apikeys

2. **登录 Google 账号**
   - 如果没有 Google 账号，先注册
   - 中国用户可能需要科学上网

3. **创建 API Key**
   - 页面应该显示一个蓝色的 "Create API Key" 按钮
   - 点击它
   - 弹出对话框，选择 "Create API key in new project"

4. **复制密钥**
   - API 密钥会自动复制到剪贴板
   - 如果没有复制，手动复制文本

#### 成功标志

你会看到一个类似这样的密钥:
```
AIzaSyDaBcDefGhIjKlMnOpQrStUvWxYzAbCdEfG
```

### 第 2 步: 配置环境变量

#### 方法 A: 本地开发

1. **复制模板**
   ```bash
   cp .env.example .env
   ```

2. **编辑 `.env` 文件**
   ```env
   FLASK_ENV=development
   FLASK_DEBUG=True
   GEMINI_API_KEY=AIzaSyDaBcDefGhIjKlMnOpQrStUvWxYzAbCdEfG
   ```

3. **保存文件**

#### 方法 B: 部署到远程服务器

具体方法取决于你选择的服务:

**Railway:**
1. 进入项目设置
2. 找到 "Variables" 部分
3. 添加新变量:
   - Key: `GEMINI_API_KEY`
   - Value: 你的 API 密钥

**Render:**
1. 进入 Service 设置
2. 找到 "Environment" 部分
3. 添加新环境变量

**Heroku:**
```bash
heroku config:set GEMINI_API_KEY=你的密钥
```

### 第 3 步: 验证配置

#### 本地测试

```bash
# 进入后端目录
cd backend

# 启动 Flask 服务
python app.py
```

你应该看到:
```
 * Running on http://127.0.0.1:5000
```

没有错误信息说明配置成功！

#### 测试搜索功能

打开浏览器，访问:
```
http://localhost:5000/api/search?query=machine+learning&max_results=5
```

看到论文列表说明工作正常。

#### 测试 AI 总结

```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "papers": [
      {
        "title": "Deep Learning",
        "summary": "This paper introduces a new approach to deep neural networks..."
      }
    ]
  }'
```

应该返回 AI 总结结果。

---

## 📊 API 调用流程图

### 搜索流程

```
前端用户搜索
  ↓
JavaScript 调用 fetch()
  ↓
GET /api/search?query=...
  ↓
后端 Flask 接收请求
  ↓
检查本地缓存
  ├─ 缓存命中 → 返回缓存数据 ✓
  └─ 缓存未命中 ↓
      ↓
      调用 ArxivService.search_papers()
      ↓
      HTTP GET http://export.arxiv.org/api/query?search_query=...
      ↓
      arXiv API 返回 RSS XML
      ↓
      Python feedparser 解析 XML
      ↓
      保存到本地缓存
      ↓
      返回论文列表给前端
```

### AI 总结流程

```
用户点击启用 AI 总结
  ↓
前端收集论文数据
  ↓
JavaScript 调用 fetch()
  ↓
POST /api/summarize
  ↓
后端接收论文列表
  ↓
对每篇论文调用 AIService.summarize_paper()
  ↓
AIService 调用 Google Gemini API
  ↓
Gemini 返回中文总结
  ↓
前端显示总结
```

---

## 🔄 代码实现细节

### arXiv 集成代码

```python
# backend/services/arxiv_service.py

def search_papers(self, query, days_back=1825, max_results=100):
    # 计算日期范围
    cutoff_date = datetime.now() - timedelta(days=days_back)
    date_str = cutoff_date.strftime('%Y%m%d%H%M%S')
    
    # 构建查询
    search_query = f'(all:"{query}") AND submittedDate:[{date_str}Z TO 9999999999]'
    
    # 调用 arXiv API
    params = {
        'search_query': search_query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
    
    # 解析 RSS
    feed = feedparser.parse(response.content)
    
    # 提取论文信息
    papers = []
    for entry in feed.entries:
        paper = {
            'arxiv_id': entry.id.split('/abs/')[-1],
            'title': entry.title.strip(),
            'authors': [a.name for a in entry.authors],
            'summary': entry.summary.strip(),
            'published': entry.published,
            'url': entry.id,
            'pdf_url': f'https://arxiv.org/pdf/{arxiv_id}.pdf'
        }
        papers.append(paper)
    
    return papers
```

### Google Gemini 集成代码

```python
# backend/services/ai_service.py

import google.generativeai as genai

def summarize_paper(self, title, abstract, max_length=200):
    # 构建提示
    prompt = f"""请对以下学术论文进行简洁总结，用中文回答：

论文标题：{title}

论文摘要：
{abstract}

请用不超过{max_length}个字符的中文总结这篇论文的主要内容、创新点和实际应用意义。"""
    
    # 调用 Gemini API
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    return response.text
```

---

## 🚀 快速验证检查表

在部署前检查:

- [ ] `.env` 文件已创建
- [ ] `GEMINI_API_KEY` 已添加到 `.env`
- [ ] 后端可以启动 (无错误)
- [ ] 可以搜索论文 (测试 arXiv API)
- [ ] 可以生成 AI 总结 (测试 Gemini API)
- [ ] 前端可以调用后端 API
- [ ] CORS 错误已解决

---

## ⚠️ 常见错误

### 错误 1: ImportError: cannot import name 'genai'

**原因**: Google Generative AI 库未安装

**解决**:
```bash
pip install google-generativeai
```

### 错误 2: 401 Unauthorized

**原因**: API 密钥无效或未设置

**解决**:
- 检查 `.env` 中的密钥是否正确
- 重新从 aistudio.google.com 获取密钥
- 确保密钥没有过期

### 错误 3: No module named 'feedparser'

**原因**: feedparser 库未安装

**解决**:
```bash
pip install -r backend/requirements.txt
```

### 错误 4: CORS 错误

**原因**: 前端无法调用后端 API

**检查**:
- 后端 CORS 是否启用 (已在 app.py 中配置)
- 前端 `config.js` 中的 baseURL 是否正确
- 后端是否正在运行

---

## 📈 配额和成本

### arXiv
- 费用: 免费
- 限制: 每秒 3 个请求
- 存储: 无限制

### Google Gemini
- 费用: 免费配额，超出后按用量计费
- 免费额度: 每分钟 60 个请求
- 成本估算: 100 次 API 调用约 $0.001 - $0.01

---

## 🔐 安全最佳实践

1. **永远不要在代码中硬编码 API 密钥**
   ```python
   # ❌ 错误
   api_key = "AIzaSyDaBcDefGhIjKlMnOpQrStUvWxYzAbCdEfG"
   
   # ✅ 正确
   api_key = os.getenv('GEMINI_API_KEY')
   ```

2. **不要将 `.env` 文件上传到 GitHub**
   `.gitignore` 已经配置了这一点

3. **定期轮换 API 密钥**
   如果怀疑泄露，立即在 Google 控制台重新生成

---

## 📚 参考资源

- arXiv API 文档: https://arxiv.org/help/api/
- Google Generative AI: https://ai.google.dev/
- feedparser 文档: https://feedparser.readthedocs.io/
- Flask 文档: https://flask.palletsprojects.com/

