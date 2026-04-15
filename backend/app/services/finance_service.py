"""财务数据服务"""

from app.core.baostock_client import client
from app.models.schemas import FinanceDataRequest, ReportRequest


def get_profit_data(req: FinanceDataRequest) -> list[dict]:
    return client.query_profit_data(
        code=req.code, year=req.year, quarter=req.quarter
    )


def get_operation_data(req: FinanceDataRequest) -> list[dict]:
    return client.query_operation_data(
        code=req.code, year=req.year, quarter=req.quarter
    )


def get_growth_data(req: FinanceDataRequest) -> list[dict]:
    return client.query_growth_data(
        code=req.code, year=req.year, quarter=req.quarter
    )


def get_balance_data(req: FinanceDataRequest) -> list[dict]:
    return client.query_balance_data(
        code=req.code, year=req.year, quarter=req.quarter
    )


def get_cash_flow_data(req: FinanceDataRequest) -> list[dict]:
    return client.query_cash_flow_data(
        code=req.code, year=req.year, quarter=req.quarter
    )


def get_dupont_data(req: FinanceDataRequest) -> list[dict]:
    return client.query_dupont_data(
        code=req.code, year=req.year, quarter=req.quarter
    )


def get_performance_express_report(req: ReportRequest) -> list[dict]:
    return client.query_performance_express_report(
        code=req.code, start_date=req.start_date, end_date=req.end_date
    )


def get_forecast_report(req: ReportRequest) -> list[dict]:
    return client.query_forecast_report(
        code=req.code, start_date=req.start_date, end_date=req.end_date
    )
