"""
单元测试 — 直接测试修复的核心逻辑

无需启动服务，直接测试关键函数的逻辑正确性。

用法:
  python test_unit.py
"""

import sys
sys.path.insert(0, ".")


def _normalize_history_frequency(value: str) -> str:
    """从 mcp_server 复制的归一化函数"""
    normalized = value.strip().lower()
    return {
        "5m": "5",
        "15m": "15",
        "30m": "30",
        "60m": "60",
    }.get(normalized, normalized)


def test_frequency_normalization():
    """测试 MCP frequency 归一化函数"""
    test_cases = [
        ("60m", "60"),
        ("30m", "30"),
        ("15m", "15"),
        ("5m", "5"),
        ("d", "d"),
        ("w", "w"),
        ("m", "m"),
        ("60M", "60"),
        (" 60m ", "60"),
    ]
    
    passed = 0
    failed = 0
    
    print("\n[单元测试] MCP frequency 归一化函数")
    for input_val, expected in test_cases:
        result = _normalize_history_frequency(input_val)
        if result == expected:
            print(f"  ✓ '{input_val}' → '{result}'")
            passed += 1
        else:
            print(f"  ✗ '{input_val}' → '{result}' (预期 '{expected}')")
            failed += 1
    
    return passed, failed


def test_trade_dates_boundary():
    """测试 trade_dates 结束日期边界条件"""
    from app.core.baostock_client import client
    from app.models.schemas import TradeDatesRequest
    from app.services.stock_service import get_trade_dates
    
    print("\n[单元测试] trade_dates 结束日期边界条件")
    
    client.login()
    
    req = TradeDatesRequest(start_date="2024-01-01", end_date="2024-01-05")
    result = get_trade_dates(req)
    
    dates = [item.get("calendar_date") for item in result if item.get("calendar_date")]
    expected_end = "2024-01-05"
    
    if expected_end in dates:
        print(f"  ✓ 结束日期 {expected_end} 正确包含在结果中")
        print(f"    返回日期范围: {dates[0]} ~ {dates[-1]}")
        return 1, 0
    else:
        print(f"  ✗ 结束日期 {expected_end} 被错误排除")
        print(f"    实际返回日期: {dates[-3:]}")
        return 0, 1


def test_all_stock_pagination():
    """测试 all_stock 分页total计数"""
    from app.core.baostock_client import client
    from app.models.schemas import AllStockRequest
    from app.services.stock_service import get_all_stock
    
    print("\n[单元测试] all_stock 分页total计数")
    
    client.login()
    
    req_all = AllStockRequest(day="2024-01-02")
    data_all, total_all = get_all_stock(req_all)
    
    req_page1 = AllStockRequest(day="2024-01-02", page=1, page_size=10)
    data_page1, total_page1 = get_all_stock(req_page1)
    
    req_page2 = AllStockRequest(day="2024-01-02", page=2, page_size=10)
    data_page2, total_page2 = get_all_stock(req_page2)
    
    passed = 0
    failed = 0
    
    if total_all == len(data_all):
        print(f"  ✓ 无分页: total={total_all} == len(data)={len(data_all)}")
        passed += 1
    else:
        print(f"  ✗ 无分页: total={total_all} != len(data)={len(data_all)}")
        failed += 1
    
    if total_page1 == total_all:
        print(f"  ✓ 第1页: total={total_page1} == 全部数据总数={total_all}")
        passed += 1
    else:
        print(f"  ✗ 第1页: total={total_page1} != 全部数据总数={total_all}")
        failed += 1
    
    if total_page2 == total_all:
        print(f"  ✓ 第2页: total={total_page2} == 全部数据总数={total_all}")
        passed += 1
    else:
        print(f"  ✗ 第2页: total={total_page2} != 全部数据总数={total_all}")
        failed += 1
    
    if len(data_page2) <= 10:
        print(f"  ✓ 第2页数据长度={len(data_page2)} <= page_size=10")
        passed += 1
    else:
        print(f"  ✗ 第2页数据长度={len(data_page2)} > page_size=10")
        failed += 1
    
    return passed, failed


def main():
    print("=" * 60)
    print(" 单元测试 — 核心逻辑验证")
    print("=" * 60)
    
    total_pass = 0
    total_fail = 0
    
    p, f = test_frequency_normalization()
    total_pass += p
    total_fail += f
    
    try:
        p, f = test_trade_dates_boundary()
        total_pass += p
        total_fail += f
    except Exception as e:
        print(f"  ✗ trade_dates 测试异常: {e}")
        total_fail += 1
    
    try:
        p, f = test_all_stock_pagination()
        total_pass += p
        total_fail += f
    except Exception as e:
        print(f"  ✗ all_stock 测试异常: {e}")
        total_fail += 1
    
    print("\n" + "=" * 60)
    total = total_pass + total_fail
    if total_fail == 0:
        print(f" ALL PASSED: {total_pass}/{total}")
    else:
        print(f" FAILED: {total_fail}/{total}")
    print("=" * 60)
    
    sys.exit(total_fail)


if __name__ == "__main__":
    main()
