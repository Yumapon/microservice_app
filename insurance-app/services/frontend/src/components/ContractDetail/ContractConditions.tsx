/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaClipboardList } from 'react-icons/fa'

export const ContractConditions = () => {
  const theme = useTheme()

  // モックデータ
  const contractDetails = {
    birthDate: '1990-02-01',
    gender: 'male',
    monthlyPremium: 12000,
    paymentPeriodYears: 20,
    taxDeductionEnabled: true,
    contractInterestRate: 1.25,
    totalPaidAmount: 2880000,
    pensionStartAge: 65,
    annualTaxDeduction: 40000,
    userConsent: true,
    identityVerified: true,
  }

  return (
    <section css={sectionStyle}>
      <h2 css={sectionTitle(theme)}>
        <FaClipboardList style={{ marginRight: '0.5rem' }} />
        契約条件・計算結果
      </h2>

      <div css={gridStyle}>
        <Item label="生年月日" value={contractDetails.birthDate} />
        <Item label="性別" value={genderMap[contractDetails.gender]} />
        <Item label="月額保険料" value={`¥${contractDetails.monthlyPremium.toLocaleString()}`} />
        <Item label="支払期間" value={`${contractDetails.paymentPeriodYears}年`} />
        <Item
          label="税制適格特約"
          value={contractDetails.taxDeductionEnabled ? 'あり' : 'なし'}
          highlight={contractDetails.taxDeductionEnabled}
        />
        <Item label="契約利率" value={`${contractDetails.contractInterestRate.toFixed(2)}%`} />
        <Item
          label="総支払額"
          value={`¥${contractDetails.totalPaidAmount.toLocaleString()}`}
        />
        <Item label="年金開始年齢" value={`${contractDetails.pensionStartAge}歳`} />
        <Item
          label="年間控除額"
          value={`¥${contractDetails.annualTaxDeduction.toLocaleString()}`}
        />
        <Item
          label="重要事項への同意"
          value={contractDetails.userConsent ? '同意済' : '未同意'}
          highlight={contractDetails.userConsent}
        />
        <Item
          label="本人確認"
          value={contractDetails.identityVerified ? '確認済' : '未確認'}
          highlight={contractDetails.identityVerified}
        />
      </div>
    </section>
  )
}

// ----------------------------
// 共通コンポーネント
// ----------------------------
const Item = ({
  label,
  value,
  highlight = false,
}: {
  label: string
  value: string
  highlight?: boolean
}) => (
  <div css={itemStyle}>
    <label>{label}</label>
    <span css={highlight ? highlightValue : valueStyle}>{value}</span>
  </div>
)

const genderMap: { [key: string]: string } = {
  male: '男性',
  female: '女性',
  other: 'その他',
}

// ----------------------------
// Emotion CSS
// ----------------------------
const sectionStyle = css`
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
`

const sectionTitle = (theme: any) => css`
  font-size: 1.3rem;
  font-weight: 700;
  color: ${theme.colors.primary};
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
`

const gridStyle = css`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
`

const itemStyle = css`
  display: flex;
  flex-direction: column;

  label {
    font-size: 0.85rem;
    color: #777;
    margin-bottom: 0.25rem;
  }
`

const valueStyle = css`
  font-size: 1rem;
  font-weight: 600;
  color: #333;
`

const highlightValue = css`
  font-size: 1rem;
  font-weight: 700;
  color: #2e7d32; /* 緑系で強調 */
`