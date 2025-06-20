from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from routers.url_router import router as url_router
from exceptions.url_exceptions import URLShortenerException


# 创建FastAPI应用实例
app = FastAPI(
    title="URL短链接生成器",
    description="基于FastAPI的URL短链接生成微服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(url_router, tags=["URL短链接"])


# 全局异常处理器
@app.exception_handler(URLShortenerException)
async def url_shortener_exception_handler(request: Request, exc: URLShortenerException):
    """处理自定义URL短链接异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理一般异常"""
    return JSONResponse(
        status_code=500,
        content={"error": "内部服务器错误", "detail": str(exc), "status_code": 500}
    )


# 根路径
@app.get("/", summary="欢迎页面")
async def root():
    """
    服务欢迎页面
    """
    return {
        "message": "欢迎使用URL短链接生成器",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 