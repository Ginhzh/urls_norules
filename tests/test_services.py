import pytest
from datetime import datetime, timedelta

from models.url_models import URLCreate, URLUpdate
from services.url_service import URLService
from exceptions.url_exceptions import (
    URLNotFoundError,
    URLExpiredError,
    InvalidURLError,
    DuplicateAliasError,
    URLInactiveError
)


class TestURLService:
    """URL服务测试"""
    
    @pytest.mark.asyncio
    async def test_create_short_url_basic(self, url_service):
        """测试创建基本短链接"""
        url_data = URLCreate(original_url="https://www.example.com")
        
        result = await url_service.create_short_url(url_data)
        
        assert result.original_url == "https://www.example.com"
        assert len(result.id) == 8
        assert result.click_count == 0
        assert result.is_active is True
        assert result.short_url.endswith(result.id)
    
    @pytest.mark.asyncio
    async def test_create_short_url_with_alias(self, url_service):
        """测试创建带自定义别名的短链接"""
        url_data = URLCreate(
            original_url="https://www.google.com",
            custom_alias="google"
        )
        
        result = await url_service.create_short_url(url_data)
        
        assert result.id == "google"
        assert result.original_url == "https://www.google.com"
        assert result.short_url.endswith("google")
    
    @pytest.mark.asyncio
    async def test_create_short_url_with_expiry(self, url_service):
        """测试创建带过期时间的短链接"""
        expires_at = datetime.utcnow() + timedelta(days=1)
        url_data = URLCreate(
            original_url="https://www.example.com",
            expires_at=expires_at
        )
        
        result = await url_service.create_short_url(url_data)
        
        assert result.expires_at == expires_at
    
    @pytest.mark.asyncio
    async def test_create_short_url_invalid_url(self, url_service):
        """测试创建无效URL的短链接"""
        # 使用pydantic验证错误，因为URLCreate会在创建时就验证
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            url_data = URLCreate(original_url="not-a-valid-url")
    
    @pytest.mark.asyncio
    async def test_create_short_url_duplicate_alias(self, url_service):
        """测试创建重复别名的短链接"""
        # 先创建一个带别名的短链接
        url_data_1 = URLCreate(
            original_url="https://www.example1.com",
            custom_alias="test"
        )
        await url_service.create_short_url(url_data_1)
        
        # 尝试创建相同别名的短链接
        with pytest.raises(DuplicateAliasError):
            url_data_2 = URLCreate(
                original_url="https://www.example2.com",
                custom_alias="test"
            )
            await url_service.create_short_url(url_data_2)
    
    @pytest.mark.asyncio
    async def test_create_short_url_invalid_alias(self, url_service):
        """测试创建无效别名的短链接"""
        with pytest.raises(InvalidURLError):
            url_data = URLCreate(
                original_url="https://www.example.com",
                custom_alias="invalid alias!"  # 包含空格和特殊字符
            )
            await url_service.create_short_url(url_data)
    
    @pytest.mark.asyncio
    async def test_get_original_url_success(self, url_service):
        """测试成功获取原始URL"""
        url_data = URLCreate(original_url="https://www.example.com")
        created_url = await url_service.create_short_url(url_data)
        
        original_url = await url_service.get_original_url(created_url.id)
        
        assert original_url == "https://www.example.com"
    
    @pytest.mark.asyncio
    async def test_get_original_url_not_found(self, url_service):
        """测试获取不存在的URL"""
        with pytest.raises(URLNotFoundError):
            await url_service.get_original_url("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_original_url_expired(self, url_service):
        """测试获取已过期的URL"""
        expired_time = datetime.utcnow() - timedelta(hours=1)
        url_data = URLCreate(
            original_url="https://www.example.com",
            expires_at=expired_time
        )
        created_url = await url_service.create_short_url(url_data)
        
        with pytest.raises(URLExpiredError):
            await url_service.get_original_url(created_url.id)
    
    @pytest.mark.asyncio
    async def test_get_original_url_inactive(self, url_service):
        """测试获取已停用的URL"""
        url_data = URLCreate(original_url="https://www.example.com")
        created_url = await url_service.create_short_url(url_data)
        
        # 停用URL
        update_data = URLUpdate(is_active=False)
        await url_service.update_url(created_url.id, update_data)
        
        with pytest.raises(URLInactiveError):
            await url_service.get_original_url(created_url.id)
    
    @pytest.mark.asyncio
    async def test_get_url_stats(self, url_service):
        """测试获取URL统计信息"""
        url_data = URLCreate(original_url="https://www.example.com")
        created_url = await url_service.create_short_url(url_data)
        
        # 访问几次URL以增加点击次数
        await url_service.get_original_url(created_url.id)
        await url_service.get_original_url(created_url.id)
        
        stats = await url_service.get_url_stats(created_url.id)
        
        assert stats.id == created_url.id
        assert stats.click_count == 2
        assert stats.last_accessed is not None
    
    @pytest.mark.asyncio
    async def test_update_url_success(self, url_service):
        """测试成功更新URL"""
        url_data = URLCreate(original_url="https://www.example.com")
        created_url = await url_service.create_short_url(url_data)
        
        update_data = URLUpdate(
            original_url="https://www.updated.com",
            is_active=False
        )
        updated_url = await url_service.update_url(created_url.id, update_data)
        
        assert updated_url.original_url == "https://www.updated.com"
        assert updated_url.is_active is False
    
    @pytest.mark.asyncio
    async def test_update_url_not_found(self, url_service):
        """测试更新不存在的URL"""
        with pytest.raises(URLNotFoundError):
            update_data = URLUpdate(is_active=False)
            await url_service.update_url("nonexistent", update_data)
    
    @pytest.mark.asyncio
    async def test_update_url_invalid_url(self, url_service):
        """测试更新为无效URL"""
        url_data = URLCreate(original_url="https://www.example.com")
        created_url = await url_service.create_short_url(url_data)
        
        # 使用pydantic验证错误，因为URLUpdate会在创建时就验证
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            update_data = URLUpdate(original_url="invalid-url")
    
    @pytest.mark.asyncio
    async def test_delete_url_success(self, url_service):
        """测试成功删除URL"""
        url_data = URLCreate(original_url="https://www.example.com")
        created_url = await url_service.create_short_url(url_data)
        
        success = await url_service.delete_url(created_url.id)
        
        assert success is True
        
        # 验证URL已被删除
        with pytest.raises(URLNotFoundError):
            await url_service.get_url_info(created_url.id)
    
    @pytest.mark.asyncio
    async def test_delete_url_not_found(self, url_service):
        """测试删除不存在的URL"""
        with pytest.raises(URLNotFoundError):
            await url_service.delete_url("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_all_urls(self, url_service):
        """测试获取所有URL"""
        url_data_1 = URLCreate(original_url="https://www.example1.com")
        url_data_2 = URLCreate(original_url="https://www.example2.com")
        
        await url_service.create_short_url(url_data_1)
        await url_service.create_short_url(url_data_2)
        
        all_urls = await url_service.get_all_urls()
        
        assert len(all_urls) >= 2
        assert all(hasattr(url, 'original_url') for url in all_urls)
    
    @pytest.mark.asyncio
    async def test_get_url_info(self, url_service):
        """测试获取URL信息（不增加点击次数）"""
        url_data = URLCreate(original_url="https://www.example.com")
        created_url = await url_service.create_short_url(url_data)
        
        # 获取信息前后点击次数应该保持不变
        info_before = await url_service.get_url_info(created_url.id)
        initial_count = info_before.click_count
        
        info_after = await url_service.get_url_info(created_url.id)
        
        assert info_after.click_count == initial_count
        assert info_after.id == created_url.id 