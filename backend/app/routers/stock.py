"""股票行情与基础数据路由"""

from fastapi import APIRouter, Query

from app.models.schemas import (
    AdjustFactorRequest,
    AdjustFlag,
    AllStockRequest,
    APIResponse,
    DividendDataRequest,
    Frequency,
    HistoryKDataRequest,
    IndexStocksRequest,
    StockBasicRequest,
    StockIndustryRequest,
    TradeDatesRequest,
    YearType,
)
from app.routers._common import build, call
from app.services import stock_service

router = APIRouter(prefix="/stock", tags=["股票数据"])


@router.get("/history_k_data", summary="历史K线数据", response_model=APIResponse)
def history_k_data(
    code: str = Query(..., description="证券代码，如 sh.600000"),
    fields: str = Query(
        "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
        description="查询字段",
    ),
    start_date: str | None = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: str | None = Query(None, description="终止日期 YYYY-MM-DD"),
    frequency: Frequency = Query(Frequency.DAILY, description="频率: d/w/m/5/15/30/60"),
    adjustflag: AdjustFlag = Query(AdjustFlag.NONE, description="复权: 1后复权 2前复权 3不复权"),
):
    req = build(HistoryKDataRequest, code=code, fields=fields,
                start_date=start_date, end_date=end_date,
                frequency=frequency, adjustflag=adjustflag)
    return call(stock_service.get_history_k_data, req)


@router.get("/trade_dates", summary="交易日查询", response_model=APIResponse)
def trade_dates(
    start_date: str | None = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: str | None = Query(None, description="终止日期 YYYY-MM-DD"),
):
    req = build(TradeDatesRequest, start_date=start_date, end_date=end_date)
    return call(stock_service.get_trade_dates, req)


@router.get("/all_stock", summary="全部证券列表", response_model=APIResponse)
def all_stock(day: str | None = Query(None, description="查询日期 YYYY-MM-DD")):
    req = build(AllStockRequest, day=day)
    return call(stock_service.get_all_stock, req)


@router.get("/stock_basic", summary="证券基本资料", response_model=APIResponse)
def stock_basic(
    code: str = Query("", description="证券代码"),
    code_name: str = Query("", description="证券名称，支持模糊查询"),
):
    req = build(StockBasicRequest, code=code, code_name=code_name)
    return call(stock_service.get_stock_basic, req)


@router.get("/stock_industry", summary="行业分类", response_model=APIResponse)
def stock_industry(
    code: str = Query("", description="股票代码"),
    date: str = Query("", description="查询日期 YYYY-MM-DD"),
):
    req = build(StockIndustryRequest, code=code, date=date)
    return call(stock_service.get_stock_industry, req)


@router.get("/hs300_stocks", summary="沪深300成分股", response_model=APIResponse)
def hs300_stocks(date: str = Query("", description="查询日期 YYYY-MM-DD")):
    req = build(IndexStocksRequest, date=date)
    return call(stock_service.get_hs300_stocks, req)


@router.get("/sz50_stocks", summary="上证50成分股", response_model=APIResponse)
def sz50_stocks(date: str = Query("", description="查询日期 YYYY-MM-DD")):
    req = build(IndexStocksRequest, date=date)
    return call(stock_service.get_sz50_stocks, req)


@router.get("/zz500_stocks", summary="中证500成分股", response_model=APIResponse)
def zz500_stocks(date: str = Query("", description="查询日期 YYYY-MM-DD")):
    req = build(IndexStocksRequest, date=date)
    return call(stock_service.get_zz500_stocks, req)


@router.get("/dividend_data", summary="股息分红数据", response_model=APIResponse)
def dividend_data(
    code: str = Query(..., description="证券代码"),
    year: str | None = Query(None, description="年份 YYYY"),
    year_type: YearType = Query(YearType.REPORT, description="年份类别: report/operate"),
):
    req = build(DividendDataRequest, code=code, year=year, year_type=year_type)
    return call(stock_service.get_dividend_data, req)


@router.get("/adjust_factor", summary="复权因子", response_model=APIResponse)
def adjust_factor(
    code: str = Query(..., description="证券代码"),
    start_date: str | None = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: str | None = Query(None, description="终止日期 YYYY-MM-DD"),
):
    req = build(AdjustFactorRequest, code=code, start_date=start_date, end_date=end_date)
    return call(stock_service.get_adjust_factor, req)
