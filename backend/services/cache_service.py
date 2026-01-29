"""
缓存服务模块
用于缓存论文数据，减少API调用
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

class CacheService:
    """论文数据缓存服务"""
    
    def __init__(self, cache_dir: str = './cache', expiry_days: int = 30):
        """
        初始化缓存服务
        
        Args:
            cache_dir: 缓存目录
            expiry_days: 缓存过期天数
        """
        self.cache_dir = cache_dir
        self.expiry_days = expiry_days
        self.expiry_seconds = expiry_days * 24 * 3600
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """获取缓存文件路径"""
        # 将key转换为安全的文件名
        safe_key = key.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_dir, f'{safe_key}.json')
    
    def get(self, key: str) -> Optional[Dict]:
        """
        从缓存获取数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存数据，如果不存在或已过期返回None
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            # 检查缓存文件是否过期
            file_time = os.path.getmtime(cache_path)
            current_time = datetime.now().timestamp()
            
            if current_time - file_time > self.expiry_seconds:
                # 缓存已过期，删除文件
                os.remove(cache_path)
                return None
            
            # 读取缓存数据
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            print(f"Error reading cache {key}: {e}")
            return None
    
    def set(self, key: str, data: Dict) -> bool:
        """
        将数据写入缓存
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            
        Returns:
            是否成功
        """
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error writing cache {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功
        """
        cache_path = self._get_cache_path(key)
        
        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return True
        except Exception as e:
            print(f"Error deleting cache {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            是否成功
        """
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """
        获取缓存统计信息
        
        Returns:
            包含缓存大小和文件数量的字典
        """
        try:
            total_size = 0
            file_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_count += 1
                    filepath = os.path.join(self.cache_dir, filename)
                    total_size += os.path.getsize(filepath)
            
            return {
                'file_count': file_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {'file_count': 0, 'total_size_mb': 0}
