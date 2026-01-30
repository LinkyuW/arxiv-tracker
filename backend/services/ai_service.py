"""
AI 总结服务模块
支持多个AI供应商：Google Gemini 和 Free Qwen3 API
"""
import requests
from typing import Optional

class AIService:
    """AI论文总结服务 - 支持多个AI供应商"""
    
    def __init__(self, api_key: str, model: str = 'gemini-pro', provider: str = 'gemini', api_endpoint: str = None):
        """
        初始化AI服务
        
        Args:
            api_key: API密钥
            model: 使用的模型名称
            provider: AI供应商 ('gemini' 或 'qwen3')
            api_endpoint: API端点（仅供Qwen3使用）
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider.lower()
        self.api_endpoint = api_endpoint or 'https://api.suanli.cn/v1'
        self.client = None
        
        if self.provider == 'gemini':
            # 配置Google Gemini
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(model)
                print(f"[INFO] Initialized Gemini AI service with model: {model}")
            except ImportError:
                print("[WARNING] google-generativeai not installed. Gemini service unavailable.")
                self.client = None
            except Exception as e:
                print(f"[ERROR] Failed to initialize Gemini service: {e}")
                self.client = None
        elif self.provider == 'qwen3':
            # 配置Qwen3 API客户端
            self.client = requests.Session()
            self.client.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
            print(f"[INFO] Initialized Qwen3 AI service with model: {model}")
        else:
            print(f"[WARNING] Unknown AI provider: {provider}")
    
    def _call_qwen3(self, prompt: str) -> Optional[str]:
        """
        调用Qwen3 API
        
        Args:
            prompt: 提示词
            
        Returns:
            API响应文本
        """
        try:
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            response = self.client.post(
                f'{self.api_endpoint}/chat/completions',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # 提取响应文本
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0].get('message', {}).get('content', '')
                    return content.strip() if content else None
            else:
                print(f"[ERROR] Qwen3 API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("[ERROR] Qwen3 API request timeout")
            return None
        except Exception as e:
            print(f"[ERROR] Qwen3 API call failed: {e}")
            return None
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """
        调用Gemini API
        
        Args:
            prompt: 提示词
            
        Returns:
            API响应文本
        """
        try:
            if not self.client:
                return None
            
            response = self.client.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            
            return None
            
        except Exception as e:
            print(f"[ERROR] Gemini API call failed: {e}")
            return None
    
    def _generate_content(self, prompt: str) -> Optional[str]:
        """
        通过相应的AI供应商生成内容
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的内容
        """
        if self.provider == 'qwen3':
            return self._call_qwen3(prompt)
        elif self.provider == 'gemini':
            return self._call_gemini(prompt)
        else:
            print(f"[ERROR] Unknown provider: {self.provider}")
            return None
    
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
        
        return self._generate_content(prompt)
    
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
        
        response = self._generate_content(prompt)
        
        if response:
            keywords = [kw.strip() for kw in response.split('，')]
            return keywords
        
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
