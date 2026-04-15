"""股票行情与基础数据服务"""

from app.core.baostock_client import client
from app.models.schemas import (
    AdjustFactorRequest,
    AllStockRequest,
    DividendDataRequest,
    HistoryKDataRequest,
    IndexStocksRequest,
    StockBasicRequest,
    StockIndustryRequest,
    TradeDatesRequest,
)


def get_history_k_data(req: HistoryKDataRequest) -> list[dict]:
    return client.query_history_k_data(
        code=req.code,
        fields=req.fields,
        start_date=req.start_date,
        end_date=req.end_date,
        frequency=req.frequency.value,
        adjustflag=req.adjustflag.value,
    )


def get_trade_dates(req: TradeDatesRequest) -> list[dict]:
    data = client.query_trade_dates(
        start_date=req.start_date, end_date=req.end_date
    )
    if req.end_date:
        data = [
            row for row in data
            if row.get("calendar_date", "") < req.end_date
        ]
    return data


def get_all_stock(req: AllStockRequest) -> list[dict]:
    data = client.query_all_stock(day=req.day)
    if req.page is not None and req.page_size is not None:
        start = (req.page - 1) * req.page_size
        end = start + req.page_size
        return data[start:end]
    return data


def get_stock_basic(req: StockBasicRequest) -> list[dict]:
    return client.query_stock_basic(code=req.code, code_name=req.code_name)


def get_stock_industry(req: StockIndustryRequest) -> list[dict]:
    return client.query_stock_industry(code=req.code, date=req.date)


def get_hs300_stocks(req: IndexStocksRequest) -> list[dict]:
    return client.query_hs300_stocks(date=req.date)


def get_sz50_stocks(req: IndexStocksRequest) -> list[dict]:
    return client.query_sz50_stocks(date=req.date)


def get_zz500_stocks(req: IndexStocksRequest) -> list[dict]:
    return client.query_zz500_stocks(date=req.date)


def get_dividend_data(req: DividendDataRequest) -> list[dict]:
    return client.query_dividend_data(
        code=req.code, year=req.year, year_type=req.year_type.value
    )


def get_adjust_factor(req: AdjustFactorRequest) -> list[dict]:
    return client.query_adjust_factor(
        code=req.code, start_date=req.start_date, end_date=req.end_date
    )
