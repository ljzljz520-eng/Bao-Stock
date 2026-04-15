# Baostock 股票数据服务

## How to Run

```bash
# 构建并启动
docker-compose up --build -d

# 查看日志
docker-compose logs -f baostock-api

# 停止
docker-compose down
```

- API 文档（本地静态资源，无需外网）: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## Services

| 服务 | 说明 | 端口/协议 |
|------|------|-----------|
| baostock-api | FastAPI RESTful API，提供 20 个数据查询端点 + Swagger 文档 | 8000 (HTTP) |
| baostock-mcp | MCP 工具服务，提供 23 个 tool 供 LLM Agent 调用 | stdio |

## 测试账号

baostock 为免费开源数据源，无需注册账号，匿名即可访问全部数据接口。

## 题目内容

参看akshare_api等的实现,和baostock库的说明，实现对baostock库调用的封装成fastapi和mcp，包含各种数据的查询，参数的支持

---

## 测试验证

全部测试在容器内运行，无需宿主机安装 Python。

```bash
# 1. 启动服务
docker-compose up -d baostock-api

# 2. API 端到端测试（20 个业务端点 + 2 个系统端点 + 6 个参数校验 = 31 个用例）
docker-compose exec baostock-api python test_api.py

# 3. MCP 工具测试（全部 23 个 tool 直接调用验证）
docker-compose exec baostock-api python test_mcp.py
```

API 测试预期输出：
```
==================================================
 Baostock API 端到端验证
==================================================

[系统]
  ✓ 健康检查 (HTTP 200, 0 records)
  ✓ Swagger文档 (HTTP 200, 0 records)

[股票数据]
  ✓ 历史K线 (HTTP 200, 4 records)
  ✓ 交易日查询 (HTTP 200, 10 records)
  ...

[参数校验]
  ✓ 非法频率→422 (HTTP 422)
  ...

==================================================
 ALL PASSED: 31/31
==================================================
```

MCP 测试预期输出：
```
==================================================
 Baostock MCP Tool 端到端验证
==================================================

[股票行情]
  ✓ query_history_k_data (4 records)
  ✓ query_trade_dates (10 records)
  ...

[财务数据]
  ✓ query_profit_data (1 records)
  ...

[宏观经济]
  ✓ query_money_supply_data_month (6 records)
  ...

==================================================
 ALL PASSED: 23/23
==================================================
```

## 接口总览

### 股票行情（10 个端点）

| 端点 | 说明 |
|------|------|
| `GET /api/v1/stock/history_k_data` | 历史K线（日/周/月/5/15/30/60分钟） |
| `GET /api/v1/stock/trade_dates` | 交易日查询 |
| `GET /api/v1/stock/all_stock` | 全部证券列表 |
| `GET /api/v1/stock/stock_basic` | 证券基本资料 |
| `GET /api/v1/stock/stock_industry` | 行业分类 |
| `GET /api/v1/stock/hs300_stocks` | 沪深300成分股 |
| `GET /api/v1/stock/sz50_stocks` | 上证50成分股 |
| `GET /api/v1/stock/zz500_stocks` | 中证500成分股 |
| `GET /api/v1/stock/dividend_data` | 股息分红 |
| `GET /api/v1/stock/adjust_factor` | 复权因子 |

### 财务数据（8 个端点）

| 端点 | 说明 |
|------|------|
| `GET /api/v1/finance/profit` | 盈利能力（季频） |
| `GET /api/v1/finance/operation` | 营运能力（季频） |
| `GET /api/v1/finance/growth` | 成长能力（季频） |
| `GET /api/v1/finance/balance` | 偿债能力（季频） |
| `GET /api/v1/finance/cash_flow` | 现金流量（季频） |
| `GET /api/v1/finance/dupont` | 杜邦指数（季频） |
| `GET /api/v1/finance/performance_express` | 业绩快报 |
| `GET /api/v1/finance/forecast` | 业绩预告 |

### 宏观经济（5 个端点）

