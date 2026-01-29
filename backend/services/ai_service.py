"""
AI 总结服务模块
用于调用Google Gemini API对论文进行总结
"""
import google.generativeai as genai
from typing import Optional

class AIService:
    """AI论文总结服务"""
    
    def __init__(self, api_key: str, model: str = 'gemini-pro'):
        """
        初始化AI服务
        
        Args:
            api_key: Google Gemini API密钥
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.model = model
        
        # 配置genai
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
    
    def summarize_paper(
        self, 
        title: str, 
        abstract: str,
        max_length: int = 200
    ) -> Optional[str]:
        """
        使用AI对论文进行总结
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            max_length: 总结最大字符数
            
        Returns:
            AI生成的总结，失败返回None
        """
        prompt = f"""请对以下学术论文进行简洁总结，用中文回答：

论文标题：{title}

论文摘要：
{abstract}

请用不超过{max_length}个字符的中文总结这篇论文的主要内容、创新点和实际应用意义。"""
        
        try:
            response = self.client.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            
            return None
            
        except Exception as e:
            print(f"Error summarizing paper: {e}")
            return None
    
    def extract_keywords(self, abstract: str) -> Optional[list]:
        """
        从摘要中提取关键词
        
        Args:
            abstract: 论文摘要
            
        Returns:
            关键词列表
        """
        prompt = f"""请从以下论文摘要中提取5-10个最重要的关键词，用中文回答，以逗号分隔：

{abstract}

只返回关键词列表，不需要其他说明。"""
        
        try:
            response = self.client.generate_content(prompt)
            
            if response.text:
                keywords = [kw.strip() for kw in response.text.split('，')]
                return keywords
            
            return []
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def batch_summarize(
        self, 
        papers: list,
        max_length: int = 200
    ) -> list:
        """
        批量总结多篇论文
        
        Args:
            papers: 论文列表，每个元素应该包含title和summary字段
            max_length: 每个总结的最大字符数
            
        Returns:
            总结列表
        """
        summaries = []
        
        for paper in papers:
            summary = self.summarize_paper(
                paper.get('title', ''),
                paper.get('summary', ''),
                max_length
            )
            summaries.append({
                'arxiv_id': paper.get('arxiv_id', ''),
                'summary': summary
            })
        
        return summaries
