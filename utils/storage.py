import json
from datetime import datetime
from typing import Dict, Optional, List
from models.url_models import URLResponse


class URLStorage:
    """URL存储管理器 - 使用内存存储，实际项目中可替换为数据库"""
    
    def __init__(self):
        self._storage: Dict[str, dict] = {}
        self._alias_index: Dict[str, str] = {}  # 别名到ID的映射
    
    async def create_url(self, url_data: dict) -> URLResponse:
        """创建短链接"""
        url_id = url_data["id"]
        self._storage[url_id] = url_data
        
        # 如果有自定义别名，建立映射
        if "custom_alias" in url_data and url_data["custom_alias"]:
            self._alias_index[url_data["custom_alias"]] = url_id
        
        return URLResponse(**url_data)
    
    async def get_url(self, url_id: str) -> Optional[URLResponse]:
        """根据ID获取短链接"""
        # 首先检查是否是别名
        actual_id = self._alias_index.get(url_id, url_id)
        
        if actual_id in self._storage:
            return URLResponse(**self._storage[actual_id])
        return None
    
    async def update_url(self, url_id: str, update_data: dict) -> Optional[URLResponse]:
        """更新短链接"""
        actual_id = self._alias_index.get(url_id, url_id)
        
        if actual_id not in self._storage:
            return None
        
        # 更新数据
        self._storage[actual_id].update(update_data)
        return URLResponse(**self._storage[actual_id])
    
    async def delete_url(self, url_id: str) -> bool:
        """删除短链接"""
        actual_id = self._alias_index.get(url_id, url_id)
        
        if actual_id not in self._storage:
            return False
        
        # 删除别名映射
        url_data = self._storage[actual_id]
        if "custom_alias" in url_data and url_data["custom_alias"]:
            self._alias_index.pop(url_data["custom_alias"], None)
        
        # 删除URL数据
        del self._storage[actual_id]
        return True
    
    async def increment_click_count(self, url_id: str) -> Optional[int]:
        """增加点击次数"""
        actual_id = self._alias_index.get(url_id, url_id)
        
        if actual_id not in self._storage:
            return None
        
        self._storage[actual_id]["click_count"] += 1
        self._storage[actual_id]["last_accessed"] = datetime.utcnow().isoformat()
        return self._storage[actual_id]["click_count"]
    
    async def get_all_urls(self) -> List[URLResponse]:
        """获取所有短链接"""
        return [URLResponse(**data) for data in self._storage.values()]
    
    async def alias_exists(self, alias: str) -> bool:
        """检查别名是否存在"""
        return alias in self._alias_index
    
    async def get_stats(self, url_id: str) -> Optional[dict]:
        """获取统计信息"""
        actual_id = self._alias_index.get(url_id, url_id)
        
        if actual_id not in self._storage:
            return None
        
        return self._storage[actual_id].copy()


# 全局存储实例
url_storage = URLStorage() 