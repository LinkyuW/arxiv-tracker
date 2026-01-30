"""
论文权威性评分服务
用于获取论文的引用次数、发表会议等信息，并计算权威性评分
"""
import requests
from typing import Dict, Optional, List
import json
import time
from datetime import datetime, timedelta

class AuthorityService:
    """论文权威性评分服务"""
    
    def __init__(self):
        """初始化权威性评分服务"""
        self.cache = {}
        self.cache_expiry = 7 * 24 * 3600  # 7天缓存
        
        # CCF A类会议列表
        self.ccf_a_conferences = self._load_ccf_conferences()
        
        # 权威期刊列表 (顶级AI/ML期刊)
        self.top_journals = {
            'JMLR',  # Journal of Machine Learning Research
            'TPAMI',  # IEEE TPAMI
            'IJCV',   # International Journal of Computer Vision
            'Neural Networks',
            'JAIR',   # Journal of AI Research
            'MLJ',    # Machine Learning Journal
            'TNN',    # IEEE TNN
            'TSMC',   # IEEE TSMC
        }
    
    def _load_ccf_conferences(self) -> Dict[str, int]:
        """加载CCF A类会议列表，返回会议和权重"""
        return {
            # 计算机视觉
            'CVPR': 10,
            'ICCV': 10,
            'ECCV': 10,
            
            # 机器学习和AI
            'ICML': 10,
            'NeurIPS': 10,
            'ICLR': 9,
            'AAAI': 9,
            'IJCAI': 9,
            
            # 自然语言处理
            'ACL': 9,
            'EMNLP': 9,
            'NAACL': 9,
            
            # 其他AI顶级会议
            'JMLR': 9,  # 期刊，但权威性极高
            'Science': 10,
            'Nature': 10,
            'Nature Machine Intelligence': 10,
        }
    
    def calculate_authority_score(
        self,
        paper: Dict,
        citation_count: Optional[int] = None,
        is_ccf_a: bool = False
    ) -> Dict:
        """
        计算论文的权威性评分
        
        Args:
            paper: 论文信息字典
            citation_count: 引用次数（可选，如果为None则尝试获取）
            is_ccf_a: 是否是CCF A类会议论文
            
        Returns:
            包含评分和元数据的字典
        """
        score = 0
        reasons = []
        badges = []
        
        # 1. CCF A类会议标识 (权重: 30分)
        if is_ccf_a:
            score += 30
            reasons.append('CCF A类会议论文')
            badges.append('CCF-A')
        elif self._check_ccf_a_from_metadata(paper):
            score += 30
            reasons.append('CCF A类会议论文（从元数据识别）')
            badges.append('CCF-A')
        
        # 2. 权威期刊 (权重: 25分)
        if self._check_top_journal(paper):
            score += 25
            reasons.append('顶级权威期刊')
            badges.append('Top-Journal')
        
        # 3. 引用次数 (权重: 30分)
        if citation_count is None:
            # 尝试从缓存或外部API获取
            citation_count = self._get_citation_count(paper)
        
        if citation_count is not None and citation_count > 0:
            # 对数增长：0-10引用=5分，10-100=15分，100+=30分
            if citation_count >= 100:
                score += 30
                badges.append(f'Citation-{citation_count}+')
                reasons.append(f'高引用次数（{citation_count}+）')
            elif citation_count >= 10:
                score += 15
                badges.append(f'Citation-{citation_count}')
                reasons.append(f'中等引用次数（{citation_count}）')
            else:
                score += 5
                reasons.append(f'低引用次数（{citation_count}）')
        
        # 4. 发表年份 (权重: 15分，最近的更权威)
        published_date = paper.get('published', '')
        if published_date:
            try:
                pub_year = datetime.fromisoformat(published_date.replace('Z', '+00:00')).year
                current_year = datetime.now().year
                years_ago = current_year - pub_year
                
                if years_ago == 0:
                    score += 15
                    reasons.append('最新发表')
                    badges.append('Recent')
                elif years_ago == 1:
                    score += 10
                    reasons.append('去年发表')
                elif years_ago <= 3:
                    score += 5
                    reasons.append('近年发表')
            except:
                pass
        
        return {
            'authority_score': min(score, 100),  # 最高100分
            'reasons': reasons,
            'badges': badges,
            'citation_count': citation_count,
            'level': self._score_to_level(score)
        }
    
    def _score_to_level(self, score: int) -> str:
        """将评分转换为等级"""
        if score >= 85:
            return '★★★'  # 顶级
        elif score >= 70:
            return '★★'   # 高级
        elif score >= 50:
            return '★'    # 中级
        else:
            return '○'    # 普通
    
    def _check_ccf_a_from_metadata(self, paper: Dict) -> bool:
        """从论文元数据中检查是否是CCF A类会议"""
        title = paper.get('title', '').upper()
        arxiv_id = paper.get('arxiv_id', '')
        
        # 简单的启发式检查：在标题或分类中查找CCF A会议名称
        for conf in self.ccf_a_conferences.keys():
            if conf.upper() in title:
                return True
        
        return False
    
    def _check_top_journal(self, paper: Dict) -> bool:
        """检查是否发表在顶级期刊"""
        title = paper.get('title', '').upper()
        summary = paper.get('summary', '').upper()
        
        for journal in self.top_journals:
            if journal.upper() in title or journal.upper() in summary:
                return True
        
        return False
    
    def _get_citation_count(self, paper: Dict) -> Optional[int]:
        """
        获取论文的引用次数（通过缓存或API）
        
        Args:
            paper: 论文信息
            
        Returns:
            引用次数，获取失败则返回None
        """
        arxiv_id = paper.get('arxiv_id', '')
        title = paper.get('title', '')
        
        # 检查缓存
        cache_key = f'citations:{arxiv_id}'
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_expiry:
                return cached_data
        
        # 尝试通过Google Scholar API获取（这里需要配置API密钥）
        # 暂时返回None，需要配置额外的API服务
        # citation_count = self._query_google_scholar(title)
        
        # 临时方案：使用启发式估计
        # 可以基于论文年份和发表会议
        return None
    
    def sort_papers_by_authority(
        self,
        papers: List[Dict]
    ) -> List[Dict]:
        """
        按权威性排序论文
        
        Args:
            papers: 论文列表
            
        Returns:
            排序后的论文列表（权威性高的在前）
        """
        papers_with_score = []
        
        for paper in papers:
            authority_info = self.calculate_authority_score(paper)
            papers_with_score.append({
                **paper,
                **authority_info
            })
        
        # 按评分从高到低排序
        return sorted(
            papers_with_score,
            key=lambda x: (
                x['authority_score'],
                x['citation_count'] if x['citation_count'] else 0
            ),
            reverse=True
        )
    
    def batch_calculate_authority(
        self,
        papers: List[Dict]
    ) -> List[Dict]:
        """
        批量计算论文权威性
        
        Args:
            papers: 论文列表
            
        Returns:
            带有权威性评分的论文列表
        """
        results = []
        
        for paper in papers:
            authority_info = self.calculate_authority_score(paper)
            results.append({
                'arxiv_id': paper.get('arxiv_id', ''),
                'title': paper.get('title', ''),
                **authority_info
            })
        
        return results
    
    def add_to_cache(self, arxiv_id: str, citation_count: int):
        """缓存引用次数"""
        self.cache[f'citations:{arxiv_id}'] = (citation_count, time.time())
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
