import pytest
from datetime import datetime, timedelta

from utils.url_utils import (
    generate_short_id,
    validate_url,
    is_url_expired,
    is_valid_alias,
    sanitize_url,
    get_domain_from_url
)


class TestURLUtils:
    """URL工具函数测试"""
    
    def test_generate_short_id_default_length(self):
        """测试生成默认长度的短ID"""
        short_id = generate_short_id()
        assert len(short_id) == 8
        assert short_id.isalnum()
    
    def test_generate_short_id_custom_length(self):
        """测试生成自定义长度的短ID"""
        short_id = generate_short_id(12)
        assert len(short_id) == 12
        assert short_id.isalnum()
    
    def test_generate_short_id_uniqueness(self):
        """测试生成的短ID的唯一性"""
        ids = [generate_short_id() for _ in range(100)]
        assert len(set(ids)) == 100  # 所有ID都应该是唯一的
    
    def test_validate_url_valid_urls(self):
        """测试有效URL的验证"""
        valid_urls = [
            "https://www.example.com",
            "http://google.com",
            "https://github.com/user/repo",
            "http://localhost:8000",
            "https://api.example.com/v1/users"
        ]
        
        for url in valid_urls:
            assert validate_url(url) is True
    
    def test_validate_url_invalid_urls(self):
        """测试无效URL的验证"""
        invalid_urls = [
            "not-a-url",
            "example.com",  # 缺少协议
            "",
            "   ",
            "javascript:alert('xss')"
        ]
        
        for url in invalid_urls:
            assert validate_url(url) is False
    
    def test_is_url_expired_not_expired(self):
        """测试未过期的URL"""
        future_time = datetime.utcnow() + timedelta(hours=1)
        assert is_url_expired(future_time) is False
        assert is_url_expired(None) is False  # 永不过期
    
    def test_is_url_expired_expired(self):
        """测试已过期的URL"""
        past_time = datetime.utcnow() - timedelta(hours=1)
        assert is_url_expired(past_time) is True
    
    def test_is_valid_alias_valid(self):
        """测试有效的别名"""
        valid_aliases = [
            "google",
            "my-link",
            "user_123",
            "ABC123",
            "test-link-123"
        ]
        
        for alias in valid_aliases:
            assert is_valid_alias(alias) is True
    
    def test_is_valid_alias_invalid(self):
        """测试无效的别名"""
        invalid_aliases = [
            "",
            "hello world",  # 包含空格
            "test@link",   # 包含特殊字符
            "link.com",    # 包含点
            "中文别名",     # 包含非ASCII字符
            "link/123",    # 包含斜杠
        ]
        
        for alias in invalid_aliases:
            assert is_valid_alias(alias) is False
    
    def test_sanitize_url_add_https(self):
        """测试为URL添加https协议"""
        test_cases = [
            ("example.com", "https://example.com"),
            ("www.google.com", "https://www.google.com"),
            ("  github.com  ", "https://github.com"),
        ]
        
        for input_url, expected in test_cases:
            assert sanitize_url(input_url) == expected
    
    def test_sanitize_url_keep_existing_protocol(self):
        """测试保持现有协议"""
        test_cases = [
            ("http://example.com", "http://example.com"),
            ("https://www.google.com", "https://www.google.com"),
        ]
        
        for input_url, expected in test_cases:
            assert sanitize_url(input_url) == expected
    
    def test_get_domain_from_url(self):
        """测试从URL中提取域名"""
        test_cases = [
            ("https://www.example.com", "www.example.com"),
            ("http://google.com/search", "google.com"),
            ("https://api.github.com/users", "api.github.com"),
            ("invalid-url", ""),
        ]
        
        for url, expected_domain in test_cases:
            assert get_domain_from_url(url) == expected_domain 