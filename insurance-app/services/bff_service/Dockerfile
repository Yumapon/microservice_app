# ------------------------------------------------------------------------------
# Build stage: 依存関係インストール用（キャッシュ効率化）
# ------------------------------------------------------------------------------
    FROM python:3.11-slim as builder

    # Python設定：キャッシュ・バッファ出力抑制
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # 必要最小限のビルド依存パッケージをインストール
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        gcc libffi-dev libssl-dev && \
        rm -rf /var/lib/apt/lists/*
    
    # 依存ファイルのみ先にコピー（Dockerレイヤキャッシュ活用）
    COPY requirements.txt .
    
    # pip依存をインストール（/install に分離配置）
    RUN pip install --upgrade pip && \
        pip install --prefix=/install -r requirements.txt
    
    # ------------------------------------------------------------------------------
    # Final stage: 実行用ステージ（最小限の環境）
    # ------------------------------------------------------------------------------
    FROM python:3.11-slim
    
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # ランタイム依存ライブラリのみインストール
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        libffi-dev libssl-dev && \
        rm -rf /var/lib/apt/lists/*
    
    # builder ステージから依存パッケージをコピー
    COPY --from=builder /install /usr/local
    
    # アプリケーションコードをコピー
    COPY . .
    
    # FastAPI 実行ポート（例：BFFサービス）
    EXPOSE 8000
    
    # アプリ起動（開発時は --reload、本番は除去）
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    