"""应用配置"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Baostock API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api/v1"

    # baostock 默认参数
    default_start_date: str = "2020-01-01"

    model_config = {"env_prefix": "BAOSTOCK_"}


settings = Settings()
