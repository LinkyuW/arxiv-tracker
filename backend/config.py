import os
from datetime import datetime, timedelta

class Config:
    """项目配置"""
    
    # Flask配置
    DEBUG = os.getenv('DEBUG', True)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///./arxiv_papers.db'
    )
    
    # arXiv配置
    ARXIV_SEARCH_DAYS = 365 * 5  # 5年内的论文
    ARXIV_MAX_RESULTS = 100  # 单次查询最大论文数
    
    # AI配置
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'qwen3')  # 默认使用Qwen3
    AI_MODEL = os.getenv('AI_MODEL', 'free:QwQ-32B')
    
    # Qwen3 API配置
    QWEN3_API_KEY = os.getenv('QWEN3_API_KEY')
    QWEN3_API_ENDPOINT = os.getenv('QWEN3_API_ENDPOINT', 'https://api.suanli.cn/v1')
    
    # Google Gemini API配置（备用）
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # 缓存配置
    CACHE_ENABLED = True
    CACHE_EXPIRY_DAYS = 30  # 缓存过期时间
    
    # 请求超时
    REQUEST_TIMEOUT = 30

# 环境特定配置
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
