# -------------------------------
# ベースイメージ（軽量かつ安定）
# -------------------------------
FROM python:3.9-slim

# -------------------------------
# 環境変数定義（バイトコード抑止・即時ログ出力・作業ディレクトリ定義）
# -------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# -------------------------------
# 必要なパッケージをインストール（build-essential のみ）
# -------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# -------------------------------
# 作業ディレクトリ作成
# -------------------------------
WORKDIR ${APP_HOME}

# -------------------------------
# requirements.txt を先にコピーしてキャッシュ有効化
# -------------------------------
COPY requirements.txt .

# -------------------------------
# Pythonパッケージインストール
# -------------------------------
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------------
# アプリケーションコードと設定ファイルをコピー
# -------------------------------
COPY ./app ./app
COPY ./config.yaml ./config.yaml

# -------------------------------
# セキュリティ強化：非rootユーザーで実行
# -------------------------------
RUN useradd -m appuser && \
    chown -R appuser:appuser ${APP_HOME}

USER appuser

# -------------------------------
# アプリケーションポート（EXPOSE はドキュメント目的）
# -------------------------------
EXPOSE 8000

# -------------------------------
# CMD は docker-compose.yaml 側で指定（柔軟性重視）
# -------------------------------