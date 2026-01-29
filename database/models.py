"""
数据库模型定义
使用SQLAlchemy定义数据库结构
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Paper(Base):
    """论文数据模型"""
    __tablename__ = 'papers'
    
    id = Column(Integer, primary_key=True)
    arxiv_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=True)  # JSON格式存储
    summary = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)  # AI生成的总结
    published = Column(DateTime, nullable=False)
    url = Column(String(200), nullable=True)
    pdf_url = Column(String(200), nullable=True)
    categories = Column(String(200), nullable=True)
    keywords = Column(Text, nullable=True)  # JSON格式存储
    search_query = Column(String(200), nullable=True, index=True)  # 用于追踪搜索源
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_bookmarked = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f'<Paper {self.arxiv_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'arxiv_id': self.arxiv_id,
            'title': self.title,
            'authors': self.authors,
            'summary': self.summary,
            'ai_summary': self.ai_summary,
            'published': self.published.isoformat() if self.published else None,
            'url': self.url,
            'pdf_url': self.pdf_url,
            'categories': self.categories,
            'keywords': self.keywords,
            'is_bookmarked': self.is_bookmarked,
            'notes': self.notes,
        }


class SearchHistory(Base):
    """搜索历史模型"""
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True)
    query = Column(String(200), nullable=False)
    result_count = Column(Integer, default=0)
    searched_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchHistory {self.query}>'


def init_db(database_url: str = 'sqlite:///./arxiv_papers.db'):
    """
    初始化数据库
    
    Args:
        database_url: 数据库连接字符串
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine)
