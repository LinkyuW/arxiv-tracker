# 权威性排序功能 - 快速使用指南

## 🎯 核心概念

系统现在会自动识别和突出显示**最权威的论文**，包括：

- **CCF A类会议** 的论文（如CVPR、ICCV、ICML、NeurIPS等）
- **顶级期刊** 的论文（如JMLR、TPAMI、IJCV等）  
- **高被引** 的论文（100次以上引用）
- **最新发表** 的论文

## 📊 权威性评分

### 评分等级

| 等级 | 分数 | 说明 |
|------|------|------|
| ★★★ | 85-100 | 顶级论文 - CCF A类会议或顶级期刊发表 |
| ★★ | 70-84 | 高质量论文 - 有一定权威性和引用 |
| ★ | 50-69 | 中等论文 - 基础研究论文 |
| ○ | 0-49 | 普通论文 - 新发表或非顶级期刊 |

### 计分规则

```
总分 = CCF A类会议(0-30分) + 顶级期刊(0-25分) + 引用次数(0-30分) + 发表时间(0-15分)

- CCF A类会议：CVPR、ICCV、ICML、NeurIPS等 → +30分
- 顶级期刊：JMLR、TPAMI、IJCV等 → +25分
- 引用次数：
  * 100+ 引用 → +30分 (显示 [Citation-100+])
  * 10-100 引用 → +15分 (显示 [Citation-50])
  * 0-10 引用 → +5分
- 发表年份：
  * 本年发表 → +15分 (显示 [Recent])
  * 去年发表 → +10分
  * 近3年发表 → +5分
```

## 🚀 使用方法

### 第1步：启用权威性排序

1. 打开应用
2. 在搜索选项中确保 **"按权威性排序"** 被勾选（默认已启用）
3. 输入搜索关键词，点击搜索

### 第2步：查看排序结果

搜索结果会**自动按权威性从高到低排序**，最权威的论文在最前面。

### 第3步：识别权威性标签

在每个论文卡片上，你会看到：

```
论文卡片
├── 权威等级显示：★★★ 85分  ← 右上角
├── 论文标题
├── 发表时间
└── 标签：[CCF-A] [Citation-100+] [Recent]  ← 表示这篇论文的特点
```

### 第4步：查看详细信息

点击论文卡片打开详情，查看：
- **权威性评分**：0-100分
- **权威等级**：★★★ / ★★ / ★ / ○
- **引用次数**：被引用了多少次
- **评分原因**：列出为什么这篇论文权威性高

示例：
```
权威性评分: 87/100
权威等级: ★★★
引用次数: 156
评分原因: CCF A类会议论文; 高引用次数(156+); 最新发表
```

## 📌 常见论文类型识别

### CCF A类会议论文 [CCF-A]

这些是计算机科学领域**最顶级的会议**：

**计算机视觉:**
- CVPR (IEEE/CVF Conference on Computer Vision and Pattern Recognition)
- ICCV (International Conference on Computer Vision)
- ECCV (European Conference on Computer Vision)

**机器学习:**
- ICML (International Conference on Machine Learning)
- NeurIPS (Neural Information Processing Systems)
- ICLR (International Conference on Learning Representations)

**AI和算法:**
- AAAI (AAAI Conference on Artificial Intelligence)
- IJCAI (International Joint Conference on Artificial Intelligence)

**自然语言处理:**
- ACL (Association for Computational Linguistics)
- EMNLP (Empirical Methods in Natural Language Processing)

### 顶级期刊论文 [Top-Journal]

- JMLR (Journal of Machine Learning Research)
- TPAMI (IEEE Transactions on Pattern Analysis and Machine Intelligence)
- IJCV (International Journal of Computer Vision)
- Nature / Science

### 高被引论文 [Citation-100+]

被学术界广泛引用的论文（通常100次以上引用）

### 最新论文 [Recent]

2024年发表的论文

## 💡 实际应用场景

### 场景1：找最新的最佳实践

```
搜索关键词：transformer attention mechanism
↓
权威性排序自动将以下论文排到最前面：
1. CVPR 2024 - "Efficient Transformer..." (★★★ 92分)
2. ICCV 2024 - "Vision Transformer v3..." (★★★ 89分)
3. ICML 2023 - "Attention is All..." (★★★ 87分)
```

### 场景2：找到领域的开创性工作

```
搜索关键词：deep learning foundations
↓
权威性排序会突出：
1. 高被引论文：ResNet, VGG, AlexNet等 (Citation-1000+)
2. CCF A类会议论文
3. 顶级期刊论文
```

### 场景3：了解某个技术的发展历程

```
1. 点击"按权威性排序"查看权威论文
2. 按时间顺序查看从基础工作到最新进展
3. 通过评分原因了解每篇论文的重要性
```

## ⚙️ 可选设置

### 禁用权威性排序

如果想按**发表时间**排序（最新的论文在前）：

1. 取消勾选 **"按权威性排序"**
2. 结果会按发表时间从新到旧排序

### 自定义权威性权重

如果是开发者，可以编辑：

文件位置：`backend/config/ccf_conferences.json`

修改会议的权重值（0-10）来调整评分。

## 🔍 常见问题

**Q: 为什么某篇来自小会议的论文排序较后？**

A: 权威性评分基于会议/期刊的影响力。小会议的论文通常权威性评分较低，除非被高度引用。

**Q: 如何区分"最新"和"最权威"？**

A: 
- **最权威** = 按权威性排序（默认）→ 顶级会议+高被引
- **最新** = 取消勾选"按权威性排序" → 按发表时间排序

**Q: 引用次数是实时的吗？**

A: 目前使用缓存的数据（可能延迟几天）。系统设计支持集成Google Scholar API获取实时数据。

## 📚 与AI总结的结合使用

权威性排序 + AI总结 = 最强组合：

```
1. 勾选"使用AI总结" 和 "按权威性排序"
2. 搜索关键词
3. 系统会：
   ① 找到相关论文
   ② 按权威性排序（最权威在前）
   ③ 生成中文总结（基于Gemini AI）
   ④ 显示权威性标签和评分
```

这样你可以**快速把握某个领域最权威的观点和进展**。

## 🎓 学术研究建议

### 文献综述时

1. 启用权威性排序
2. 先读 ★★★ 的论文（顶级会议/期刊）
3. 再补充 ★★ 的高质量工作
4. 根据需要参考 ★ 的论文

### 跟踪研究热点

1. 搜索热门关键词（如"diffusion model", "large language model"）
2. 权威性排序会自动把最新的顶级会议论文排在前面
3. 快速了解最新动向

## 📖 更多信息

详细的技术文档请参考：[AUTHORITY_GUIDE.md](AUTHORITY_GUIDE.md)

## 🐛 反馈和改进

如有问题或建议，欢迎提Issue：
https://github.com/LinkyuW/arxiv-tracker/issues
