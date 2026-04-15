"""宏观经济数据路由"""

from fastapi import APIRouter, Query

from app.models.schemas import APIResponse, MacroDateRangeRequest, ReserveRatioRequest, ReserveDateType
from app.routers._common import build, call
from app.services import macro_service

router = APIRouter(prefix="/macro", tags=["宏观经济"])


@router.get("/deposit_rate", summary="存款利率", response_model=APIResponse)
def deposit_rate(
    start_date: str = Query("", description="起始日期"),
    end_date: str = Query("", description="终止日期"),
):
    req = build(MacroDateRangeRequest, start_date=start_date, end_date=end_date)
    return call(macro_service.get_deposit_rate, req)


@router.get("/loan_rate", summary="贷款利率", response_model=APIResponse)
def loan_rate(
    start_date: str = Query("", description="起始日期"),
    end_date: str = Query("", description="终止日期"),
):
    req = build(MacroDateRangeRequest, start_date=start_date, end_date=end_date)
    return call(macro_service.get_loan_rate, req)


@router.get("/money_supply_month", summary="货币供应量（月）", response_model=APIResponse)
def money_supply_month(
    start_date: str = Query("", description="起始年月 yyyy-MM"),
    end_date: str = Query("", description="终止年月 yyyy-MM"),
):
    req = build(MacroDateRangeRequest, start_date=start_date, end_date=end_date)
    return call(macro_service.get_money_supply_month, req)


@router.get("/money_supply_year", summary="货币供应量（年）", response_model=APIResponse)
def money_supply_year(
    start_date: str = Query("", description="起始年份 yyyy"),
    end_date: str = Query("", description="终止年份 yyyy"),
):
    req = build(MacroDateRangeRequest, start_date=start_date, end_date=end_date)
    return call(macro_service.get_money_supply_year, req)


@router.get("/reserve_ratio", summary="存款准备金率", response_model=APIResponse)
def reserve_ratio(
    start_date: str = Query("", description="起始日期"),
    end_date: str = Query("", description="终止日期"),
    year_type: ReserveDateType = Query(ReserveDateType.ANNOUNCE, description="日期类型: 0公告日期 1生效日期"),
):
    req = build(ReserveRatioRequest, start_date=start_date, end_date=end_date, year_type=year_type)
    return call(macro_service.get_required_reserve_ratio, req)