| 端点 | 说明 |
|------|------|
| `GET /api/v1/macro/deposit_rate` | 存款利率 |
| `GET /api/v1/macro/loan_rate` | 贷款利率 |
| `GET /api/v1/macro/money_supply_month` | 货币供应量（月） |
| `GET /api/v1/macro/money_supply_year` | 货币供应量（年） |
| `GET /api/v1/macro/reserve_ratio` | 存款准备金率 |

## 参数校验

所有枚举参数使用 Pydantic Enum 严格校验，日期参数使用正则校验，非法参数返回 HTTP 422 及详细错误信息。

| 参数 | 类型 | 合法值 |
|------|------|--------|
| frequency | Enum | `d`, `w`, `m`, `5`, `15`, `30`, `60` |
| adjustflag | Enum | `1`(后复权), `2`(前复权), `3`(不复权) |
| year_type (分红) | Enum | `report`(预案公告), `operate`(除权除息) |
| year_type (准备金) | Enum | `0`(公告日期), `1`(生效日期) |
| 日期字段 | 正则 | `YYYY-MM-DD` |
| 宏观日期 | 正则 | `YYYY-MM-DD` / `YYYY-MM` / `YYYY` |
| quarter | 范围 | 1-4 |
| year (财务) | 范围 | 1990-2100 |

## 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": [{"date": "2024-01-02", "open": "7.1400", ...}],
  "total": 4
}
```

## MCP 配置

在 IDE 或 Agent 中配置 MCP 服务（Docker 方式或本地方式）：

```json
{
  "mcpServers": {
    "baostock": {
      "command": "docker-compose",
      "args": ["exec", "-T", "baostock-mcp", "python", "mcp_server.py"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

本地运行方式：

```json
{
  "mcpServers": {
    "baostock": {
      "command": "python",
      "args": ["backend/mcp_server.py"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## 技术栈

| 依赖 | 版本 |
|------|------|
| Python | 3.12 |
| FastAPI | >=0.104.0,<1.0.0 |
| uvicorn | >=0.24.0,<1.0.0 |
| pydantic | >=2.5.0,<3.0.0 |
| baostock | >=0.8.8,<1.0.0 |
| mcp | >=1.26.0,<2.0.0 |
| pandas | >=2.0.0,<3.0.0 |

## 架构设计

- 线程安全单例 `BaostockClient`（RLock 可重入锁），封装全部 23 个 baostock 查询方法
- 三层架构：Router → Service → Client，职责清晰
- 路由层公共模块 `_common.py`：统一参数构建（`build`）和调用包装（`call`）
- Swagger UI 静态资源本地化，构建时从 npmmirror 国内源下载，无需运行时访问外网
- 多阶段 Docker 构建，`--platform=$BUILDPLATFORM` 支持 ARM + X86 跨平台
- HTTP 请求/响应日志中间件，统一异常处理

## 项目结构

```
├── docker-compose.yml          # 编排 api + mcp 两个服务
├── .gitignore
├── README.md
└── backend/
    ├── Dockerfile              # 多阶段构建，跨平台
    ├── run_api.py              # FastAPI 启动入口
    ├── mcp_server.py           # MCP 服务入口（23 个 tool）
    ├── test_api.py             # API 端到端测试（31 个用例）
    ├── test_mcp.py             # MCP 工具测试（23 个用例）
    ├── requirements.txt
    ├── scripts/
    │   └── download_swagger_ui.py  # 构建时下载 swagger-ui（国内源优先）
    └── app/
        ├── main.py             # FastAPI 应用 + 中间件 + 异常处理
        ├── config.py           # pydantic-settings 配置
        ├── core/
        │   ├── baostock_client.py  # 线程安全单例（RLock）
        │   └── exceptions.py      # 自定义异常
        ├── models/
        │   └── schemas.py      # Pydantic 模型 + Enum + 日期校验
        ├── services/
        │   ├── stock_service.py
        │   ├── finance_service.py
        │   └── macro_service.py
        └── routers/
            ├── _common.py      # build() + call() 公共工具
            ├── stock.py        # 10 个股票端点
            ├── finance.py      # 8 个财务端点
            └── macro.py        # 5 个宏观端点
```
