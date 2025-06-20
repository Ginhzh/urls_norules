import pytest
from datetime import datetime

from utils.storage import URLStorage
from models.url_models import URLResponse


class TestURLStorage:
    """URL存储测试"""
    
    @pytest.mark.asyncio
    async def test_create_url(self, url_storage):
        """测试创建URL"""
        url_data = {
            "id": "test123",
            "original_url": "https://www.example.com",
            "short_url": "http://localhost:8000/test123",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None
        }
        
        result = await url_storage.create_url(url_data)
        
        assert isinstance(result, URLResponse)
        assert result.id == "test123"
        assert result.original_url == "https://www.example.com"
        assert result.click_count == 0
    
    @pytest.mark.asyncio
    async def test_create_url_with_alias(self, url_storage):
        """测试创建带别名的URL"""
        url_data = {
            "id": "test123",
            "original_url": "https://www.example.com",
            "short_url": "http://localhost:8000/test123",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None,
            "custom_alias": "myalias"
        }
        
        result = await url_storage.create_url(url_data)
        
        # 测试通过别名查找
        alias_result = await url_storage.get_url("myalias")
        assert alias_result is not None
        assert alias_result.id == "test123"
    
    @pytest.mark.asyncio
    async def test_get_url_existing(self, url_storage):
        """测试获取存在的URL"""
        url_data = {
            "id": "test123",
            "original_url": "https://www.example.com",
            "short_url": "http://localhost:8000/test123",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None
        }
        
        await url_storage.create_url(url_data)
        result = await url_storage.get_url("test123")
        
        assert result is not None
        assert result.id == "test123"
    
    @pytest.mark.asyncio
    async def test_get_url_non_existing(self, url_storage):
        """测试获取不存在的URL"""
        result = await url_storage.get_url("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_url(self, url_storage):
        """测试更新URL"""
        url_data = {
            "id": "test123",
            "original_url": "https://www.example.com",
            "short_url": "http://localhost:8000/test123",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None
        }
        
        await url_storage.create_url(url_data)
        
        update_data = {"is_active": False}
        result = await url_storage.update_url("test123", update_data)
        
        assert result is not None
        assert result.is_active is False
    
    @pytest.mark.asyncio
    async def test_update_url_non_existing(self, url_storage):
        """测试更新不存在的URL"""
        update_data = {"is_active": False}
        result = await url_storage.update_url("nonexistent", update_data)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_url(self, url_storage):
        """测试删除URL"""
        url_data = {
            "id": "test123",
            "original_url": "https://www.example.com",
            "short_url": "http://localhost:8000/test123",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None
        }
        
        await url_storage.create_url(url_data)
        
        success = await url_storage.delete_url("test123")
        assert success is True
        
        # 验证URL已被删除
        result = await url_storage.get_url("test123")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_url_non_existing(self, url_storage):
        """测试删除不存在的URL"""
        success = await url_storage.delete_url("nonexistent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_increment_click_count(self, url_storage):
        """测试增加点击次数"""
        url_data = {
            "id": "test123",
            "original_url": "https://www.example.com",
            "short_url": "http://localhost:8000/test123",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None
        }
        
        await url_storage.create_url(url_data)
        
        count = await url_storage.increment_click_count("test123")
        assert count == 1
        
        count = await url_storage.increment_click_count("test123")
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_increment_click_count_non_existing(self, url_storage):
        """测试增加不存在URL的点击次数"""
        count = await url_storage.increment_click_count("nonexistent")
        assert count is None
    
    @pytest.mark.asyncio
    async def test_get_all_urls(self, url_storage):
        """测试获取所有URL"""
        url_data_1 = {
            "id": "test1",
            "original_url": "https://www.example1.com",
            "short_url": "http://localhost:8000/test1",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None
        }
        
        url_data_2 = {
            "id": "test2",
            "original_url": "https://www.example2.com",
            "short_url": "http://localhost:8000/test2",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None
        }
        
        await url_storage.create_url(url_data_1)
        await url_storage.create_url(url_data_2)
        
        all_urls = await url_storage.get_all_urls()
        assert len(all_urls) == 2
        assert all(isinstance(url, URLResponse) for url in all_urls)
    
    @pytest.mark.asyncio
    async def test_alias_exists(self, url_storage):
        """测试别名是否存在"""
        url_data = {
            "id": "test123",
            "original_url": "https://www.example.com",
            "short_url": "http://localhost:8000/test123",
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "is_active": True,
            "last_accessed": None,
            "custom_alias": "myalias"
        }
        
        await url_storage.create_url(url_data)
        
        assert await url_storage.alias_exists("myalias") is True
        assert await url_storage.alias_exists("nonexistent") is False