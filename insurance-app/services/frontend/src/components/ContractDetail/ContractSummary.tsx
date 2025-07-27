/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaFileContract } from 'react-icons/fa'

export const ContractSummary = () => {
  const theme = useTheme()

  // モックデータ
  const contract = {
    contractId: 'abcd-1234',
    status: 'active',
    policyNumber: 'PN-2025-0001',
    startDate: '2025-04-01',
    endDate: '2045-03-31',
    termYears: 20,
    underwriter: 'オペレーター太郎',
    paymentMethod: 'クレジットカード',
  }

  return (
    <section css={sectionStyle}>
      <h2 css={sectionTitle(theme)}>
        <FaFileContract style={{ marginRight: '0.5rem' }} />
        契約概要
      </h2>
      <div css={gridStyle}>
        <div><label>契約ID</label><span>{contract.contractId}</span></div>
        <div><label>ステータス</label><span>{contract.status}</span></div>
        <div><label>証券番号</label><span>{contract.policyNumber}</span></div>
        <div><label>契約期間</label><span>{contract.termYears}年</span></div>
        <div><label>開始日</label><span>{contract.startDate}</span></div>
        <div><label>終了日</label><span>{contract.endDate}</span></div>
        <div><label>引受担当者</label><span>{contract.underwriter}</span></div>
        <div><label>支払方法</label><span>{contract.paymentMethod}</span></div>
      </div>
    </section>
  )
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
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;

  div {
    display: flex;
    flex-direction: column;

    label {
      font-size: 0.85rem;
      color: #777;
      margin-bottom: 0.25rem;
    }

    span {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
    }
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`