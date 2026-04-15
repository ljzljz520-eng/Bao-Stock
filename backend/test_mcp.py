"""
MCP 工具端到端验证脚本 — 覆盖全部 23 个 MCP tool

直接调用 mcp_server 中注册的 tool 函数，验证 baostock 数据查询正确性。
无需启动 MCP 服务进程，在容器内直接运行即可。

用法:
  docker-compose exec baostock-api python test_mcp.py
"""

import sys

sys.path.insert(0, ".")

from mcp_server import (  # noqa: E402
    query_history_k_data,
    query_trade_dates,
    query_all_stock,
    query_stock_basic,
    query_stock_industry,
    query_hs300_stocks,
    query_sz50_stocks,
    query_zz500_stocks,
    query_dividend_data,
    query_adjust_factor,
    query_profit_data,
    query_operation_data,
    query_growth_data,
    query_balance_data,
    query_cash_flow_data,
    query_dupont_data,
    query_performance_express_report,
    query_forecast_report,
    query_deposit_rate_data,
    query_loan_rate_data,
    query_money_supply_data_month,
    query_money_supply_data_year,
    query_required_reserve_ratio_data,
)

PASS = 0
FAIL = 0


def test(name: str, fn, kwargs: dict, expect_min: int = 0):
    """调用 tool 函数，验证返回 list 且长度 >= expect_min"""
    global PASS, FAIL
    try:
        result = fn(**kwargs)
        if not isinstance(result, list):
            print(f"  ✗ {name} — 返回类型错误: {type(result)}")
            FAIL += 1
            return
        if len(result) < expect_min:
            print(f"  ✗ {name} — 记录数 {len(result)} < 预期最少 {expect_min}")
            FAIL += 1
            return
        print(f"  ✓ {name} ({len(result)} records)")
        PASS += 1
    except Exception as e:
        print(f"  ✗ {name} — 异常: {e}")
        FAIL += 1


print("=" * 50)
print(" Baostock MCP Tool 端到端验证")
print("=" * 50)

# ── 股票行情（10 个 tool）────────────────────────
print("\n[股票行情]")
test("query_history_k_data", query_history_k_data,
     {"code": "sh.600000", "fields": "date,code,open,close",
      "start_date": "2024-01-02", "end_date": "2024-01-05"}, 1)
test("query_trade_dates", query_trade_dates,
     {"start_date": "2024-01-01", "end_date": "2024-01-10"}, 1)
test("query_all_stock", query_all_stock,
     {"day": "2024-01-02"}, 1)
test("query_stock_basic", query_stock_basic,
     {"code": "sh.600000"}, 1)
test("query_stock_industry", query_stock_industry,
     {"code": "sh.600000"}, 1)
test("query_hs300_stocks", query_hs300_stocks,
     {"date": "2024-01-02"}, 1)
test("query_sz50_stocks", query_sz50_stocks,
     {"date": "2024-01-02"}, 1)
test("query_zz500_stocks", query_zz500_stocks,
     {"date": "2024-01-02"}, 1)
test("query_dividend_data", query_dividend_data,
     {"code": "sh.600000", "year": "2023"}, 1)
test("query_adjust_factor", query_adjust_factor,
     {"code": "sh.600000", "start_date": "2024-01-01", "end_date": "2024-06-30"})

# ── 财务数据（8 个 tool）─────────────────────────
print("\n[财务数据]")
test("query_profit_data", query_profit_data,
     {"code": "sh.600000", "year": 2023, "quarter": 4}, 1)
test("query_operation_data", query_operation_data,
     {"code": "sh.600000", "year": 2023, "quarter": 4}, 1)
test("query_growth_data", query_growth_data,
     {"code": "sh.600000", "year": 2023, "quarter": 4}, 1)
test("query_balance_data", query_balance_data,
     {"code": "sh.600000", "year": 2023, "quarter": 4}, 1)
test("query_cash_flow_data", query_cash_flow_data,
     {"code": "sh.600000", "year": 2023, "quarter": 4}, 1)
test("query_dupont_data", query_dupont_data,
     {"code": "sh.600000", "year": 2023, "quarter": 4}, 1)
test("query_performance_express_report", query_performance_express_report,
     {"code": "sh.600000", "start_date": "2023-01-01", "end_date": "2023-12-31"}, 1)
test("query_forecast_report", query_forecast_report,
     {"code": "sh.600000", "start_date": "2023-01-01", "end_date": "2023-12-31"})

# ── 宏观经济（5 个 tool）─────────────────────────
print("\n[宏观经济]")
test("query_deposit_rate_data", query_deposit_rate_data,
     {"start_date": "2020-01-01", "end_date": "2020-12-31"})
test("query_loan_rate_data", query_loan_rate_data,
     {"start_date": "2020-01-01", "end_date": "2020-12-31"})
test("query_money_supply_data_month", query_money_supply_data_month,
     {"start_date": "2023-01", "end_date": "2023-06"}, 1)
test("query_money_supply_data_year", query_money_supply_data_year,
     {"start_date": "2020", "end_date": "2023"}, 1)
test("query_required_reserve_ratio_data", query_required_reserve_ratio_data,
     {"start_date": "2020-01-01", "end_date": "2023-12-31"})

# ── 汇总 ─────────────────────────────────────────
print("\n" + "=" * 50)
total = PASS + FAIL
if FAIL == 0:
    print(f" ALL PASSED: {PASS}/{total}")
else:
    print(f" FAILED: {FAIL}/{total}")
print("=" * 50)

sys.exit(FAIL)
