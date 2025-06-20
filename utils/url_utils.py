import re
import string
import secrets
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse


def generate_short_id(length: int = 8) -> str:
    """生成短链接ID"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def validate_url(url: str) -> bool:
    """验证URL格式"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_url_expired(expires_at: Optional[datetime]) -> bool:
    """检查URL是否过期"""
    if expires_at is None:
        return False
    return datetime.utcnow() > expires_at


def is_valid_alias(alias: str) -> bool:
    """验证别名格式"""
    if not alias:
        return False
    
    # 只允许字母、数字、连字符和下划线
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, alias))


def sanitize_url(url: str) -> str:
    """清理和规范化URL"""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def get_domain_from_url(url: str) -> str:
    """从URL中提取域名"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "" 