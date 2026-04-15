"""财务数据路由"""

from fastapi import APIRouter, Query

from app.models.schemas import APIResponse, FinanceDataRequest, ReportRequest
from app.routers._common import build, call
from app.services import finance_service

router = APIRouter(prefix="/finance", tags=["财务数据"])


@router.get("/profit", summary="盈利能力（季频）", response_model=APIResponse)
def profit_data(
    code: str = Query(..., description="证券代码"),
    year: int | None = Query(None, description="统计年份"),
    quarter: int | None = Query(None, ge=1, le=4, description="统计季度"),
):
    req = build(FinanceDataRequest, code=code, year=year, quarter=quarter)
    return call(finance_service.get_profit_data, req)


@router.get("/operation", summary="营运能力（季频）", response_model=APIResponse)
def operation_data(
    code: str = Query(..., description="证券代码"),
    year: int | None = Query(None, description="统计年份"),
    quarter: int | None = Query(None, ge=1, le=4, description="统计季度"),
):
    req = build(FinanceDataRequest, code=code, year=year, quarter=quarter)
    return call(finance_service.get_operation_data, req)


@router.get("/growth", summary="成长能力（季频）", response_model=APIResponse)
def growth_data(
    code: str = Query(..., description="证券代码"),
    year: int | None = Query(None, description="统计年份"),
    quarter: int | None = Query(None, ge=1, le=4, description="统计季度"),
):
    req = build(FinanceDataRequest, code=code, year=year, quarter=quarter)
    return call(finance_service.get_growth_data, req)


@router.get("/balance", summary="偿债能力（季频）", response_model=APIResponse)
def balance_data(
    code: str = Query(..., description="证券代码"),
    year: int | None = Query(None, description="统计年份"),
    quarter: int | None = Query(None, ge=1, le=4, description="统计季度"),
):
    req = build(FinanceDataRequest, code=code, year=year, quarter=quarter)
    return call(finance_service.get_balance_data, req)


@router.get("/cash_flow", summary="现金流量（季频）", response_model=APIResponse)
def cash_flow_data(
    code: str = Query(..., description="证券代码"),
    year: int | None = Query(None, description="统计年份"),
    quarter: int | None = Query(None, ge=1, le=4, description="统计季度"),
):
    req = build(FinanceDataRequest, code=code, year=year, quarter=quarter)
    return call(finance_service.get_cash_flow_data, req)


@router.get("/dupont", summary="杜邦指数（季频）", response_model=APIResponse)
def dupont_data(
    code: str = Query(..., description="证券代码"),
    year: int | None = Query(None, description="统计年份"),
    quarter: int | None = Query(None, ge=1, le=4, description="统计季度"),
):
    req = build(FinanceDataRequest, code=code, year=year, quarter=quarter)
    return call(finance_service.get_dupont_data, req)


@router.get("/performance_express", summary="业绩快报", response_model=APIResponse)
def performance_express(
    code: str = Query(..., description="证券代码"),
    start_date: str | None = Query(None, description="起始日期"),
    end_date: str | None = Query(None, description="终止日期"),
):
    req = build(ReportRequest, code=code, start_date=start_date, end_date=end_date)
    return call(finance_service.get_performance_express_report, req)


@router.get("/forecast", summary="业绩预告", response_model=APIResponse)
def forecast_report(
    code: str = Query(..., description="证券代码"),
    start_date: str | None = Query(None, description="起始日期"),
    end_date: str | None = Query(None, description="终止日期"),
):
    req = build(ReportRequest, code=code, start_date=start_date, end_date=end_date)
    return call(finance_service.get_forecast_report, req)
