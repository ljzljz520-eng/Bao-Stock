FROM --platform=$BUILDPLATFORM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 下载 swagger-ui 静态资源（多源 fallback，离线可用）
COPY scripts/download_swagger_ui.py /tmp/download_swagger_ui.py
RUN python /tmp/download_swagger_ui.py /swagger-ui

FROM python:3.12-slim

WORKDIR /app

# 从 builder 复制已安装的依赖
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 从 builder 复制 swagger-ui 静态资源
COPY --from=builder /swagger-ui /app/static

# 应用代码
COPY . .

EXPOSE 8000

CMD ["python", "run_api.py"]
