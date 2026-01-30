# 论文信息增强 - 实现指南

## 功能说明

系统现在会自动为每篇论文添加以下信息：

### 1. **发表地点** (论文发表在什么会议或期刊)
- 例如: `CVPR`, `ICCV`, `JMLR`, `NeurIPS` 等
- 自动从论文标题和摘要中检测

### 2. **CCF等级** (中国计算机学会分类)
- `A` - 顶级会议/期刊
- `B` - 高级会议/期刊  
- `C` - 普通会议/期刊
- `N/A` - 未分类或国际期刊

### 3. **引用次数** (论文被引用的次数)
- 直接显示数字（例如: 156, 89 等）
- 可选：通过Google Scholar API获取实时数据

## 用户界面

### 论文卡片显示

每个论文卡片会显示：

```
arXiv ID
论文标题
发布时间       156 引用

[CVPR [CCF A]]  ← 发表会议/期刊和CCF等级

论文摘要...

[View] [PDF]
```

### 论文详情页面

点击论文打开详情，会显示：

```
论文标题
─────────────
作者: Author1, Author2
发布时间: 2024年1月15日
分类: cs.CV

发表会议/期刊: CVPR
CCF等级: A
引用次数: 156 次
```

## API端点

### 搜索API

```bash
GET /api/search?query=machine+learning&max_results=100
```

**响应中每篇论文包含：**
```json
{
  "arxiv_id": "2301.12345",
  "title": "Paper Title",
  "summary": "...",
  "published": "2023-01-15T00:00:00Z",
  "publication_venue": "CVPR",        // 新增：发表会议/期刊
  "publication_type": "conference",   // 新增：类型 (conference/journal)
  "ccf_grade": "A",                   // 新增：CCF等级
  "citation_count": 156               // 新增：引用次数
}
```

### 获取论文信息API

```bash
POST /api/authority/score
Content-Type: application/json

{
  "papers": [
    {
      "arxiv_id": "2301.12345",
      "title": "Paper Title",
      "summary": "Paper summary..."
    }
  ]
}
```

**响应：**
```json
{
  "status": "success",
  "data": [
    {
      "arxiv_id": "2301.12345",
      "title": "Paper Title",
      "publication_venue": "CVPR",
      "publication_type": "conference",
      "ccf_grade": "A",
      "citation_count": 156
    }
  ]
}
```

## 支持的会议和期刊

### CCF A类

**计算机视觉:**
- CVPR, ICCV, ECCV

**机器学习:**
- ICML, NeurIPS (NIPS), ICLR

**AI和算法:**
- AAAI, IJCAI

**自然语言处理:**
- ACL, EMNLP, NAACL

**信息检索:**
- SIGIR

**理论:**
- COLT, STOC, FOCS

### CCF B类

- ICPR, IJCNN, ICRA, IROS, KDD, SODA

### 期刊

**CCF A类期刊:**
- JMLR (Journal of Machine Learning Research)
- TPAMI (IEEE Transactions on Pattern Analysis and Machine Intelligence)
- IJCV (International Journal of Computer Vision)

**CCF B类期刊:**
- TNN, TSMC, JAIR

**顶级期刊:**
- Nature, Science

## 集成Google Scholar API（可选）

要获取实时引用数据，可以配置Google Scholar集成。

### 方式1：使用Scholarly库（免费）

```bash
pip install scholarly
```

然后系统会自动使用。注意：Google Scholar会对频繁请求进行限流。

### 方式2：使用SerpAPI（付费）

1. 在 https://serpapi.com/ 注册并获取API密钥
2. 在 `.env` 文件中添加：
   ```
   SERPAPI_API_KEY=your_api_key_here
   ```
3. 系统会自动使用SerpAPI获取引用数据

### 配置引用数据缓存

修改 `backend/services/authority_service.py` 中的缓存时间：

```python
self.cache_expiry = 7 * 24 * 3600  # 7天缓存，可根据需要修改
```

## 配置会议和期刊列表

如果需要添加或修改会议/期刊的CCF等级，编辑 `backend/services/authority_service.py`：

```python
def _load_conferences(self) -> Dict:
    return {
        'CVPR': {'name': '...', 'ccf': 'A'},
        'Your Conference': {'name': '...', 'ccf': 'A'},  # 新增
        # ...
    }
```

## 技术细节

### 会议/期刊检测

系统通过以下方式检测论文的发表地点：

1. **启发式匹配**：在论文标题和摘要中搜索会议/期刊缩写
2. **例如**：
   - 标题中包含 "CVPR 2024" → 检测为 CVPR (CCF A)
   - 摘要中包含 "JMLR" → 检测为 JMLR (CCF A)

### 引用次数获取

三个优先级的获取方式：

1. **缓存数据** (7天有效期)
2. **Google Scholar Scholarly库** (免费，可能限流)
3. **SerpAPI** (需要付费，推荐用于生产环境)

如果三种方式都失败，会返回 `null`。

### 缓存策略

- **搜索结果缓存**：30天（保存完整搜索结果）
- **引用数据缓存**：7天（每篇论文单独缓存）

## 常见问题

**Q: 为什么有些论文显示 "引用次数: null"？**

A: 论文的引用数据暂时无法获取，原因可能是：
- 系统未配置Google Scholar API
- 论文太新，Google Scholar还未收录
- 网络请求被限流

**Q: 如何更新会议列表？**

A: 会议列表在代码中硬编码。可以：
- 直接编辑源代码中的会议列表
- 通过Pull Request提交更新
- 提交Issue要求更新

**Q: 发表会议/期刊能自动检测吗？**

A: 是的，系统通过启发式匹配自动检测。但准确度取决于：
- 论文标题中是否包含会议名称
- 会议缩写是否在配置列表中

**Q: 可以禁用某些功能吗？**

A: 目前无法通过UI配置，但可以修改后端代码：
- 注释掉引用数获取逻辑
- 直接修改 `PaperEnhancementService` 的方法

## 实现细节

### PaperEnhancementService 类

主要方法：

```python
# 检测论文发表信息
pub_info = enhancement_service.detect_publication_info(paper)

# 获取引用次数
citation_count = enhancement_service.get_citation_count(paper)

# 为论文添加所有增强信息
enhanced_paper = enhancement_service.enrich_paper(paper)

# 批量处理
enhanced_papers = enhancement_service.enrich_papers(papers)
```

## 性能

- **发表信息检测**：<10ms/篇（简单字符串匹配）
- **引用数获取**：~500ms-2s/篇（取决于Google Scholar响应速度）
- **缓存命中**：<1ms（几乎无开销）

建议：
- 缓存引用数据7天以上
- 对大批量查询使用SerpAPI（更稳定）
- 考虑异步获取引用数据以提高响应速度

## 贡献

如有问题或改进建议，欢迎提交Issue或PR：
https://github.com/LinkyuW/arxiv-tracker
