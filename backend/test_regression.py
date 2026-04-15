"""
回归测试脚本 — 专门锁定本次 4 个修复点的语义验证

用法:
  python test_regression.py
"""

import json
import sys
import urllib.request
import urllib.error

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0


def assert_eq(name: str, actual, expected):
    global PASS, FAIL
    if actual == expected:
        print(f"  ✓ {name}")
        PASS += 1
    else:
        print(f"  ✗ {name}: expected {expected!r}, got {actual!r}")
        FAIL += 1


def get(path: str):
    url = f"{BASE}{path}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        print(f"  连接失败: {e}")
        return None, None


print("=" * 60)
print(" 回归测试 — 本次 4 个修复点验证")
print("=" * 60)

# ── 修复点 1: frequency 60m 归一化一致性 ─────────────────
print("\n[修复点 1] frequency=60m 归一化一致性")
status1, body1 = get("/api/v1/stock/history_k_data?code=sh.600000&start_date=2024-01-02&end_date=2024-01-05&frequency=60m")
status2, body2 = get("/api/v1/stock/history_k_data?code=sh.600000&start_date=2024-01-02&end_date=2024-01-05&frequency=60")
if status1 == 200 and status2 == 200:
    assert_eq("60m 和 60 返回记录数相同", body1.get("total"), body2.get("total"))
    assert_eq("60m 和 60 数据内容一致", body1.get("data"), body2.get("data"))
else:
    print(f"  ✗ 请求失败 (60m: {status1}, 60: {status2})")
    FAIL += 2

# ── 修复点 2: trade_dates 结束日期不被排除 ───────────────
print("\n[修复点 2] trade_dates 结束日期包含验证")
status, body = get("/api/v1/stock/trade_dates?start_date=2024-01-01&end_date=2024-01-05")
if status == 200:
    dates = [row.get("calendar_date") for row in body.get("data", [])]
    assert_eq("结束日期 2024-01-05 被包含", "2024-01-05" in dates, True)
    assert_eq("没有超过结束日期的记录", all(d <= "2024-01-05" for d in dates if d), True)
else:
    print(f"  ✗ 请求失败: {status}")
    FAIL += 2

# ── 修复点 3: all_stock 分页 total 计数正确 ──────────────
print("\n[修复点 3] all_stock 分页 total 计数验证")
status_full, body_full = get("/api/v1/stock/all_stock?day=2024-01-02")
status_page, body_page = get("/api/v1/stock/all_stock?day=2024-01-02&page=1&page_size=10")
if status_full == 200 and status_page == 200:
    full_total = body_full.get("total")
    page_total = body_page.get("total")
    assert_eq("分页 total = 全量 total", page_total, full_total)
    assert_eq("分页 total >= 当前页记录数", page_total >= len(body_page.get("data", [])), True)
    assert_eq("分页 total 不是 len(data)-1", page_total != max(len(body_page.get("data", [])) - 1, 0), True)
else:
    print(f"  ✗ 请求失败 (full: {status_full}, page: {status_page})")
    FAIL += 3

# ── 修复点 4: 422 响应结构统一 schema ────────────────────
print("\n[修复点 4] 422 响应结构一致性验证")
status, body = get("/api/v1/stock/history_k_data?code=sh.600000&frequency=invalid")
if status == 422:
    assert_eq("422 包含 code 字段", "code" in body, True)
    assert_eq("422 包含 message 字段", "message" in body, True)
    assert_eq("422 包含 detail 字段", "detail" in body, True)
    assert_eq("422 data 是数组类型", isinstance(body.get("data"), list), True)
    assert_eq("422 包含 total 字段", "total" in body, True)
    assert_eq("422 total = 0", body.get("total"), 0)
else:
    print(f"  ✗ 期望 422，实际 {status}")
    FAIL += 6

# ── 汇总 ─────────────────────────────────────────────────
print("\n" + "=" * 60)
total = PASS + FAIL
if FAIL == 0:
    print(f"  ALL PASSED: {PASS}/{total}")
else:
    print(f"  FAILED: {FAIL}/{total}")
print("=" * 60)

sys.exit(FAIL)
