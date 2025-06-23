#ビルド用の軽量ステージ
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./v1/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

#実行用の最小ステージ
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

# 必要ポート公開 (FastAPIは8000)
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]