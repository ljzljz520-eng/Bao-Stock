"""
端到端验证脚本 — 覆盖全部 20 个 API 端点 + 参数校验

用法:
  1. 启动服务:  docker-compose up -d baostock-api
  2. 运行测试:  python test_api.py
  3. 或在容器内: docker-compose exec baostock-api python test_api.py
"""

import json
import sys
import urllib.request
import urllib.error

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0


def test(name: str, path: str, expect_status: int = 200):
    global PASS, FAIL
    url = f"{BASE}{path}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=30)
        status = resp.status
        raw = resp.read()
        try:
            body = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            body = {}
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
    except Exception as e:
        print(f"  ✗ {name} — 连接失败: {e}")
        FAIL += 1
        return

    ok = status == expect_status
    if ok and expect_status == 200:
        ok = body.get("code", 0) == 0

    if ok:
        detail = f"HTTP {status}"
        if expect_status == 200:
            detail += f", {body.get('total', 0)} records"
        print(f"  ✓ {name} ({detail})")
        PASS += 1
    else:
        print(f"  ✗ {name} (expected {expect_status}, got {status})")
        FAIL += 1


print("=" * 50)
print(" Baostock API 端到端验证")
print("=" * 50)

# ── 系统 ──────────────────────────────────────────
print("\n[系统]")
test("健康检查", "/health")
test("Swagger文档", "/docs")

# ── 股票数据（10个端点）─────────────────────────────
print("\n[股票数据]")
test("历史K线",
     "/api/v1/stock/history_k_data?code=sh.600000&start_date=2024-01-02&end_date=2024-01-05&fields=date,code,open,close")
test("交易日查询",
     "/api/v1/stock/trade_dates?start_date=2024-01-01&end_date=2024-01-10")
test("全部证券",
     "/api/v1/stock/all_stock?day=2024-01-02")
test("证券基本资料",
     "/api/v1/stock/stock_basic?code=sh.600000")
test("行业分类",
     "/api/v1/stock/stock_industry?code=sh.600000")
test("沪深300成分股",
     "/api/v1/stock/hs300_stocks?date=2024-01-02")
test("上证50成分股",
     "/api/v1/stock/sz50_stocks?date=2024-01-02")
test("中证500成分股",
     "/api/v1/stock/zz500_stocks?date=2024-01-02")
test("股息分红",
     "/api/v1/stock/dividend_data?code=sh.600000&year=2023")
test("复权因子",
     "/api/v1/stock/adjust_factor?code=sh.600000&start_date=2024-01-01&end_date=2024-06-30")

# ── 财务数据（8个端点）─────────────────────────────
print("\n[财务数据]")
test("盈利能力",
     "/api/v1/finance/profit?code=sh.600000&year=2023&quarter=4")
test("营运能力",
     "/api/v1/finance/operation?code=sh.600000&year=2023&quarter=4")
test("成长能力",
     "/api/v1/finance/growth?code=sh.600000&year=2023&quarter=4")
test("偿债能力",
     "/api/v1/finance/balance?code=sh.600000&year=2023&quarter=4")
test("现金流量",
     "/api/v1/finance/cash_flow?code=sh.600000&year=2023&quarter=4")
test("杜邦指数",
     "/api/v1/finance/dupont?code=sh.600000&year=2023&quarter=4")
test("业绩快报",
     "/api/v1/finance/performance_express?code=sh.600000&start_date=2023-01-01&end_date=2023-12-31")
test("业绩预告",
     "/api/v1/finance/forecast?code=sh.600000&start_date=2023-01-01&end_date=2023-12-31")

# ── 宏观经济（5个端点）─────────────────────────────
print("\n[宏观经济]")
test("存款利率",
     "/api/v1/macro/deposit_rate?start_date=2020-01-01&end_date=2020-12-31")
test("贷款利率",
     "/api/v1/macro/loan_rate?start_date=2020-01-01&end_date=2020-12-31")
test("货币供应量(月)",
     "/api/v1/macro/money_supply_month?start_date=2023-01&end_date=2023-06")
test("货币供应量(年)",
     "/api/v1/macro/money_supply_year?start_date=2020&end_date=2023")
test("存款准备金率",
     "/api/v1/macro/reserve_ratio?start_date=2020-01-01&end_date=2023-12-31")

# ── 参数校验（应返回 422）────────────────────────
print("\n[参数校验]")
test("非法频率→422",
     "/api/v1/stock/history_k_data?code=sh.600000&frequency=x", 422)
test("非法复权→422",
     "/api/v1/stock/history_k_data?code=sh.600000&adjustflag=9", 422)
test("非法日期格式→422",
     "/api/v1/stock/trade_dates?start_date=20240101", 422)
test("非法季度→422",
     "/api/v1/finance/profit?code=sh.600000&quarter=5", 422)
test("非法年份类别→422",
     "/api/v1/stock/dividend_data?code=sh.600000&year_type=invalid", 422)
test("非法准备金日期类型→422",
     "/api/v1/macro/reserve_ratio?year_type=2", 422)

# ── 汇总 ─────────────────────────────────────────
print("\n" + "=" * 50)
total = PASS + FAIL
if FAIL == 0:
    print(f" ALL PASSED: {PASS}/{total}")
else:
    print(f" FAILED: {FAIL}/{total}")
print("=" * 50)

sys.exit(FAIL)
