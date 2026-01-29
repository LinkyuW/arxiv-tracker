"""
Flask 主应用程序
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

from config import config
from services.arxiv_service import ArxivService
from services.ai_service import AIService
from services.cache_service import CacheService

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)

# 加载配置
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))

# 启用CORS (允许所有来源，生产环境建议限制)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 初始化服务
arxiv_service = ArxivService(
    max_results=app.config.get('ARXIV_MAX_RESULTS', 100),
    timeout=app.config.get('REQUEST_TIMEOUT', 30)
)

cache_service = CacheService(
    expiry_days=app.config.get('CACHE_EXPIRY_DAYS', 30)
)

# AI服务（如果提供了API密钥）
ai_service = None
if app.config.get('GEMINI_API_KEY'):
    try:
        ai_service = AIService(
            api_key=app.config['GEMINI_API_KEY'],
            model=app.config.get('AI_MODEL', 'gemini-pro')
        )
    except Exception as e:
        print(f"Warning: Could not initialize AI service: {e}")


# ==================== 路由 ====================

@app.route('/', methods=['GET'])
def index():
    """API首页"""
    return jsonify({
        'status': 'success',
        'message': 'arXiv Paper Tracker API',
        'version': '1.0.0',
        'endpoints': {
            'search': '/api/search',
            'paper': '/api/paper/<arxiv_id>',
            'summarize': '/api/summarize',
            'cache_stats': '/api/cache/stats'
        }
    })


@app.route('/api/search', methods=['GET'])
def search_papers():
    """
    搜索论文
    
    查询参数:
        - query: 搜索关键词 (必需)
        - days_back: 搜索多少天内的论文 (可选，默认1825天=5年)
        - max_results: 返回结果数量 (可选，默认100)
    """
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify({
            'status': 'error',
            'message': '搜索关键词不能为空'
        }), 400
    
    days_back = request.args.get('days_back', type=int, default=365*5)
    max_results = request.args.get('max_results', type=int, default=100)
    
    # 检查缓存
    cache_key = f'search:{query}:{days_back}'
    cached_result = cache_service.get(cache_key)
    
    if cached_result:
        return jsonify({
            'status': 'success',
            'message': '从缓存中获取',
            'data': cached_result,
            'from_cache': True
        })
    
    # 从arXiv获取数据
    papers = arxiv_service.search_papers(query, days_back, max_results)
    
    if papers:
        # 缓存结果
        cache_service.set(cache_key, papers)
    
    return jsonify({
        'status': 'success',
        'message': f'找到 {len(papers)} 篇论文',
        'data': papers,
        'from_cache': False
    })


@app.route('/api/paper/<arxiv_id>', methods=['GET'])
def get_paper(arxiv_id):
    """
    获取单篇论文信息
    
    Args:
        arxiv_id: arXiv论文ID (例如: 2301.12345)
    """
    paper = arxiv_service.get_paper_by_id(arxiv_id)
    
    if not paper:
        return jsonify({
            'status': 'error',
            'message': f'未找到论文: {arxiv_id}'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': paper
    })


@app.route('/api/summarize', methods=['POST'])
def summarize_papers():
    """
    对论文进行AI总结
    
    请求体:
        {
            "papers": [
                {"title": "...", "summary": "..."},
                ...
            ]
        }
    """
    if not ai_service:
        return jsonify({
            'status': 'error',
            'message': 'AI服务未配置'
        }), 503
    
    data = request.get_json()
    
    if not data or 'papers' not in data:
        return jsonify({
            'status': 'error',
            'message': '请提供papers列表'
        }), 400
    
    papers = data['papers']
    max_length = data.get('max_length', 200)
    
    summaries = ai_service.batch_summarize(papers, max_length)
    
    return jsonify({
        'status': 'success',
        'message': f'成功总结 {len(summaries)} 篇论文',
        'data': summaries
    })


@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """获取缓存统计信息"""
    stats = cache_service.get_cache_stats()
    
    return jsonify({
        'status': 'success',
        'data': stats
    })


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清空所有缓存"""
    result = cache_service.clear()
    
    if result:
        return jsonify({
            'status': 'success',
            'message': '缓存已清空'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '清空缓存失败'
        }), 500


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': '端点不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', True)
    )
