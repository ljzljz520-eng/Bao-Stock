"""
Baostock MCP Server
将 baostock 全部查询接口暴露为 MCP 工具，供 LLM Agent 调用。
启动方式: python mcp_server.py
"""

import logging
import sys

from mcp.server.fastmcp import FastMCP

# 将项目根目录加入 path，以便 import app 模块
sys.path.insert(0, ".")

from app.core.baostock_client import client  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("baostock-server")


# ── 启动时登录 baostock ──────────────────────────────────
_logged_in = False


def _ensure_login():
    global _logged_in
    if not _logged_in:
        client.login()
        _logged_in = True


# ══════════════════════════════════════════════════════════
#  股票行情工具
# ══════════════════════════════════════════════════════════


@mcp.tool()
def query_history_k_data(
    code: str,
    fields: str = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
    start_date: str = "",
    end_date: str = "",
    frequency: str = "d",
    adjustflag: str = "3",
) -> list[dict]:
    """
    查询历史K线数据。
    - code: 证券代码，如 sh.600000、sz.000001
    - fields: 查询字段，逗号分隔
    - start_date: 起始日期 YYYY-MM-DD
    - end_date: 终止日期 YYYY-MM-DD
    - frequency: 数据频率 d日/w周/m月/5分钟/15分钟/30分钟/60分钟
    - adjustflag: 复权类型 1后复权 2前复权 3不复权
    """
    _ensure_login()
    return client.query_history_k_data(
        code=code, fields=fields, start_date=start_date or None,
        end_date=end_date or None, frequency=frequency, adjustflag=adjustflag,
    )


@mcp.tool()
def query_trade_dates(
    start_date: str = "", end_date: str = ""
) -> list[dict]:
    """
    查询交易日信息。
    - start_date: 起始日期 YYYY-MM-DD，默认 2015-01-01
    - end_date: 终止日期 YYYY-MM-DD，默认当前日期
    返回字段: calendar_date(日期), is_trading_day(是否交易日 0/1)
    """
    _ensure_login()
    return client.query_trade_dates(
        start_date=start_date or None, end_date=end_date or None
    )


@mcp.tool()
def query_all_stock(day: str = "") -> list[dict]:
    """
    查询指定日期的全部证券列表。
    - day: 查询日期 YYYY-MM-DD，默认当前日期
    """
    _ensure_login()
    return client.query_all_stock(day=day or None)


@mcp.tool()
def query_stock_basic(code: str = "", code_name: str = "") -> list[dict]:
    """
    查询A股证券基本资料。
    - code: 证券代码，可为空
    - code_name: 证券名称，支持模糊查询
    """
    _ensure_login()
    return client.query_stock_basic(code=code, code_name=code_name)


@mcp.tool()
def query_stock_industry(code: str = "", date: str = "") -> list[dict]:
    """
    查询行业分类信息。
    - code: 股票代码
    - date: 查询日期 YYYY-MM-DD
    """
    _ensure_login()
    return client.query_stock_industry(code=code, date=date)


# ── 指数成分股 ────────────────────────────────────────────


@mcp.tool()
def query_hs300_stocks(date: str = "") -> list[dict]:
    """
    查询沪深300成分股。
    - date: 查询日期 YYYY-MM-DD
    """
    _ensure_login()
    return client.query_hs300_stocks(date=date)


@mcp.tool()
def query_sz50_stocks(date: str = "") -> list[dict]:
    """
    查询上证50成分股。
    - date: 查询日期 YYYY-MM-DD
    """
    _ensure_login()
    return client.query_sz50_stocks(date=date)


@mcp.tool()
def query_zz500_stocks(date: str = "") -> list[dict]:
    """
    查询中证500成分股。
    - date: 查询日期 YYYY-MM-DD
    """
    _ensure_login()
    return client.query_zz500_stocks(date=date)


# ── 分红 / 复权 ──────────────────────────────────────────


@mcp.tool()
def query_dividend_data(
    code: str, year: str = "", year_type: str = "report"
) -> list[dict]:
    """
    查询股息分红数据。
    - code: 证券代码（必填）
    - year: 年份
    - year_type: 年份类别 report(预案公告年份) / operate(除权除息年份)
    """
    _ensure_login()
    return client.query_dividend_data(
        code=code, year=year or None, year_type=year_type
    )


@mcp.tool()
def query_adjust_factor(
    code: str, start_date: str = "", end_date: str = ""
) -> list[dict]:
    """
    查询复权因子信息。
    - code: 证券代码（必填）
    - start_date: 起始除权除息日期
    - end_date: 终止除权除息日期
    """
    _ensure_login()
    return client.query_adjust_factor(
        code=code, start_date=start_date or None, end_date=end_date or None
    )


# ══════════════════════════════════════════════════════════
#  财务数据工具
# ══════════════════════════════════════════════════════════


