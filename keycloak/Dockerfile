# Keycloak base image（バージョンは必要に応じて変更）
FROM quay.io/keycloak/keycloak:18.0.2

# 作業ディレクトリを設定
WORKDIR /opt/keycloak

# 起動時にビルドモードで実行する（--optimized 起動推奨）
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]

# デフォルトコマンド（start時に override 可能）
CMD ["start-dev"]