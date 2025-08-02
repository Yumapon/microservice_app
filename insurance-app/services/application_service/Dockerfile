# ベースイメージ（軽量かつ安定）
FROM python:3.9-slim

# 環境変数
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# 必要パッケージインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ作成
WORKDIR ${APP_HOME}

# 必要ファイルをコピー（先にrequirementsでキャッシュ活用）
COPY requirements.txt .

# Pythonパッケージインストール
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 残りのアプリ本体をコピー
COPY ./app ./app
COPY ./config.yaml ./config.yaml

# 非root実行（セキュリティ対策）
RUN useradd -m appuser && \
    chown -R appuser:appuser ${APP_HOME}

USER appuser

# ポートはENVで制御（docker-compose側で対応）
EXPOSE 8000

# 起動コマンドは docker-compose.yaml 側にて定義
# 例: uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT}

# 開発時の参考: ヘルスチェック追加例（オプション）
# HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
#   CMD curl -f http://localhost:8000/health || exit 1
