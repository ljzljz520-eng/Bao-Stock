"""请求/响应 Pydantic 模型"""

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ── 枚举定义 ─────────────────────────────────────────────

class Frequency(str, Enum):
    """K线数据频率"""
    DAILY = "d"
    WEEKLY = "w"
    MONTHLY = "m"
    MIN5 = "5"
    MIN15 = "15"
    MIN30 = "30"
    MIN60 = "60"


class AdjustFlag(str, Enum):
    """复权类型"""
    FORWARD = "2"    # 前复权
    BACKWARD = "1"   # 后复权
    NONE = "3"       # 不复权


class YearType(str, Enum):
    """分红年份类别"""
    REPORT = "report"    # 预案公告年份
    OPERATE = "operate"  # 除权除息年份


class ReserveDateType(str, Enum):
    """准备金率日期类型"""
    ANNOUNCE = "0"   # 公告日期
    EFFECTIVE = "1"  # 生效日期


# ── 日期校验器 ───────────────────────────────────────────

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_YEAR_MONTH_PATTERN = re.compile(r"^\d{4}-\d{2}$")
_YEAR_PATTERN = re.compile(r"^\d{4}$")


def _validate_date(v: str | None, field_name: str) -> str | None:
    if v is not None and v != "" and not _DATE_PATTERN.match(v):
        raise ValueError(f"{field_name} 格式必须为 YYYY-MM-DD，收到: {v}")
    return v


def _validate_year_month(v: str | None, field_name: str) -> str | None:
    if v is not None and v != "" and not _YEAR_MONTH_PATTERN.match(v):
        raise ValueError(f"{field_name} 格式必须为 YYYY-MM，收到: {v}")
    return v


def _validate_year(v: str | None, field_name: str) -> str | None:
    if v is not None and v != "" and not _YEAR_PATTERN.match(v):
        raise ValueError(f"{field_name} 格式必须为 YYYY，收到: {v}")
    return v


# ── 通用响应 ─────────────────────────────────────────────

class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0


# ── 股票行情请求 ─────────────────────────────────────────

class HistoryKDataRequest(BaseModel):
    code: str = Field(..., description="证券代码，如 sh.600000")
    fields: str = Field(
        default="date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
        description="查询字段，逗号分隔",
    )
    start_date: str | None = Field(None, description="起始日期 YYYY-MM-DD")
    end_date: str | None = Field(None, description="终止日期 YYYY-MM-DD")
    frequency: Frequency = Field(Frequency.DAILY, description="数据频率: d/w/m/5/15/30/60")
    adjustflag: AdjustFlag = Field(AdjustFlag.NONE, description="复权类型: 1后复权 2前复权 3不复权")

    @field_validator("start_date", "end_date")
    @classmethod
    def check_date(cls, v):
        return _validate_date(v, "日期")


class TradeDatesRequest(BaseModel):
    start_date: str | None = Field(None, description="起始日期 YYYY-MM-DD")
    end_date: str | None = Field(None, description="终止日期 YYYY-MM-DD")

    @field_validator("start_date", "end_date")
    @classmethod
    def check_date(cls, v):
        return _validate_date(v, "日期")


class AllStockRequest(BaseModel):
    day: str | None = Field(None, description="查询日期 YYYY-MM-DD")
    page: int | None = Field(None, ge=1, description="分页页码，从 1 开始")
    page_size: int | None = Field(None, ge=1, le=500, description="分页大小")

    @field_validator("day")
    @classmethod
    def check_date(cls, v):
        return _validate_date(v, "day")


class StockBasicRequest(BaseModel):
    code: str = Field("", description="证券代码")
    code_name: str = Field("", description="证券名称，支持模糊查询")


class StockIndustryRequest(BaseModel):
    code: str = Field("", description="股票代码")
    date: str = Field("", description="查询日期 YYYY-MM-DD")

    @field_validator("date")
    @classmethod
    def check_date(cls, v):
        return _validate_date(v, "date")


class IndexStocksRequest(BaseModel):
    date: str = Field("", description="查询日期 YYYY-MM-DD")

    @field_validator("date")
    @classmethod
    def check_date(cls, v):
        return _validate_date(v, "date")


# ── 分红 / 复权 ─────────────────────────────────────────

class DividendDataRequest(BaseModel):
    code: str = Field(..., description="证券代码")
    year: str | None = Field(None, description="年份 YYYY")
    year_type: YearType = Field(YearType.REPORT, description="年份类别: report/operate")

    @field_validator("year")
    @classmethod
    def check_year(cls, v):
        return _validate_year(v, "year")


class AdjustFactorRequest(BaseModel):
    code: str = Field(..., description="证券代码")
    start_date: str | None = Field(None, description="起始日期")
    end_date: str | None = Field(None, description="终止日期")

    @field_validator("start_date", "end_date")
    @classmethod
    def check_date(cls, v):
        return _validate_date(v, "日期")


# ── 财务数据请求 ─────────────────────────────────────────

class FinanceDataRequest(BaseModel):
    code: str = Field(..., description="证券代码")
    year: int | None = Field(None, ge=1990, le=2100, description="统计年份")
    quarter: int | None = Field(None, ge=1, le=4, description="统计季度 1-4")


class ReportRequest(BaseModel):
    code: str = Field(..., description="证券代码")
    start_date: str | None = Field(None, description="起始日期")
    end_date: str | None = Field(None, description="终止日期")

    @field_validator("start_date", "end_date")
    @classmethod
    def check_date(cls, v):
        return _validate_date(v, "日期")


# ── 宏观经济请求 ─────────────────────────────────────────

class MacroDateRangeRequest(BaseModel):
    start_date: str = Field("", description="起始日期")
    end_date: str = Field("", description="终止日期")

    @field_validator("start_date", "end_date")
    @classmethod
    def check_date(cls, v):
        # 宏观接口日期格式较灵活，允许 YYYY-MM-DD / YYYY-MM / YYYY / 空
        if v and not (_DATE_PATTERN.match(v) or _YEAR_MONTH_PATTERN.match(v) or _YEAR_PATTERN.match(v)):
            raise ValueError(f"日期格式必须为 YYYY-MM-DD / YYYY-MM / YYYY，收到: {v}")
        return v


class ReserveRatioRequest(BaseModel):
    start_date: str = Field("", description="起始日期")
    end_date: str = Field("", description="终止日期")
    year_type: ReserveDateType = Field(ReserveDateType.ANNOUNCE, description="日期类型: 0公告日期 1生效日期")

    @field_validator("start_date", "end_date")
    @classmethod
    def check_date(cls, v):
        if v and not (_DATE_PATTERN.match(v) or _YEAR_MONTH_PATTERN.match(v) or _YEAR_PATTERN.match(v)):
            raise ValueError(f"日期格式必须为 YYYY-MM-DD / YYYY-MM / YYYY，收到: {v}")
        return v
