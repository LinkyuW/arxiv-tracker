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
        
        # 提取关键信息
        titles = [p.get('title', '') for p in papers[:20]]  # 取前20篇
        summaries = [p.get('summary', '')[:200] for p in papers[:20]]
        
        # 组织信息
        trajectory_text = f"""请根据以下{len(papers)}篇论文的信息，用中文总结近3年该领域的发展脉络和趋势：

论文数量: {len(papers)}篇
时间跨度: 过去3年

主要论文（按相关度）:
"""
        for i, (title, summary) in enumerate(zip(titles, summaries), 1):
            trajectory_text += f"\n{i}. 标题: {title}\n   摘要: {summary}\n"
        
        trajectory_text += f"\n请用不超过{max_length}个字符的中文总结：\n1. 该领域的主要研究方向\n2. 近3年的重要进展\n3. 当前的技术趋势\n4. 未来可能的发展方向"
        
        # 如果有AI服务，使用AI生成总结
        if self.ai_service:
            try:
                response = self.ai_service.client.generate_content(trajectory_text)
                if response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[ERROR] Failed to generate trajectory summary: {e}")
        
        return None
    
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
        titles = [p.get('title', '') for p in papers[:10]]  # 取前10篇
        
        prompt = f"""请根据以下{len(papers)}篇{quarter_key}期间发表的论文标题，用中文撰写一篇简短的季度综述（不超过{max_length}个字符）：

论文标题：
"""
        for i, title in enumerate(titles, 1):
            prompt += f"{i}. {title}\n"
        
        prompt += f"\n请总结这个季度该领域的主要研究热点和进展（约{max_length}字）"
        
        # 如果有AI服务，使用AI生成
        if self.ai_service:
            try:
                response = self.ai_service.client.generate_content(prompt)
                if response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[ERROR] Failed to generate quarterly summary: {e}")
        
        # 降级方案：返回论文数和标题列表
        return f"{quarter_key}: 共{len(papers)}篇论文\n主要论文: {', '.join(titles[:3])}"
    
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
