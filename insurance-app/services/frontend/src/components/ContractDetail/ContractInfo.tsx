/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { format } from 'date-fns'

// モックデータ（仮置き）
const mockContract = {
  contractId: 'abcd-1234-efgh-5678',
  policyNumber: 'PN-20250717-001',
  status: 'active',
  startDate: '2023-10-01',
  endDate: '2043-10-01',
  termYears: 20,
  paymentMethod: 'クレジットカード',
}

const statusLabel = {
  active: '有効',
  grace_period: '猶予期間',
  lapsed: '失効',
  cancelled: '解約済',
  expired: '満期終了',
} as const

const statusColor = {
  active: '#4caf50',
  grace_period: '#ff9800',
  lapsed: '#f44336',
  cancelled: '#9e9e9e',
  expired: '#607d8b',
} as const

export const ContractInfo = () => {
  const {
    contractId,
    policyNumber,
    status,
    startDate,
    endDate,
    termYears,
    paymentMethod,
  } = mockContract

  // 型アサーションでstatusをkeyof statusLabelに変換
  const typedStatus = status as keyof typeof statusLabel

  return (
    <section css={infoSection}>
      <h2 css={sectionTitle}>契約情報</h2>
      <div css={infoGrid}>
        <div>
          <span css={label}>契約ID</span>
          <span css={value}>{contractId}</span>
        </div>
        <div>
          <span css={label}>証券番号</span>
          <span css={value}>{policyNumber}</span>
        </div>
        <div>
          <span css={label}>契約ステータス</span>
          <span css={[value, statusBadge(typedStatus)]}>{statusLabel[typedStatus]}</span>
        </div>
        <div>
          <span css={label}>契約開始日</span>
          <span css={value}>{format(new Date(startDate), 'yyyy年MM月dd日')}</span>
        </div>
        <div>
          <span css={label}>契約終了日</span>
          <span css={value}>{format(new Date(endDate), 'yyyy年MM月dd日')}</span>
        </div>
        <div>
          <span css={label}>契約期間</span>
          <span css={value}>{termYears} 年</span>
        </div>
        <div>
          <span css={label}>支払方法</span>
          <span css={value}>{paymentMethod}</span>
        </div>
      </div>
    </section>
  )
}

// ----------------------------
// Emotion CSS
// ----------------------------

const infoSection = css`
  margin-bottom: 3rem;
`

const sectionTitle = css`
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
`

const infoGrid = css`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`

const label = css`
  display: block;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.25rem;
`

const value = css`
  font-size: 1rem;
  font-weight: 600;
  color: #222;
`

const statusBadge = (status: keyof typeof statusColor) => css`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background-color: ${statusColor[status]};
  color: white;
  font-size: 0.85rem;
`