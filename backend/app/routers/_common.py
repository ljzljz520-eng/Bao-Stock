"""路由公共工具"""

import logging

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.exceptions import BaostockError, BaostockHTTPException
from app.models.schemas import APIResponse

logger = logging.getLogger(__name__)


def ok(data: list[dict], total: int | None = None) -> APIResponse:
    return APIResponse(data=data, total=len(data) if total is None else total)


def call(fn, req):
    """统一调用 service 函数，捕获 BaostockError"""
    try:
        result = fn(req)
        logger.info("%s -> %d records", fn.__name__, len(result))
        if getattr(req, "page", None) is not None and getattr(req, "page_size", None) is not None:
            return ok(result, total=len(result))
        return ok(result)
    except BaostockError as e:
        logger.error("%s failed: [%s] %s", fn.__name__, e.error_code, e.error_msg)
        raise BaostockHTTPException(e.error_code, e.error_msg)


def build(model_cls, **kwargs):
    """构造 Pydantic 模型，校验失败返回 422"""
    try:
        return model_cls(**kwargs)
    except ValidationError as e:
        logger.warning("参数校验失败: %s", e.error_count())
        raise RequestValidationError(errors=e.errors())
