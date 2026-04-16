"""
回归测试 — 覆盖4个缺陷场景和错误响应schema一致性

用法:
  1. 启动服务:  docker-compose up -d baostock-api
  2. 运行测试:  python test_regression.py
  3. 或在容器内: docker-compose exec baostock-api python test_regression.py
"""

import json
import sys
import urllib.request
import urllib.error

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0


def test(name: str, path: str, validator, expect_status: int = 200):
    """通用测试函数，支持自定义验证器"""
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

    if status != expect_status:
        print(f"  ✗ {name} (预期状态码 {expect_status}, 实际 {status})")
        FAIL += 1
        return

    ok, msg = validator(body, status)
    if ok:
        print(f"  ✓ {name}")
        PASS += 1
    else:
        print(f"  ✗ {name} — {msg}")
        FAIL += 1


def validate_error_schema(body, status):
    """验证错误响应schema一致性"""
    required_fields = ["code", "message", "data", "total"]
    for field in required_fields:
        if field not in body:
            return False, f"缺少必填字段: {field}"
    
    if body["code"] != -1:
        return False, f"code 应为 -1，实际为 {body['code']}"
    
    if body["data"] != []:
        return False, f"data 应为 []，实际为 {body['data']}"
    
    if body["total"] != 0:
        return False, f"total 应为 0，实际为 {body['total']}"
    
    return True, "schema 正确"


def validate_422_schema(body, status):
    """验证422错误响应schema"""
    ok, msg = validate_error_schema(body, status)
    if not ok:
        return False, msg
    if "detail" not in body:
        return False, "422响应应包含detail字段"
    return True, "422 schema 正确"


def validate_frequency_60m(body, status):
    """验证frequency=60m返回数据（只要成功返回数据即可）"""
    if body.get("code") != 0:
        return False, f"请求失败: {body.get('message')}"
    return True, "frequency=60m 解析成功"


def validate_trade_dates_end_date(body, status):
    """验证trade_dates结束日期边界条件"""
    if body.get("code") != 0:
        return False, f"请求失败: {body.get('message')}"
    
    data = body.get("data", [])
    if not data:
        return False, "无数据返回"
    
    dates = [item.get("calendar_date") for item in data if item.get("calendar_date")]
    if not dates:
        return False, "数据中无calendar_date字段"
    
    expected_end = "2024-01-05"
    if expected_end not in dates:
        return False, f"结束日期 {expected_end} 被错误排除，实际日期: {dates[-3:]}"
    
    return True, f"结束日期 {expected_end} 正确包含"


def validate_all_stock_total(body, status):
    """验证all_stock分页total计数正确"""
    if body.get("code") != 0:
        return False, f"请求失败: {body.get('message')}"
    
    total = body.get("total")
    data = body.get("data", [])
    
    if total is None:
        return False, "缺少total字段"
    
    if len(data) > total:
        return False, f"分页数据长度 {len(data)} > total {total}"
    
    if total < len(data):
        return True, f"分页正常: total={total}, 当前页={len(data)}"
    
    return True, f"total 正确: {total}"


print("=" * 60)
print(" 回归测试 — 缺陷修复验证")
print("=" * 60)

# ── 缺陷1: frequency=60m 解析一致性 ─────────────────
print("\n[缺陷1] frequency=60m HTTP与MCP解析一致性")
test("HTTP frequency=60m",
     "/api/v1/stock/history_k_data?code=sh.600000&start_date=2024-01-02&end_date=2024-01-05&frequency=60m",
     validate_frequency_60m)

# ── 缺陷2: trade_dates 结束日期边界 ─────────────────
print("\n[缺陷2] trade_dates 结束日期边界条件")
test("trade_dates 包含结束日期",
     "/api/v1/stock/trade_dates?start_date=2024-01-01&end_date=2024-01-05",
     validate_trade_dates_end_date)

# ── 缺陷3: all_stock 分页total计数 ─────────────────
print("\n[缺陷3] all_stock 分页total计数")
test("all_stock 第1页",
     "/api/v1/stock/all_stock?day=2024-01-02&page=1&page_size=10",
     validate_all_stock_total)
test("all_stock 第2页",
     "/api/v1/stock/all_stock?day=2024-01-02&page=2&page_size=10",
     validate_all_stock_total)

# ── 缺陷4: 422错误响应schema ───────────────────────
print("\n[缺陷4] 422错误响应schema一致性")
test("参数校验失败→422 schema",
     "/api/v1/stock/history_k_data?code=sh.600000&frequency=invalid",
     validate_422_schema, 422)

# ── 额外: 所有错误路径schema一致性 ──────────────────
print("\n[错误响应schema] 所有异常路径统一验证")
test("ValidationError 路径",
     "/api/v1/stock/history_k_data?code=invalid_code",
     validate_error_schema, 422)
test("非法日期格式→422",
     "/api/v1/stock/trade_dates?start_date=20240101&end_date=20240110",
     validate_error_schema, 422)
test("非法季度参数→422",
     "/api/v1/finance/profit?code=sh.600000&quarter=5",
     validate_error_schema, 422)

# ── 汇总 ─────────────────────────────────────────
print("\n" + "=" * 60)
total = PASS + FAIL
if FAIL == 0:
    print(f" ALL PASSED: {PASS}/{total}")
else:
    print(f" FAILED: {FAIL}/{total}")
print("=" * 60)

sys.exit(FAIL)
