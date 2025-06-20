from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class URLCreate(BaseModel):
    """创建短链接的请求模型"""
    original_url: HttpUrl = Field(..., description="原始URL")
    custom_alias: Optional[str] = Field(None, min_length=3, max_length=20, description="自定义别名")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class URLResponse(BaseModel):
    """短链接响应模型"""
    id: str = Field(..., description="短链接ID")
    original_url: str = Field(..., description="原始URL")
    short_url: str = Field(..., description="短链接")
    click_count: int = Field(0, description="点击次数")
    created_at: datetime = Field(..., description="创建时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    is_active: bool = Field(True, description="是否激活")


class URLStats(BaseModel):
    """短链接统计模型"""
    id: str = Field(..., description="短链接ID")
    original_url: str = Field(..., description="原始URL")
    short_url: str = Field(..., description="短链接")
    click_count: int = Field(..., description="点击次数")
    created_at: datetime = Field(..., description="创建时间")
    last_accessed: Optional[datetime] = Field(None, description="最后访问时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    is_active: bool = Field(..., description="是否激活")


class URLUpdate(BaseModel):
    """更新短链接的请求模型"""
    original_url: Optional[HttpUrl] = Field(None, description="原始URL")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    is_active: Optional[bool] = Field(None, description="是否激活") 