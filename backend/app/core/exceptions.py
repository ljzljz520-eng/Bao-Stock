"""自定义异常"""

from fastapi import HTTPException


class BaostockError(Exception):
    """baostock 调用异常"""

    def __init__(self, error_code: str, error_msg: str):
        self.error_code = error_code
        self.error_msg = error_msg
        super().__init__(f"[{error_code}] {error_msg}")


class BaostockHTTPException(HTTPException):
    """baostock HTTP 异常"""

    def __init__(self, error_code: str, error_msg: str):
        super().__init__(
            status_code=500,
            detail={"error_code": error_code, "error_msg": error_msg},
        )
