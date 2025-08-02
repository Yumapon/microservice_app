-- ============================================================================
-- テーブル: applications（申込情報）
-- ============================================================================
CREATE TABLE applications (
    application_id UUID PRIMARY KEY,                   -- 申込ID
    quote_id UUID NOT NULL,                            -- 紐づく見積もり
    user_id UUID NOT NULL,                             -- ユーザーID（Keycloakのsub）

    application_status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (
        application_status IN ('pending', 'under_review', 'confirmed', 'rejected', 'cancelled')
    ),                                                 -- 申込ステータス

    approved_by UUID,                                  -- 申込承認者（社内ユーザーID）
    approval_date TIMESTAMP,                           -- 申込承認日時
    application_number TEXT,                           -- 社内管理用の申込番号

    applied_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,   -- 申込日時
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 更新日時
    created_by VARCHAR(64),                            -- 作成者（オペレーターIDなど）
    updated_by VARCHAR(64)                             -- 更新者（オペレーターIDなど）
);

-- ============================================================================
-- テーブル: application_details（申込時の契約条件および計算結果を保持）
-- ============================================================================
CREATE TABLE application_details (
    application_id UUID PRIMARY KEY REFERENCES applications(application_id) ON DELETE CASCADE, -- 申込ID（1対1）

    -- 契約条件
    birth_date DATE NOT NULL,                          -- 生年月日
    gender TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other')), -- 性別
    monthly_premium INTEGER NOT NULL,                  -- 月額保険料
    payment_period_years INTEGER NOT NULL,             -- 支払い年数
    tax_deduction_enabled BOOLEAN NOT NULL,            -- 税制適格特約の有無

    -- 計算結果
    contract_date DATE NOT NULL,                       -- 契約開始日
    contract_interest_rate NUMERIC(5,2) NOT NULL,      -- 契約利率
    total_paid_amount INTEGER NOT NULL,                -- 総支払額
    pension_start_age INTEGER NOT NULL,                -- 年金開始年齢
    annual_tax_deduction INTEGER NOT NULL,             -- 年間控除額

    -- 商品連携用コード
    plan_code VARCHAR NOT NULL,                        -- 商品コード

    -- 支払い方法など、申し込み時の追加カラム
    payment_method VARCHAR NOT NULL,                    -- 支払方法（スナップショット）
    user_consent BOOLEAN NOT NULL,                     -- 同意の有無（重要事項説明への同意）
    identity_verified BOOLEAN NOT NULL                -- 本人確認完了フラグ
);