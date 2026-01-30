"""
arXiv API 服务模块
用于获取和处理arXiv论文数据
"""
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import urllib.parse

class ArxivService:
    """arXiv数据获取服务"""
    
    BASE_URL = 'http://export.arxiv.org/api/query'
    
    def __init__(self, max_results: int = 100, timeout: int = 30):
        """
        初始化arXiv服务
        
        Args:
            max_results: 单次查询最大论文数
            timeout: 请求超时时间（秒）
        """
        self.max_results = max_results
        self.timeout = timeout
    
    def search_papers(
        self, 
        query: str, 
        days_back: int = 365 * 5,
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        搜索arXiv上的论文
        
        Args:
            query: 搜索关键词
            days_back: 搜索多少天内的论文（默认5年）
            max_results: 返回结果数量
            
        Returns:
            论文列表，包含标题、摘要、作者、发布日期等信息
        """
        max_results = max_results or self.max_results
        
        # arXiv API 查询格式：在所有字段中搜索
        # 简化查询，直接搜索关键词，不限制日期
        search_query = f'all:{query}'
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            print(f"[DEBUG] Searching arXiv with query: {search_query}")
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            print(f"[DEBUG] Response status: {response.status_code}")
            response.raise_for_status()
            
            # 解析RSS feed
            feed = feedparser.parse(response.content)
            print(f"[DEBUG] Found {len(feed.entries)} entries")
            
            papers = []
            for entry in feed.entries:
                paper = self._parse_entry(entry)
                papers.append(paper)
            
            return papers
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from arXiv: {e}")
            return []
    
    def _parse_entry(self, entry) -> Dict:
        """
        解析arXiv feed条目
        
        Args:
            entry: feedparser的entry对象
            
        Returns:
            解析后的论文信息字典
        """
        # 提取作者
        authors = [author.name for author in entry.get('authors', [])]
        
        # 处理论文ID（从arXiv URL中提取）
        arxiv_id = entry.id.split('/abs/')[-1]
        
        # 发布时间
        published = entry.get('published', '')
        
        paper = {
            'arxiv_id': arxiv_id,
            'title': entry.get('title', '').strip(),
            'authors': authors,
            'summary': entry.get('summary', '').strip(),
            'published': published,
            'url': entry.get('id', ''),
            'pdf_url': f'https://arxiv.org/pdf/{arxiv_id}.pdf',
            'categories': entry.get('arxiv_primary_category', {}).get('term', ''),
        }
        
        return paper
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict]:
        """
        根据arXiv ID获取单篇论文
        
        Args:
            arxiv_id: arXiv论文ID
            
        Returns:
            论文信息字典
        """
        params = {
            'search_query': f'arxiv:{arxiv_id}',
            'max_results': 1
        }
        
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                return self._parse_entry(feed.entries[0])
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching paper {arxiv_id}: {e}")
            return None
