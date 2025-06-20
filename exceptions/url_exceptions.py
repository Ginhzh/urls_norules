from fastapi import HTTPException
from typing import Optional


class URLShortenerException(HTTPException):
    """短链接服务基础异常"""
    def __init__(self, status_code: int, detail: str, headers: Optional[dict] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class URLNotFoundError(URLShortenerException):
    """URL未找到异常"""
    def __init__(self, url_id: str):
        super().__init__(
            status_code=404,
            detail=f"短链接 '{url_id}' 不存在"
        )


class URLExpiredError(URLShortenerException):
    """URL已过期异常"""
    def __init__(self, url_id: str):
        super().__init__(
            status_code=410,
            detail=f"短链接 '{url_id}' 已过期"
        )


class InvalidURLError(URLShortenerException):
    """无效URL异常"""
    def __init__(self, url: str):
        super().__init__(
            status_code=400,
            detail=f"无效的URL格式: '{url}'"
        )


class DuplicateAliasError(URLShortenerException):
    """重复别名异常"""
    def __init__(self, alias: str):
        super().__init__(
            status_code=409,
            detail=f"别名 '{alias}' 已存在"
        )


class URLInactiveError(URLShortenerException):
    """URL已停用异常"""
    def __init__(self, url_id: str):
        super().__init__(
            status_code=410,
            detail=f"短链接 '{url_id}' 已停用"
        ) 