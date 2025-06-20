from datetime import datetime
from typing import List, Optional
from fastapi import Request

from models.url_models import URLCreate, URLResponse, URLStats, URLUpdate
from utils.url_utils import generate_short_id, validate_url, is_url_expired, is_valid_alias, sanitize_url
from utils.storage import url_storage
from exceptions.url_exceptions import (
    URLNotFoundError, 
    URLExpiredError, 
    InvalidURLError, 
    DuplicateAliasError, 
    URLInactiveError
)


class URLService:
    """URL短链接服务层"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.storage = url_storage
    
    async def create_short_url(self, url_data: URLCreate, request: Request = None) -> URLResponse:
        """创建短链接"""
        # 验证原始URL
        original_url = str(url_data.original_url)
        if not validate_url(original_url):
            raise InvalidURLError(original_url)
        
        # 清理URL
        original_url = sanitize_url(original_url)
        
        # 生成或验证自定义别名
        if url_data.custom_alias:
            if not is_valid_alias(url_data.custom_alias):
                raise InvalidURLError(f"无效的别名格式: {url_data.custom_alias}")
            
            if await self.storage.alias_exists(url_data.custom_alias):
                raise DuplicateAliasError(url_data.custom_alias)
            
            short_id = url_data.custom_alias
        else:
            # 生成唯一的短ID
            while True:
                short_id = generate_short_id()
                if not await self.storage.get_url(short_id):
                    break
        
        # 构建短链接URL
        if request:
            base_url = str(request.base_url).rstrip('/')
        else:
            base_url = self.base_url
        
        short_url = f"{base_url}/{short_id}"
        
        # 创建URL数据
        url_dict = {
            "id": short_id,
            "original_url": original_url,
            "short_url": short_url,
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": url_data.expires_at.isoformat() if url_data.expires_at else None,
            "is_active": True,
            "last_accessed": None
        }
        
        if url_data.custom_alias:
            url_dict["custom_alias"] = url_data.custom_alias
        
        return await self.storage.create_url(url_dict)
    
    async def get_original_url(self, short_id: str) -> str:
        """根据短ID获取原始URL"""
        url_data = await self.storage.get_url(short_id)
        if not url_data:
            raise URLNotFoundError(short_id)
        
        # 检查是否过期
        if url_data.expires_at and is_url_expired(url_data.expires_at):
            raise URLExpiredError(short_id)
        
        # 检查是否激活
        if not url_data.is_active:
            raise URLInactiveError(short_id)
        
        # 增加点击次数
        await self.storage.increment_click_count(short_id)
        
        return url_data.original_url
    
    async def get_url_stats(self, short_id: str) -> URLStats:
        """获取URL统计信息"""
        url_data = await self.storage.get_url(short_id)
        if not url_data:
            raise URLNotFoundError(short_id)
        
        # 转换为URLStats模型
        stats_data = {
            "id": url_data.id,
            "original_url": url_data.original_url,
            "short_url": url_data.short_url,
            "click_count": url_data.click_count,
            "created_at": url_data.created_at,
            "expires_at": url_data.expires_at,
            "is_active": url_data.is_active,
            "last_accessed": None
        }
        
        # 获取详细统计信息
        detailed_stats = await self.storage.get_stats(short_id)
        if detailed_stats and "last_accessed" in detailed_stats:
            if detailed_stats["last_accessed"]:
                stats_data["last_accessed"] = datetime.fromisoformat(detailed_stats["last_accessed"])
        
        return URLStats(**stats_data)
    
    async def update_url(self, short_id: str, update_data: URLUpdate) -> URLResponse:
        """更新短链接"""
        url_data = await self.storage.get_url(short_id)
        if not url_data:
            raise URLNotFoundError(short_id)
        
        update_dict = {}
        if update_data.original_url is not None:
            original_url = str(update_data.original_url)
            if not validate_url(original_url):
                raise InvalidURLError(original_url)
            update_dict["original_url"] = sanitize_url(original_url)
        
        if update_data.expires_at is not None:
            update_dict["expires_at"] = update_data.expires_at.isoformat()
        
        if update_data.is_active is not None:
            update_dict["is_active"] = update_data.is_active
        
        if not update_dict:
            return url_data
        
        return await self.storage.update_url(short_id, update_dict)
    
    async def delete_url(self, short_id: str) -> bool:
        """删除短链接"""
        url_data = await self.storage.get_url(short_id)
        if not url_data:
            raise URLNotFoundError(short_id)
        
        return await self.storage.delete_url(short_id)
    
    async def get_all_urls(self) -> List[URLResponse]:
        """获取所有短链接"""
        return await self.storage.get_all_urls()
    
    async def get_url_info(self, short_id: str) -> URLResponse:
        """获取短链接信息（不增加点击次数）"""
        url_data = await self.storage.get_url(short_id)
        if not url_data:
            raise URLNotFoundError(short_id)
        
        return url_data 