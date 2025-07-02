# ------------------------------------------------------------------------------
# Build stage: 依存関係インストール用（キャッシュ効率化）
# ------------------------------------------------------------------------------
    FROM python:3.11-slim as builder

    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # ランタイム・ビルドに必要なツールを最小限インストール
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        gcc libffi-dev libssl-dev && \
        rm -rf /var/lib/apt/lists/*
    
    # requirements.txt のみを先にコピー（キャッシュ効率を高める）
    COPY requirements.txt .
    
    # 仮想パスにインストール（次のステージにコピーするため）
    RUN pip install --upgrade pip && \
        pip install --prefix=/install -r requirements.txt
    
    
    # ------------------------------------------------------------------------------
    # Final stage: 実行用ステージ（最小限の環境）
    # ------------------------------------------------------------------------------
    FROM python:3.11-slim
    
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # 必要な共有ライブラリのみインストール
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        libffi-dev libssl-dev && \
        rm -rf /var/lib/apt/lists/*
    
    # builder ステージから依存関係をコピー
    COPY --from=builder /install /usr/local
    
    # アプリケーション本体をコピー
    COPY . .
    
    # FastAPI 実行ポートを公開
    EXPOSE 8000
    
    # アプリ起動（--reload は本番では外す）
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    