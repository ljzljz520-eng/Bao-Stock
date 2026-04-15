# Baostock API & MCP Server

将 baostock 股票数据库的查询接口封装为 FastAPI RESTful API 和 MCP 工具服务。

## 功能覆盖

| 分类 | 接口 |
|------|------|
| 股票行情 | 历史K线、交易日、全部证券、证券基本资料、行业分类 |
| 指数成分 | 沪深300、上证50、中证500 成分股 |
| 分红复权 | 股息分红、复权因子 |
| 财务数据 | 盈利能力、营运能力、成长能力、偿债能力、现金流量、杜邦指数 |
| 业绩报告 | 业绩快报、业绩预告 |
| 宏观经济 | 存款利率、贷款利率、货币供应量(月/年)、存款准备金率 |

## 安装

```bash
pip install -r requirements.txt
```

## 启动 FastAPI 服务

```bash
python run_api.py
```

API 文档: http://localhost:8000/docs

## 启动 MCP 服务

```bash
python mcp_server.py
```

### MCP 配置示例 (mcp.json)

```json
{
  "mcpServers": {
    "baostock": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## API 示例

```bash
# 历史K线
curl "http://localhost:8000/api/v1/stock/history_k_data?code=sh.600000&start_date=2024-01-01&end_date=2024-01-31"

# 盈利能力
curl "http://localhost:8000/api/v1/finance/profit?code=sh.600000&year=2023&quarter=4"

# 存款利率
curl "http://localhost:8000/api/v1/macro/deposit_rate?start_date=2020-01-01"
```

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── core/
│   │   ├── baostock_client.py  # baostock 连接管理（线程安全单例）
│   │   └── exceptions.py       # 异常定义
│   ├── models/
│   │   └── schemas.py          # Pydantic 请求/响应模型
│   ├── services/
│   │   ├── stock_service.py    # 股票数据服务
│   │   ├── finance_service.py  # 财务数据服务
│   │   └── macro_service.py    # 宏观数据服务
│   └── routers/
│       ├── stock.py            # 股票路由
│       ├── finance.py          # 财务路由
│       └── macro.py            # 宏观路由
├── mcp_server.py             # MCP 服务入口
├── run_api.py                # FastAPI 启动脚本
└── requirements.txt
```
