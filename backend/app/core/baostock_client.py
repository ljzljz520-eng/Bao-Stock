"""Baostock 连接管理器 — 线程安全的单例封装"""

import threading
from contextlib import contextmanager
from typing import Generator

import baostock as bs
import pandas as pd

from app.core.exceptions import BaostockError


class BaostockClient:
    """
    封装 baostock 的登录/登出和查询操作。
    使用线程锁保证并发安全（baostock 底层是 socket 连接，不支持并发）。
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "BaostockClient":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._logged_in = False
                    cls._instance._query_lock = threading.RLock()
        return cls._instance

    def login(self) -> None:
        with self._query_lock:
            if not self._logged_in:
                result = bs.login()
                if result.error_code != "0":
                    raise BaostockError(result.error_code, result.error_msg)
                self._logged_in = True

    def logout(self) -> None:
        with self._query_lock:
            if self._logged_in:
                bs.logout()
                self._logged_in = False

    @contextmanager
    def _ensure_login(self) -> Generator[None, None, None]:
        """确保已登录，并持有查询锁"""
        with self._query_lock:
            if not self._logged_in:
                self.login()
            yield

    def _result_to_list(self, rs) -> list[dict]:
        """将 baostock ResultData 转为 list[dict]"""
        if rs.error_code != "0":
            raise BaostockError(rs.error_code, rs.error_msg)
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        if not rows:
            return []
        return pd.DataFrame(rows, columns=rs.fields).to_dict(orient="records")

    # ── 股票行情 ──────────────────────────────────────────

    def query_history_k_data(
        self,
        code: str,
        fields: str,
        start_date: str | None = None,
        end_date: str | None = None,
        frequency: str = "d",
        adjustflag: str = "3",
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_history_k_data_plus(
                code, fields,
                start_date=start_date or "",
                end_date=end_date or "",
                frequency=frequency,
                adjustflag=adjustflag,
            )
            return self._result_to_list(rs)

    def query_trade_dates(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_trade_dates(
                start_date=start_date or "",
                end_date=end_date or "",
            )
            return self._result_to_list(rs)

    def query_all_stock(self, day: str | None = None) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_all_stock(day=day or "")
            return self._result_to_list(rs)

    def query_stock_basic(
        self, code: str = "", code_name: str = ""
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_stock_basic(code=code, code_name=code_name)
            return self._result_to_list(rs)

    def query_stock_industry(
        self, code: str = "", date: str = ""
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_stock_industry(code=code, date=date)
            return self._result_to_list(rs)

    # ── 指数成分股 ────────────────────────────────────────

    def query_hs300_stocks(self, date: str = "") -> list[dict]:
        with self._ensure_login():
            rs = bs.query_hs300_stocks(date=date)
            return self._result_to_list(rs)

    def query_sz50_stocks(self, date: str = "") -> list[dict]:
        with self._ensure_login():
            rs = bs.query_sz50_stocks(date=date)
            return self._result_to_list(rs)

    def query_zz500_stocks(self, date: str = "") -> list[dict]:
        with self._ensure_login():
            rs = bs.query_zz500_stocks(date=date)
            return self._result_to_list(rs)

    # ── 分红 / 复权 ──────────────────────────────────────

    def query_dividend_data(
        self, code: str, year: str | None = None, year_type: str = "report"
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_dividend_data(
                code=code, year=year or "", yearType=year_type
            )
            return self._result_to_list(rs)

    def query_adjust_factor(
        self, code: str, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_adjust_factor(
                code=code,
                start_date=start_date or "",
                end_date=end_date or "",
            )
            return self._result_to_list(rs)

    # ── 财务数据（季频） ─────────────────────────────────

    def query_profit_data(
        self, code: str, year: int | None = None, quarter: int | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_profit_data(
                code=code,
                year=year or "",
                quarter=quarter or "",
            )
            return self._result_to_list(rs)

    def query_operation_data(
        self, code: str, year: int | None = None, quarter: int | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_operation_data(
                code=code,
                year=year or "",
                quarter=quarter or "",
            )
            return self._result_to_list(rs)

    def query_growth_data(
        self, code: str, year: int | None = None, quarter: int | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_growth_data(
                code=code,
                year=year or "",
                quarter=quarter or "",
            )
            return self._result_to_list(rs)

    def query_balance_data(
        self, code: str, year: int | None = None, quarter: int | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_balance_data(
                code=code,
                year=year or "",
                quarter=quarter or "",
            )
            return self._result_to_list(rs)

    def query_cash_flow_data(
        self, code: str, year: int | None = None, quarter: int | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_cash_flow_data(
                code=code,
                year=year or "",
                quarter=quarter or "",
            )
            return self._result_to_list(rs)

    def query_dupont_data(
        self, code: str, year: int | None = None, quarter: int | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_dupont_data(
                code=code,
                year=year or "",
                quarter=quarter or "",
            )
            return self._result_to_list(rs)

    # ── 业绩报告 ─────────────────────────────────────────

    def query_performance_express_report(
        self, code: str, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_performance_express_report(
                code=code,
                start_date=start_date or "",
                end_date=end_date or "",
            )
            return self._result_to_list(rs)

    def query_forecast_report(
        self, code: str, start_date: str | None = None, end_date: str | None = None
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_forecast_report(
                code=code,
                start_date=start_date or "",
                end_date=end_date or "",
            )
            return self._result_to_list(rs)

    # ── 宏观经济 ─────────────────────────────────────────

    def query_deposit_rate_data(
        self, start_date: str = "", end_date: str = ""
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_deposit_rate_data(
                start_date=start_date, end_date=end_date
            )
            return self._result_to_list(rs)

    def query_loan_rate_data(
        self, start_date: str = "", end_date: str = ""
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_loan_rate_data(
                start_date=start_date, end_date=end_date
            )
            return self._result_to_list(rs)

    def query_money_supply_data_month(
        self, start_date: str = "", end_date: str = ""
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_money_supply_data_month(
                start_date=start_date, end_date=end_date
            )
            return self._result_to_list(rs)

    def query_money_supply_data_year(
        self, start_date: str = "", end_date: str = ""
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_money_supply_data_year(
                start_date=start_date, end_date=end_date
            )
            return self._result_to_list(rs)

    def query_required_reserve_ratio_data(
        self, start_date: str = "", end_date: str = "", year_type: str = "0"
    ) -> list[dict]:
        with self._ensure_login():
            rs = bs.query_required_reserve_ratio_data(
                start_date=start_date,
                end_date=end_date,
                yearType=year_type,
            )
            return self._result_to_list(rs)


# 全局单例
client = BaostockClient()
