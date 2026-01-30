"""
论文分析和聚合服务
用于生成发展脉络总结和季度聚合
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

class PaperAnalysisService:
    """论文分析和聚合服务"""
    
    def __init__(self, ai_service=None):
        """
        初始化服务
        
        Args:
            ai_service: AI总结服务（可选）
        """
        self.ai_service = ai_service
    
    def generate_trajectory_summary(
        self,
        papers: List[Dict],
        max_length: int = 500
    ) -> Optional[str]:
        """
        生成论文的发展脉络总结
        
        对近3年的论文进行综合总结，说明研究方向的发展趋势
        
        Args:
            papers: 论文列表
            max_length: 总结最大字符数
            
        Returns:
            发展脉络总结文本，或None
        """
        if not papers:
            return None
        
        # 按发布时间排序，获取最新的论文信息
        sorted_papers = sorted(
            papers, 
            key=lambda p: p.get('published', '0'), 
            reverse=True
        )
        
        # 提取关键信息（最新的论文优先）
        titles = [p.get('title', '') for p in sorted_papers[:25]]  # 取前25篇
        summaries = [p.get('summary', '')[:150] for p in sorted_papers[:25]]
        
        # 提取发表地点信息用于分析
        venues = []
        for p in sorted_papers[:25]:
            venue = p.get('publication_venue')
            if venue:
                venues.append(venue)
        venue_info = ', '.join(set(venues[:10])) if venues else '多个学术期刊和会议'
        
        # 组织更详细的信息
        trajectory_text = f"""请根据以下{len(papers)}篇论文的信息，用中文生成一份学术领域发展脉络报告。

数据概览：
- 论文总数：{len(papers)}篇
- 分析时间跨度：过去3年
- 主要发表地点：{venue_info}

顶级论文（按新旧度排序）:
"""
        for i, (title, summary) in enumerate(zip(titles, summaries), 1):
            trajectory_text += f"\n{i}. 《{title}》\n   摘要概要：{summary}\n"
        
        trajectory_text += f"""
请生成一份不超过{max_length}个字符的中文发展脉络分析报告，包含以下要点（以段落形式呈现）：

1. **研究热点**：该领域当前的主要研究方向和热点问题
2. **关键进展**：过去3年中的重要学术突破和创新
3. **技术趋势**：正在快速发展的技术方向和方法
4. **未来展望**：基于当前趋势的可能发展方向

