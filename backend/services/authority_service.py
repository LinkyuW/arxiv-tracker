"""
论文信息增强服务
用于检测论文发表的会议/期刊，和获取引用次数
"""
import requests
from typing import Dict, Optional, List, Tuple
import json
import time
from datetime import datetime, timedelta

class PaperEnhancementService:
    """论文信息增强服务 - 获取会议/期刊信息和引用数据"""
    
    def __init__(self):
        """初始化服务"""
        self.cache = {}
        self.cache_expiry = 7 * 24 * 3600  # 7天缓存
        
        # 加载会议和期刊配置
        self.conferences = self._load_conferences()
        self.journals = self._load_journals()
    
    def _load_conferences(self) -> Dict:
        """加载会议配置"""
        return {
            # CCF A类
            'CVPR': {'name': 'IEEE/CVF Conference on Computer Vision and Pattern Recognition', 'ccf': 'A'},
            'ICCV': {'name': 'International Conference on Computer Vision', 'ccf': 'A'},
            'ECCV': {'name': 'European Conference on Computer Vision', 'ccf': 'A'},
            'ICML': {'name': 'International Conference on Machine Learning', 'ccf': 'A'},
            'NeurIPS': {'name': 'Neural Information Processing Systems', 'ccf': 'A', 'aliases': ['NIPS']},
            'ICLR': {'name': 'International Conference on Learning Representations', 'ccf': 'A'},
            'AAAI': {'name': 'AAAI Conference on Artificial Intelligence', 'ccf': 'A'},
            'IJCAI': {'name': 'International Joint Conference on Artificial Intelligence', 'ccf': 'A'},
            'ACL': {'name': 'Annual Meeting of the Association for Computational Linguistics', 'ccf': 'A'},
            'EMNLP': {'name': 'Conference on Empirical Methods in Natural Language Processing', 'ccf': 'A'},
            'NAACL': {'name': 'North American Chapter of ACL', 'ccf': 'A'},
            'SIGIR': {'name': 'Special Interest Group on Information Retrieval', 'ccf': 'A'},
            'COLT': {'name': 'Conference on Learning Theory', 'ccf': 'A'},
            'STOC': {'name': 'ACM Symposium on Theory of Computing', 'ccf': 'A'},
            'FOCS': {'name': 'IEEE Symposium on Foundations of Computer Science', 'ccf': 'A'},
            
            # CCF B类
            'ICPR': {'name': 'International Conference on Pattern Recognition', 'ccf': 'B'},
            'IJCNN': {'name': 'International Joint Conference on Neural Networks', 'ccf': 'B'},
            'ICRA': {'name': 'IEEE International Conference on Robotics and Automation', 'ccf': 'B'},
            'IROS': {'name': 'IEEE/RSJ International Conference on Intelligent Robots and Systems', 'ccf': 'B'},
            'KDD': {'name': 'ACM SIGKDD Conference on Knowledge Discovery and Data Mining', 'ccf': 'B'},
            'NIPS': {'name': 'Neural Information Processing Systems', 'ccf': 'A'},  # NIPS = NeurIPS
            'SODA': {'name': 'Symposium on Discrete Algorithms', 'ccf': 'B'},
            
            # CCF C类
            'CAI': {'name': 'China AI Conference', 'ccf': 'C'},
        }
    
    def _load_journals(self) -> Dict:
        """加载期刊配置"""
        return {
            # CCF A类期刊
            'JMLR': {'name': 'Journal of Machine Learning Research', 'ccf': 'A'},
            'TPAMI': {'name': 'IEEE TPAMI', 'ccf': 'A'},
            'IJCV': {'name': 'International Journal of Computer Vision', 'ccf': 'A'},
            
            # CCF B类期刊
            'TNN': {'name': 'IEEE Transactions on Neural Networks', 'ccf': 'B'},
            'TSMC': {'name': 'IEEE TSMC', 'ccf': 'B'},
            'JAIR': {'name': 'Journal of AI Research', 'ccf': 'B'},
            
            # 顶级期刊（即使不在CCF中，也要标注）
            'Nature': {'name': 'Nature', 'ccf': 'N/A', 'prestigious': True},
            'Science': {'name': 'Science', 'ccf': 'N/A', 'prestigious': True},
        }
    
    def detect_publication_info(self, paper: Dict) -> Dict:
        """
        检测论文的发表信息（会议/期刊 + CCF等级）
        
        Args:
            paper: 论文信息字典
            
        Returns:
            发表信息字典，包含会议/期刊名称、CCF等级等
        """
        title = paper.get('title', '').upper()
        summary = paper.get('summary', '').upper()
        
        publication_info = {
            'venue': None,  # 会议/期刊名称
            'venue_type': None,  # 'conference' or 'journal'
            'ccf_grade': None,  # 'A', 'B', 'C' 或 None
            'is_prestigious': False,  # 是否是顶级期刊/会议
        }
        
        # 检测会议
        for conf_abbr, conf_info in self.conferences.items():
            if conf_abbr.upper() in title or conf_abbr.upper() in summary:
                publication_info['venue'] = conf_abbr
                publication_info['venue_type'] = 'conference'
                publication_info['ccf_grade'] = conf_info['ccf']
                publication_info['is_prestigious'] = conf_info['ccf'] == 'A'
                return publication_info
        
        # 检测期刊
        for journal_abbr, journal_info in self.journals.items():
            if journal_abbr.upper() in title or journal_abbr.upper() in summary:
                publication_info['venue'] = journal_abbr
                publication_info['venue_type'] = 'journal'
                publication_info['ccf_grade'] = journal_info['ccf']
                publication_info['is_prestigious'] = journal_info.get('prestigious', False) or journal_info['ccf'] == 'A'
                return publication_info
        
        return publication_info
    
    def get_citation_count(self, paper: Dict) -> Optional[int]:
        """
        获取论文的引用次数
        
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
        
        # 尝试通过Google Scholar API获取
        citation_count = self._fetch_from_google_scholar(title)
        
        # 缓存结果
        if citation_count is not None:
            self.add_to_cache(arxiv_id, citation_count)
        
        return citation_count
    
    def _fetch_from_google_scholar(self, title: str) -> Optional[int]:
        """
        从Google Scholar获取论文引用次数（可选功能）
        
        支持两种方式：
        1. 使用 SerpAPI (推荐) - 需要API密钥
        2. 使用 scholarly 库 - 免费但可能被限流
        
        这个功能是可选的，失败不会影响系统运行
        
        Args:
            title: 论文标题
            
        Returns:
            引用次数或None
        """
        # 默认关闭，防止错误日志
        # 如果用户想使用，需要在代码中显式启用
        return None
    
    def _fetch_via_serpapi(self, title: str, api_key: str) -> Optional[int]:
        """
        使用 SerpAPI 获取引用次数（需要付费）
        
        Args:
            title: 论文标题
            api_key: SerpAPI密钥
            
        Returns:
            引用次数或None
        """
        try:
            url = 'https://serpapi.com/search'
            params = {
                'q': title,
                'engine': 'google_scholar',
                'api_key': api_key,
                'hl': 'en',
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'organic_results' in data and len(data['organic_results']) > 0:
                    first_result = data['organic_results'][0]
                    return first_result.get('inline_links', {}).get('cited_by', {}).get('total', None)
            
            return None
        except Exception as e:
            print(f"[ERROR] SerpAPI error: {e}")
            return None
    
    def enrich_paper(self, paper: Dict, citation_count: Optional[int] = None) -> Dict:
        """
        为论文添加增强信息
        
        Args:
            paper: 原始论文数据
            citation_count: 可选的引用次数
            
        Returns:
            添加了发表信息和引用数的论文数据
        """
        # 检测发表信息
        pub_info = self.detect_publication_info(paper)
        
        # 获取引用数
        if citation_count is None:
            citation_count = self.get_citation_count(paper)
        
        # 返回增强后的论文数据
        return {
            **paper,
            'publication_venue': pub_info['venue'],
            'publication_type': pub_info['venue_type'],
            'ccf_grade': pub_info['ccf_grade'],
            'citation_count': citation_count,
        }
    
    def enrich_papers(self, papers: List[Dict]) -> List[Dict]:
        """批量增强论文信息"""
        return [self.enrich_paper(p) for p in papers]
    
    def add_to_cache(self, arxiv_id: str, citation_count: int):
        """缓存引用次数"""
        self.cache[f'citations:{arxiv_id}'] = (citation_count, time.time())
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
