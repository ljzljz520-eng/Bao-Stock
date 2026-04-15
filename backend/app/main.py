"""FastAPI 应用入口"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.config import settings
from app.core.baostock_client import client
from app.core.exceptions import BaostockError
from app.routers import finance, macro, stock

# ── 统一日志配置 ─────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("baostock_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时登录 baostock，关闭时登出"""
    logger.info("Logging in to baostock...")
    client.login()
    logger.info("Baostock login success.")
    yield
    logger.info("Logging out from baostock...")
    client.logout()
    logger.info("Baostock logout done.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Baostock 股票数据查询 API — 历史K线、财务报表、宏观经济数据",
    lifespan=lifespan,
    docs_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    """使用本地 swagger-ui 静态资源，无需外网 CDN"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title,
        swagger_css_url="/static/swagger-ui.css",
        swagger_js_url="/static/swagger-ui-bundle.js",
    )


# ── 请求/响应日志中间件 ──────────────────────────────────

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info("-> %s %s", request.method, request.url.path)
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    logger.info("<- %s %s %d %.1fms", request.method, request.url.path, response.status_code, elapsed)
    return response


# ── 异常处理 ─────────────────────────────────────────────

@app.exception_handler(BaostockError)
async def baostock_error_handler(request: Request, exc: BaostockError):
    logger.error("BaostockError on %s: [%s] %s", request.url.path, exc.error_code, exc.error_msg)
    return JSONResponse(
        status_code=500,
        content={
            "code": -1,
            "message": exc.error_msg,
            "error_code": exc.error_code,
            "data": [],
            "total": 0,
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    logger.warning("RequestValidationError on %s: %s", request.url.path, len(exc.errors()))
    first_error = exc.errors()[0] if exc.errors() else {"msg": "参数校验失败"}
    return JSONResponse(
        status_code=422,
        content={
            "code": -1,
            "message": "参数校验失败",
            "detail": first_error.get("msg", "参数校验失败"),
            "data": [],
            "total": 0,
        },
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    logger.warning("ValidationError on %s: %s", request.url.path, exc.error_count())
    return JSONResponse(
        status_code=422,
        content={
            "code": -1,
            "message": "参数校验失败",
            "detail": exc.errors(),
        },
    )


# ── 注册路由 ─────────────────────────────────────────────

app.include_router(stock.router, prefix=settings.api_prefix)
app.include_router(finance.router, prefix=settings.api_prefix)
app.include_router(macro.router, prefix=settings.api_prefix)


@app.get("/health", tags=["系统"])
def health():
    return {"status": "ok", "version": settings.app_version}