@mcp.tool()
def query_profit_data(
    code: str, year: int | None = None, quarter: int | None = None
) -> list[dict]:
    """
    查询季频盈利能力数据。
    - code: 证券代码（必填）
    - year: 统计年份
    - quarter: 统计季度 1-4
    """
    _ensure_login()
    return client.query_profit_data(code=code, year=year, quarter=quarter)


@mcp.tool()
def query_operation_data(
    code: str, year: int | None = None, quarter: int | None = None
) -> list[dict]:
    """
    查询季频营运能力数据。
    - code: 证券代码（必填）
    - year: 统计年份
    - quarter: 统计季度 1-4
    """
    _ensure_login()
    return client.query_operation_data(code=code, year=year, quarter=quarter)


@mcp.tool()
def query_growth_data(
    code: str, year: int | None = None, quarter: int | None = None
) -> list[dict]:
    """
    查询季频成长能力数据。
    - code: 证券代码（必填）
    - year: 统计年份
    - quarter: 统计季度 1-4
    """
    _ensure_login()
    return client.query_growth_data(code=code, year=year, quarter=quarter)


@mcp.tool()
def query_balance_data(
    code: str, year: int | None = None, quarter: int | None = None
) -> list[dict]:
    """
    查询季频偿债能力数据。
    - code: 证券代码（必填）
    - year: 统计年份
    - quarter: 统计季度 1-4
    """
    _ensure_login()
    return client.query_balance_data(code=code, year=year, quarter=quarter)


@mcp.tool()
def query_cash_flow_data(
    code: str, year: int | None = None, quarter: int | None = None
) -> list[dict]:
    """
    查询季频现金流量数据。
    - code: 证券代码（必填）
    - year: 统计年份
    - quarter: 统计季度 1-4
    """
    _ensure_login()
    return client.query_cash_flow_data(code=code, year=year, quarter=quarter)


@mcp.tool()
def query_dupont_data(
    code: str, year: int | None = None, quarter: int | None = None
) -> list[dict]:
    """
    查询季频杜邦指数数据。
    - code: 证券代码（必填）
    - year: 统计年份
    - quarter: 统计季度 1-4
    """
    _ensure_login()
    return client.query_dupont_data(code=code, year=year, quarter=quarter)


@mcp.tool()
def query_performance_express_report(
    code: str, start_date: str = "", end_date: str = ""
) -> list[dict]:
    """
    查询公司业绩快报。
    - code: 证券代码（必填）
    - start_date: 开始日期
    - end_date: 结束日期
    """
    _ensure_login()
    return client.query_performance_express_report(
        code=code, start_date=start_date or None, end_date=end_date or None
    )


@mcp.tool()
def query_forecast_report(
    code: str, start_date: str = "", end_date: str = ""
) -> list[dict]:
    """
    查询公司业绩预告。
    - code: 证券代码（必填）
    - start_date: 开始日期
    - end_date: 结束日期
    """
    _ensure_login()
    return client.query_forecast_report(
        code=code, start_date=start_date or None, end_date=end_date or None
    )


# ══════════════════════════════════════════════════════════
#  宏观经济数据工具
# ══════════════════════════════════════════════════════════


@mcp.tool()
def query_deposit_rate_data(
    start_date: str = "", end_date: str = ""
) -> list[dict]:
    """
    查询存款利率数据。
    - start_date: 起始日期
    - end_date: 终止日期
    """
    _ensure_login()
    return client.query_deposit_rate_data(
        start_date=start_date, end_date=end_date
    )


@mcp.tool()
def query_loan_rate_data(
    start_date: str = "", end_date: str = ""
) -> list[dict]:
    """
    查询贷款利率数据。
    - start_date: 起始日期
    - end_date: 终止日期
    """
    _ensure_login()
    return client.query_loan_rate_data(
        start_date=start_date, end_date=end_date
    )


@mcp.tool()
def query_money_supply_data_month(
    start_date: str = "", end_date: str = ""
) -> list[dict]:
    """
    查询货币供应量（月度）数据。
    - start_date: 起始年月 yyyy-MM
    - end_date: 终止年月 yyyy-MM
    """
    _ensure_login()
    return client.query_money_supply_data_month(
        start_date=start_date, end_date=end_date
    )


@mcp.tool()
def query_money_supply_data_year(
    start_date: str = "", end_date: str = ""
) -> list[dict]:
    """
    查询货币供应量（年度余额）数据。
    - start_date: 起始年份 yyyy
    - end_date: 终止年份 yyyy
    """
    _ensure_login()
    return client.query_money_supply_data_year(
        start_date=start_date, end_date=end_date
    )


@mcp.tool()
def query_required_reserve_ratio_data(
    start_date: str = "", end_date: str = "", year_type: str = "0"
) -> list[dict]:
    """
    查询存款准备金率数据。
    - start_date: 起始日期
    - end_date: 终止日期
    - year_type: 日期类型 0公告日期 1生效日期
    """
    _ensure_login()
    return client.query_required_reserve_ratio_data(
        start_date=start_date, end_date=end_date, year_type=year_type
    )


# ══════════════════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run()
