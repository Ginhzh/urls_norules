import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from main import app
from utils.storage import URLStorage
from services.url_service import URLService


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def url_storage():
    """创建新的存储实例用于测试"""
    return URLStorage()


@pytest.fixture
def url_service(url_storage):
    """创建URL服务实例用于测试"""
    service = URLService()
    service.storage = url_storage
    return service


@pytest.fixture
def sample_url_data():
    """示例URL数据"""
    return {
        "original_url": "https://www.example.com",
        "custom_alias": None,
        "expires_at": None
    }


@pytest.fixture
def sample_url_with_alias():
    """带自定义别名的示例URL数据"""
    return {
        "original_url": "https://www.google.com",
        "custom_alias": "google",
        "expires_at": None
    }


@pytest.fixture
def expired_url_data():
    """过期的URL数据"""
    return {
        "original_url": "https://www.expired.com",
        "custom_alias": None,
        "expires_at": datetime.utcnow() - timedelta(days=1)
    }


@pytest.fixture
def future_expired_url_data():
    """将来过期的URL数据"""
    return {
        "original_url": "https://www.future.com",
        "custom_alias": None,
        "expires_at": datetime.utcnow() + timedelta(days=1)
    } 