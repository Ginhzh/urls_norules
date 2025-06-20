from typing import List
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse

from models.url_models import URLCreate, URLResponse, URLStats, URLUpdate
from services.url_service import URLService


router = APIRouter()


def get_url_service() -> URLService:
    """依赖注入：获取URL服务实例"""
    return URLService()


@router.post("/shorten", response_model=URLResponse, summary="创建短链接")
async def create_short_url(
    url_data: URLCreate,
    request: Request,
    service: URLService = Depends(get_url_service)
):
    """
    创建短链接
    
    - **original_url**: 要缩短的原始URL
    - **custom_alias**: 可选的自定义别名
    - **expires_at**: 可选的过期时间
    """
    return await service.create_short_url(url_data, request)


@router.get("/{short_id}", summary="重定向到原始URL")
async def redirect_to_original(
    short_id: str,
    service: URLService = Depends(get_url_service)
):
    """
    根据短链接ID重定向到原始URL
    
    - **short_id**: 短链接ID或自定义别名
    """
    original_url = await service.get_original_url(short_id)
    return RedirectResponse(url=original_url, status_code=302)


@router.get("/api/urls", response_model=List[URLResponse], summary="获取所有短链接")
async def get_all_urls(
    service: URLService = Depends(get_url_service)
):
    """
    获取所有短链接列表
    """
    return await service.get_all_urls()


@router.get("/api/urls/{short_id}", response_model=URLResponse, summary="获取短链接信息")
async def get_url_info(
    short_id: str,
    service: URLService = Depends(get_url_service)
):
    """
    获取短链接详细信息（不增加点击次数）
    
    - **short_id**: 短链接ID或自定义别名
    """
    return await service.get_url_info(short_id)


@router.get("/api/urls/{short_id}/stats", response_model=URLStats, summary="获取短链接统计")
async def get_url_stats(
    short_id: str,
    service: URLService = Depends(get_url_service)
):
    """
    获取短链接统计信息
    
    - **short_id**: 短链接ID或自定义别名
    """
    return await service.get_url_stats(short_id)


@router.put("/api/urls/{short_id}", response_model=URLResponse, summary="更新短链接")
async def update_url(
    short_id: str,
    update_data: URLUpdate,
    service: URLService = Depends(get_url_service)
):
    """
    更新短链接信息
    
    - **short_id**: 短链接ID或自定义别名
    - **update_data**: 更新数据
    """
    return await service.update_url(short_id, update_data)


@router.delete("/api/urls/{short_id}", summary="删除短链接")
async def delete_url(
    short_id: str,
    service: URLService = Depends(get_url_service)
):
    """
    删除短链接
    
    - **short_id**: 短链接ID或自定义别名
    """
    success = await service.delete_url(short_id)
    return {"message": "短链接删除成功" if success else "删除失败"}


@router.get("/api/health", summary="健康检查")
async def health_check():
    """
    服务健康检查
    """
    return {"status": "healthy", "service": "URL Shortener"} 