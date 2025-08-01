# -*- coding: utf-8 -*-
"""
アプリケーション設定管理クラス

config.yaml を読み込み、各種サービス（Keycloak 等）の設定を提供します。
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import yaml


# ------------------------------------------------------------------------------
# コンフィグ管理クラス
# ------------------------------------------------------------------------------
class Config:
    """
    YAML形式の設定ファイルを読み込み、設定値へアクセスするためのヘルパークラス
    """

    def __init__(self, file_path: str = "config.yaml"):
        """
        コンストラクタで YAML ファイルを読み込み、内部データとして保持

        Parameters:
            file_path (str): 設定ファイルのパス（デフォルトは "config.yaml"）
        """
        with open(file_path, "r") as f:
            self._data = yaml.safe_load(f)

    # --------------------------------------------------------------------------
    # Keycloak設定の取得（任意項目）
    # --------------------------------------------------------------------------
    @property
    def keycloak(self):
        """
        Keycloak 認証設定情報を返す（未設定時は空dictを返す）
        """
        return self._data.get("keycloak", {})

    # --------------------------------------------------------------------------
    # セッション設定の取得（任意項目）
    # --------------------------------------------------------------------------
    @property
    def session(self):
        """
        セッション制御に関する設定情報を返す（未設定時は空dictを返す）
        """
        return self._data.get("session", {})
    
    # --------------------------------------------------------------------------
    # 外部サービスの取得
    # --------------------------------------------------------------------------
    @property
    def plans_service(self):
        """
        plans_serviceに関する設定情報を返す（未設定時は空dictを返す）
        """
        return self._data.get("plans_service", {})
    
    @property
    def quotation_service(self):
        """
        quotation_serviceに関する設定情報を返す（未設定時は空dictを返す）
        """
        return self._data.get("quotation_service", {})

    @property
    def application_service(self):
        """
        application_serviceに関する設定情報を返す（未設定時は空dictを返す）
        """
        return self._data.get("application_service", {})
    
    @property
    def contraction_service(self):
        """
        contraction_serviceに関する設定情報を返す（未設定時は空dictを返す）
        """
        return self._data.get("contraction_service", {})