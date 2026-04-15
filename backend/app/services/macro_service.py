"""宏观经济数据服务"""

from app.core.baostock_client import client
from app.models.schemas import MacroDateRangeRequest, ReserveRatioRequest


def get_deposit_rate(req: MacroDateRangeRequest) -> list[dict]:
    return client.query_deposit_rate_data(
        start_date=req.start_date, end_date=req.end_date
    )


def get_loan_rate(req: MacroDateRangeRequest) -> list[dict]:
    return client.query_loan_rate_data(
        start_date=req.start_date, end_date=req.end_date
    )


def get_money_supply_month(req: MacroDateRangeRequest) -> list[dict]:
    return client.query_money_supply_data_month(
        start_date=req.start_date, end_date=req.end_date
    )


def get_money_supply_year(req: MacroDateRangeRequest) -> list[dict]:
    return client.query_money_supply_data_year(
        start_date=req.start_date, end_date=req.end_date
    )


def get_required_reserve_ratio(req: ReserveRatioRequest) -> list[dict]:
    return client.query_required_reserve_ratio_data(
        start_date=req.start_date,
        end_date=req.end_date,
        year_type=req.year_type.value,
    )
