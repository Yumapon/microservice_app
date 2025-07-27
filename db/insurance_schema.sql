
-- ============================================================================
-- テーブル: quotes（見積もりの基本情報を保持）
-- ============================================================================
CREATE TABLE quotes (
    quote_id UUID PRIMARY KEY,                         -- 見積もりID
    user_id UUID NOT NULL,                             -- ユーザーID（Keycloakのsub）
    quote_state VARCHAR(32) NOT NULL DEFAULT 'draft' CHECK (
        quote_state IN ('draft', 'confirmed', 'applied', 'cancelled', 'expired')
    ),                                                 -- ステータス（状態遷移図に基づく）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 作成日時
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 更新日時

    created_by VARCHAR(64),                            -- 作成者
    updated_by VARCHAR(64)                             -- 更新者
);

-- ============================================================================
-- テーブル: quote_details（見積もりの契約条件および計算結果を分離保持）
-- ============================================================================
CREATE TABLE quote_details (
    quote_id UUID PRIMARY KEY REFERENCES quotes(quote_id) ON DELETE CASCADE,  -- 見積もりID（1対1）

    -- 契約条件
    birth_date DATE NOT NULL,                          -- 生年月日
    gender TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other')), -- 性別
    monthly_premium INTEGER NOT NULL,                  -- 月額保険料
    payment_period_years INTEGER NOT NULL,             -- 支払い年数
    tax_deduction_enabled BOOLEAN NOT NULL,            -- 税制適格特約の有無
    pension_payment_years INTEGER NOT NULL DEFAULT 10,  -- 年金受取年数（例：10年分割など）

    -- 計算結果
    contract_date DATE NOT NULL,                       -- 契約開始日
    contract_interest_rate NUMERIC(5,2) NOT NULL,      -- 契約利率
    total_paid_amount INTEGER NOT NULL,                -- 総支払額
    pension_start_age INTEGER NOT NULL,                -- 年金開始年齢
    annual_tax_deduction INTEGER NOT NULL,             -- 年間控除額

    -- 商品連携用コード
    plan_code VARCHAR NOT NULL                         -- 商品コード
);

-- ============================================================================
-- テーブルJOIN: quote JOIN quote_details
-- ============================================================================

SELECT
  q.quote_id,
  q.user_id,
  q.quote_state,
  q.created_at AS quote_created_at,
  q.updated_at AS quote_updated_at,
  q.created_by,
  q.updated_by,

  -- quote_details側
  d.birth_date,
  d.gender,
  d.monthly_premium,
  d.payment_period_years,
  d.tax_deduction_enabled,
  d.pension_payment_years,
  d.contract_date,
  d.contract_interest_rate,
  d.total_paid_amount,
  d.pension_start_age,
  d.annual_tax_deduction,
  d.plan_code

FROM
  quotes q
JOIN
  quote_details d ON q.quote_id = d.quote_id

ORDER BY
  q.created_at DESC
LIMIT 300;

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

-- ============================================================================
-- application tableお掃除
-- ============================================================================
TRUNCATE TABLE
    application_details,
    applications
RESTART IDENTITY CASCADE;


-- ============================================================================
-- テーブル: contracts（契約情報）
-- ============================================================================
CREATE TABLE contracts (
    contract_id UUID PRIMARY KEY,                      -- 契約ID
    quote_id UUID NOT NULL REFERENCES quotes(quote_id) ON DELETE CASCADE,        -- 紐づく見積もり
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE, -- 紐づく申込
    user_id UUID NOT NULL,                             -- ユーザーID（契約者）

    contract_status VARCHAR(32) NOT NULL DEFAULT 'active' CHECK (
        contract_status IN ('active', 'grace_period', 'lapsed', 'cancelled', 'expired')
    ),                                                 -- 契約ステータス

    policy_number TEXT,                                -- 保険証券番号
    contract_start_date DATE NOT NULL,                 -- 契約開始日（効力発生日）
    contract_end_date DATE NOT NULL,                   -- 契約終了日（満期または更新日）
    contract_term_years INTEGER NOT NULL,              -- 契約期間（年）
    underwriter_id UUID,                               -- 引受担当者（社内オペレーターID）
    payment_method VARCHAR NOT NULL,                   -- 支払方法（確定済）

    contracted_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,-- 契約成立日時
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 更新日時
    created_by VARCHAR(64),                            -- 作成者（オペレーターIDなど）
    updated_by VARCHAR(64)                             -- 更新者（オペレーターIDなど）
);

-- ============================================================================
-- テーブル: contract_details（契約時の契約条件および計算結果を保持）
-- ============================================================================
CREATE TABLE contract_details (
    contract_id UUID PRIMARY KEY REFERENCES contracts(contract_id) ON DELETE CASCADE, -- 契約ID（1対1）

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
    payment_method VARCHAR NOT NULL                    -- 支払方法（スナップショット）
    user_consent BOOLEAN NOT NULL,                     -- 同意の有無（重要事項説明への同意）
    identity_verified BOOLEAN NOT NULL                 -- 本人確認完了フラグ
);