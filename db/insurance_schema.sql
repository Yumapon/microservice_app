
-- ============================================================================
-- テーブル: quotes（見積もりの基本情報を保持）
-- ============================================================================
CREATE TABLE quotes (
    quote_id UUID PRIMARY KEY,                         -- 見積もりID
    user_id UUID NOT NULL,                             -- ユーザーID（Keycloakのsub）
    quote_state VARCHAR(32) NOT NULL DEFAULT 'draft' CHECK (
        quote_state IN ('draft', 'confirmed', 'applied', 'cancelled', 'expired')
    ),                                                 -- ステータス（状態遷移図に基づく）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- 作成日時
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

    -- 計算結果
    contract_date DATE NOT NULL,                       -- 契約開始日
    contract_interest_rate NUMERIC(5,2) NOT NULL,      -- 契約利率
    total_paid_amount INTEGER NOT NULL,                -- 総支払額
    pension_start_age INTEGER NOT NULL,                -- 年金開始年齢
    annual_tax_deduction INTEGER NOT NULL              -- 年間控除額
);

-- ============================================================================
-- テーブル: applications（申込情報）
-- ============================================================================
CREATE TABLE applications (
    application_id UUID PRIMARY KEY,                   -- 申込ID
    quote_id UUID NOT NULL REFERENCES quotes(quote_id) ON DELETE CASCADE, -- 紐づく見積もり
    user_id UUID NOT NULL,                             -- ユーザーID

    application_status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (
        application_status IN ('pending', 'under_review', 'confirmed', 'rejected', 'cancelled')
    ),                                                 -- 申込ステータス

    user_consent BOOLEAN NOT NULL,                     -- 同意の有無
    applied_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,   -- 申込日時
    deleted_at TIMESTAMP WITHOUT TIME ZONE             -- キャンセル日時（論理削除）
);

-- ============================================================================
-- テーブル: application_snapshots（申込時の見積もり条件スナップショット）
-- ============================================================================
CREATE TABLE application_snapshots (
    application_id UUID PRIMARY KEY REFERENCES applications(application_id) ON DELETE CASCADE, -- 申込ID

    snapshot_birth_date DATE NOT NULL,                          -- 生年月日
    snapshot_gender TEXT NOT NULL CHECK (snapshot_gender IN ('male', 'female', 'other')), -- 性別
    snapshot_monthly_premium INTEGER NOT NULL,                 -- 月額保険料
    snapshot_payment_period_years INTEGER NOT NULL,            -- 支払い年数
    snapshot_tax_deduction_enabled BOOLEAN NOT NULL,           -- 税制適格特約の有無

    snapshot_contract_date DATE NOT NULL,                      -- 契約開始日
    snapshot_contract_interest_rate NUMERIC(5,2) NOT NULL,     -- 契約利率
    snapshot_total_paid_amount INTEGER NOT NULL,               -- 総支払額
    snapshot_pension_start_age INTEGER NOT NULL,               -- 年金開始年齢
    snapshot_annual_tax_deduction INTEGER NOT NULL             -- 年間控除額
);

-- ============================================================================
-- テーブル: contracts（契約情報）
-- ============================================================================
CREATE TABLE contracts (
    contract_id UUID PRIMARY KEY,                     -- 契約ID
    quote_id UUID NOT NULL REFERENCES quotes(quote_id) ON DELETE CASCADE, -- 紐づく見積もり
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE, -- 紐づく申込
    user_id UUID NOT NULL,                            -- ユーザーID

    contract_status VARCHAR(32) NOT NULL DEFAULT 'active' CHECK (
        contract_status IN ('active', 'grace_period', 'lapsed', 'cancelled', 'expired')
    ),                                                -- 契約ステータス

    user_consent BOOLEAN NOT NULL,                    -- 契約時の同意
    applied_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,  -- 契約成立日
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    -- レコード作成日時
);

-- ============================================================================
-- テーブル: contract_snapshots（契約時点の見積もり条件スナップショット）
-- ============================================================================
CREATE TABLE contract_snapshots (
    contract_id UUID PRIMARY KEY REFERENCES contracts(contract_id) ON DELETE CASCADE, -- 契約ID

    birth_date DATE NOT NULL,                             -- 生年月日
    gender TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other')), -- 性別
    monthly_premium INTEGER NOT NULL,                     -- 月額保険料
    payment_period_years INTEGER NOT NULL,                -- 支払い年数
    tax_deduction_enabled BOOLEAN NOT NULL,               -- 税制適格特約の有無

    contract_date DATE NOT NULL,                          -- 契約開始日
    contract_interest_rate NUMERIC(5,2) NOT NULL,         -- 契約利率
    total_paid_amount INTEGER NOT NULL,                   -- 総支払額
    pension_start_age INTEGER NOT NULL,                   -- 年金開始年齢
    annual_tax_deduction INTEGER NOT NULL                 -- 年間控除額
);