请简洁明了地表述，避免过度学术化，使其易于理解。"""
        
        # 如果有AI服务，使用AI生成总结
        if self.ai_service:
            try:
                response = self.ai_service.client.generate_content(trajectory_text)
                if response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[ERROR] Failed to generate trajectory summary: {e}")
        
        # 降级方案：生成基于数据的简单总结
        return self._generate_fallback_trajectory(papers)
    
    def _generate_fallback_trajectory(self, papers: List[Dict]) -> str:
        """
        生成回退的发展脉络总结（当AI服务不可用时）
        
        Args:
            papers: 论文列表
            
        Returns:
            基于数据统计的总结
        """
        if not papers:
            return None
        
        # 统计发表地点
        venues = defaultdict(int)
        for paper in papers:
            venue = paper.get('publication_venue')
            if venue:
                venues[venue] += 1
        
        # 按频率排序
        top_venues = sorted(venues.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 分析时间分布
        date_distribution = defaultdict(int)
        for paper in papers:
            published = paper.get('published', '')
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    year = pub_date.year
                    date_distribution[year] += 1
                except:
                    pass
        
        # 生成统计总结
        summary = f"""【研究概览】\n\n"""
        summary += f"本领域在过去3年共发表{len(papers)}篇研究论文，\n"
        
        if top_venues:
            venue_names = ', '.join([f"{v[0]}({v[1]}篇)" for v in top_venues[:3]])
            summary += f"主要发表在：{venue_names}等学术期刊和会议。\n\n"
        
        if date_distribution:
            years = sorted(date_distribution.keys())
            year_trends = ', '.join([f"{y}年({date_distribution[y]}篇)" for y in years])
            summary += f"【年度分布】\n{year_trends}\n\n"
        
        # 提取关键词（从标题中）
        keywords = defaultdict(int)
        for paper in papers[:30]:
            title = paper.get('title', '').lower()
            # 简单关键词提取（英文）
            for word in title.split():
                if len(word) > 4:
                    keywords[word.strip('()[],.;:?!')] += 1
        
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_keywords:
            keyword_str = ', '.join([kw[0] for kw in top_keywords[:5]])
            summary += f"【研究热词】\n{keyword_str}\n"
        
        return summary

    
    def group_papers_by_quarter(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按季度将论文分组
        
        Args:
            papers: 论文列表
            
        Returns:
            按季度分组的论文字典，键为 "2024-Q1" 这样的格式
        """
        quarters = defaultdict(list)
        
        for paper in papers:
            published = paper.get('published', '')
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    year = pub_date.year
                    month = pub_date.month
                    quarter = (month - 1) // 3 + 1
                    quarter_key = f"{year}-Q{quarter}"
                    quarters[quarter_key].append(paper)
                except:
                    # 如果解析失败，放在"未知"分类
                    quarters['Unknown'].append(paper)
        
        # 排序季度
        sorted_quarters = {}
        for key in sorted(quarters.keys(), reverse=True):
            sorted_quarters[key] = quarters[key]
        
        return sorted_quarters
    
    def generate_quarterly_summaries(
        self,
        papers: List[Dict],
        max_length: int = 300
    ) -> Dict[str, Optional[str]]:
        """
        为每个季度生成论文综述
        
        Args:
            papers: 论文列表
            max_length: 每个总结的最大字符数
            
        Returns:
            按季度的综述文本字典
        """
        quarters = self.group_papers_by_quarter(papers)
        summaries = {}
        
        for quarter_key, quarter_papers in quarters.items():
            if quarter_key == 'Unknown':
                continue
            
            summary = self._generate_quarter_summary(quarter_papers, quarter_key, max_length)
            summaries[quarter_key] = summary
        
        return summaries
    
    def _generate_quarter_summary(
        self,
        papers: List[Dict],
        quarter_key: str,
        max_length: int
    ) -> Optional[str]:
        """
        生成单个季度的综述
        
        Args:
            papers: 该季度的论文列表
            quarter_key: 季度标识符
            max_length: 最大字符数
            
        Returns:
            综述文本或None
        """
        if not papers:
            return None
        
        # 提取该季度的论文信息
        titles = [p.get('title', '') for p in papers[:15]]  # 取前15篇
        
        # 统计发表地点
        venues = defaultdict(int)
        for paper in papers:
            venue = paper.get('publication_venue')
            if venue:
                venues[venue] += 1
        top_venues = sorted(venues.items(), key=lambda x: x[1], reverse=True)[:3]
        venue_str = ', '.join([v[0] for v in top_venues]) if top_venues else "学术期刊和会议"
        
        prompt = f"""请根据以下{len(papers)}篇在{quarter_key}期间发表的论文信息，生成一份简洁的季度研究进展总结。

季度信息：
- 时间周期：{quarter_key}
- 论文数量：{len(papers)}篇
- 主要发表地：{venue_str}

论文标题（按重要性排序）:
"""
        for i, title in enumerate(titles, 1):
            prompt += f"{i}. {title}\n"
        
        prompt += f"""
请生成一份不超过{max_length}个字符的中文季度总结，简洁地描述：
1. 本季度该领域的主要研究热点
2. 出现的新颖研究方向
3. 技术应用的新进展
4. 值得关注的研究趋势

要求：使用学术但易懂的语言，避免过度专业化。"""
        
        # 如果有AI服务，使用AI生成
        if self.ai_service:
            try:
                response = self.ai_service.client.generate_content(prompt)
                if response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[ERROR] Failed to generate quarterly summary: {e}")
        
        # 降级方案：返回基于数据的简单总结
        return f"{quarter_key}: {len(papers)}篇论文，主要发表在{venue_str}"
    
    def get_quarterly_aggregates(
        self,
        papers: List[Dict]
    ) -> List[Dict]:
        """
        获取季度聚合数据
        
        Args:
            papers: 论文列表
            
        Returns:
            季度聚合数据列表
        """
        quarters = self.group_papers_by_quarter(papers)
        aggregates = []
        
        for quarter_key, quarter_papers in quarters.items():
            if quarter_key == 'Unknown':
                continue
            
            aggregate = {
                'quarter': quarter_key,
                'paper_count': len(quarter_papers),
                'papers': quarter_papers,
                'top_venues': self._extract_top_venues(quarter_papers),
                'sample_titles': [p.get('title', '') for p in quarter_papers[:3]]
            }
            aggregates.append(aggregate)
        
        return aggregates
    
    def _extract_top_venues(self, papers: List[Dict]) -> List[str]:
        """提取该季度论文的主要发表地点"""
        venues = defaultdict(int)
        
        for paper in papers:
            venue = paper.get('publication_venue')
            if venue:
                venues[venue] += 1
        
        # 按数量排序，返回前3个
        return [v for v, _ in sorted(venues.items(), key=lambda x: x[1], reverse=True)[:3]]
