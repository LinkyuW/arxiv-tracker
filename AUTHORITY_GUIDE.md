# 论文权威性评分系统 - 实现指南

## 概述

本系统通过集成多个维度的评分标准，将**最权威、最高质量的论文**自动排在搜索结果的前面，并用醒目的标签突出显示。

## 核心功能

### 1. 权威性评分算法

论文的权威性评分由以下4个维度组成（总分100分）：

| 维度 | 权重 | 评分规则 |
|-----|------|--------|
| **CCF A类会议** | 30分 | 发表在CVPR、ICCV、ECCV、ICML、NeurIPS等顶级会议 |
| **权威期刊** | 25分 | 发表在JMLR、TPAMI、IJCV等顶级期刊 |
| **引用次数** | 30分 | 0-10次=5分，10-100次=15分，100+次=30分 |
| **发表年份** | 15分 | 最新(0年)=15分，去年=10分，近年=5分 |

**评分等级：**
- ★★★ (85-100分): 顶级论文
- ★★ (70-84分): 高质量论文  
- ★ (50-69分): 中等论文
- ○ (0-49分): 普通论文

### 2. 可视化标签

论文卡片上会显示以下标签：

```
[CCF-A]       # 如果发表在CCF A类会议
[Top-Journal] # 如果发表在顶级期刊
[Citation-100+] # 如果被高度引用
[Recent]      # 如果是最近发表
```

## 技术架构

### 后端架构

```
backend/
├── services/
│   ├── arxiv_service.py       # arXiv数据获取
│   ├── authority_service.py   # 权威性评分 (新增)
│   ├── ai_service.py          # AI总结
│   └── cache_service.py       # 缓存管理
├── config/
│   └── ccf_conferences.json   # CCF会议配置 (新增)
├── app.py                     # 主应用 (已更新)
└── requirements.txt
```

### 前端架构

```
frontend/
├── src/
│   └── main.js               # 主程序 (已更新)
├── index.html                # 页面 (已更新)
└── style.css                 # 样式 (已更新)
```

## API接口说明

### 1. 搜索API（已更新）

**请求：**
```bash
GET /api/search?query=machine+learning&max_results=100&enable_authority=true&sort_by=authority
```

**参数：**
- `query` (必需): 搜索关键词
- `max_results` (可选, 默认100): 返回论文数
- `enable_authority` (可选, 默认true): 是否启用权威性评分
- `sort_by` (可选, 默认authority): 排序方式 (authority/date)

**响应：**
```json
{
  "status": "success",
  "message": "找到 50 篇论文",
  "data": [
    {
      "arxiv_id": "2301.12345",
      "title": "Example Paper",
      "summary": "...",
      "published": "2023-01-15T00:00:00Z",
      "authority_score": 85,
      "level": "★★★",
      "badges": ["CCF-A", "Citation-100+"],
      "citation_count": 150,
      "reasons": ["CCF A类会议论文", "高引用次数(150+)", "最新发表"]
    }
  ],
  "from_cache": false,
  "sort_by": "authority"
}
```

### 2. 权威性评分API（新增）

**请求：**
```bash
POST /api/authority/score
Content-Type: application/json

{
  "papers": [
    {
      "arxiv_id": "2301.12345",
      "title": "Paper Title",
      "summary": "Paper summary...",
      "published": "2023-01-15T00:00:00Z"
    }
  ]
}
```

**响应：**
```json
{
  "status": "success",
  "message": "计算了 1 篇论文的权威性",
  "data": [
    {
      "arxiv_id": "2301.12345",
      "title": "Paper Title",
      "authority_score": 85,
      "reasons": ["CCF A类会议论文", "高引用次数(150+)"],
      "badges": ["CCF-A", "Citation-100+"],
      "citation_count": 150,
      "level": "★★★"
    }
  ]
}
```

## 使用方式

### 用户端

1. **启用权威性排序**（默认启用）
   - 在搜索选项中勾选"按权威性排序"

2. **查看权威性标签**
   - 论文卡片右上角会显示权威性评分
   - 下方会显示具体的标签（CCF-A、Citation-100+等）

3. **查看详细评分信息**
   - 点击论文卡片打开详情
   - 在"权威性评分"部分查看：
     - 总评分（0-100）
     - 权威等级（★★★ / ★★ / ★ / ○）
     - 引用次数
     - 评分原因

### 开发者集成

在后端代码中使用权威性服务：

```python
from services.authority_service import AuthorityService

# 初始化服务
authority_service = AuthorityService()

# 为单篇论文计算权威性
paper = {...}
authority_info = authority_service.calculate_authority_score(paper)

# 按权威性排序论文列表
papers = [...]
sorted_papers = authority_service.sort_papers_by_authority(papers)
```

## 配置说明

### CCF会议配置

文件：`backend/config/ccf_conferences.json`

包含所有CCF A类会议的列表，每个会议都有：
- 全称（英文）
- 分类
- 权重系数
- 别名列表

可以根据最新的CCF排名更新此文件。

### 扩展功能

#### 集成Google Scholar Citation API

如果要获取实时引用次数，可以：

1. 从Google Scholar获取API密钥
2. 在`authority_service.py`中实现`_query_google_scholar()`方法
3. 配置缓存机制，避免频繁调用API

示例代码框架：

```python
def _query_google_scholar(self, title: str) -> Optional[int]:
    """
    从Google Scholar获取论文引用次数
    
    需要安装: pip install scholarly
    """
    from scholarly import scholarly
    
    try:
        search_query = scholarly.search_pubs(title)
        pub = next(search_query)
        citation_count = pub.get('num_citations', 0)
        return citation_count
    except:
        return None
```

## 性能优化

### 缓存策略

1. **搜索结果缓存**
   - 缓存完整搜索结果（包含权威性评分）
   - 缓存时间：30天（可配置）

2. **引用数据缓存**
   - 每篇论文的引用数单独缓存
   - 缓存时间：7天
   - 可通过API清空

### 并发处理

权威性评分的计算是轻量级的（通过启发式规则），不会产生显著性能瓶颈。

## 未来改进方向

1. **动态引用数据**
   - 集成Google Scholar API获取实时引用数
   - 定期更新论文的引用数据

2. **作者声望评分**
   - 基于作者的H-Index
   - 基于作者的论文发表历史

3. **机器学习排序**
   - 基于用户点击行为优化排序
   - 学习用户的偏好

4. **细粒度分类**
   - 按领域细分CCF会议
   - 针对不同领域的用户提供定制排序

5. **社区评分**
   - 用户可以对论文的权威性进行评分
   - 基于社区评分优化算法

## 常见问题

**Q: 为什么某篇论文的权威性评分较低？**

A: 权威性评分基于客观指标（发表地点、年份、引用数）。如果论文：
- 未发表在CCF A类会议
- 发表时间较早
- 引用次数较少

则评分会较低。这是正常的。

**Q: 如何手动调整权威性评分？**

A: 目前系统完全基于自动化算法。可以：
- 修改`ccf_conferences.json`调整会议权重
- 修改`authority_service.py`中的评分逻辑
- 手动添加论文到"收藏"或"标记"系统

**Q: 是否支持自定义排序权重？**

A: 当前不支持用户界面配置。可以：
- 修改源代码中的权重配置
- 提出Feature Request，我们会考虑添加UI配置

## 支持和贡献

如有问题或建议，请提交Issue或PR到：
https://github.com/LinkyuW/arxiv-tracker
