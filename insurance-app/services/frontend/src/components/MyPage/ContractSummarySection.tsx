/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import PensionChart from '@/components/ui/PensionChart'

type Contract = {
  id: string
  planName: string
  contractType: 'saving' | 'term'
  monthlyPremium: number
  totalPaid: number
  currentValue?: number
  totalReturned?: number
  coverage?: string
}

const mockContracts: Contract[] = [
  {
    id: '1',
    planName: '個人年金保険',
    contractType: 'saving',
    monthlyPremium: 10000,
    totalPaid: 120000,
    currentValue: 140000,
  },
  {
    id: '2',
    planName: '就業不能保険',
    contractType: 'term',
    monthlyPremium: 2000,
    totalPaid: 24000,
    totalReturned: 0,
    coverage: '月額10万円 × 最大2年',
  },
]

const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`

const ContractSummarySection = () => {
  const [contracts, setContracts] = useState<Contract[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    setContracts(mockContracts)
  }, [])

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>ご契約中の保険</h2>

      {contracts.length === 0 ? (
        <div css={ctaBox}>
          <p>まだ契約中の保険はありません。</p>
          <p>まずは保険診断・見積もりからはじめましょう。</p>
          <button css={ctaButton}>見積もりをはじめる</button>
        </div>
      ) : (
        <div css={cardContainer}>
          {contracts.map((contract) => {
            const { contractType, totalPaid, currentValue, totalReturned } = contract
            const futureEstimate = currentValue ? Math.round(currentValue * 1.15) : null

            return (
              <div key={contract.id} css={cardStyle(contractType)} onClick={() => navigate(`/mypage/contracts/${contract.id}`)}>
                <div css={badge(contractType)}>{contractType === 'saving' ? '貯蓄型' : '保障型'}</div>
                <h3 css={planTitle}>{contract.planName}</h3>
                <p>月額保険料：{contract.monthlyPremium.toLocaleString()}円</p>
                <p>払込総額：{totalPaid.toLocaleString()}円</p>

                {contractType === 'saving' && currentValue !== undefined && (
                  <>
                    <p>現在の貯蓄額：{currentValue.toLocaleString()}円</p>
                    <PensionChart totalPaid={totalPaid} currentValue={currentValue} />
                    <p css={highlightText}>返戻率：{formatPercent(currentValue / totalPaid)}</p>
                    <p css={subduedText}>将来見込み額（15%成長想定）：{futureEstimate?.toLocaleString()}円</p>
                  </>
                )}

                {contractType === 'term' && (
                  <>
                    <p>保障内容：{contract.coverage}</p>
                    <p>支払済保険金：{(totalReturned ?? 0).toLocaleString()}円</p>
                    <div css={termBarContainer}>
                      <div css={termBar(totalReturned ?? 0, totalPaid)} />
                    </div>
                    <p css={subduedText}>支払総額に対する受け取り割合：{formatPercent((totalReturned ?? 0) / totalPaid)}</p>
                    <p css={infoText}>いざという時の生活保障として備える保険です。</p>
                  </>
                )}
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}

export default ContractSummarySection

// ----------------------------
// CSS
// ----------------------------
const sectionStyle = css`
  padding: 1rem 0;
`

const titleStyle = css`
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
`

const cardContainer = css`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
`

const cardStyle = (type: 'saving' | 'term') => css`
  position: relative;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background: ${type === 'saving' ? '#f0f9ff' : '#fff7ed'};
  cursor: pointer;
  transition: box-shadow 0.2s ease, transform 0.1s ease, border-color 0.2s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
    border-color: ${type === 'saving' ? '#0ea5e9' : '#f97316'};
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }
`

const badge = (type: 'saving' | 'term') => css`
  position: absolute;
  top: 1rem;
  right: 1rem;
  background-color: ${type === 'saving' ? '#0ea5e9' : '#f97316'};
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
`

const planTitle = css`
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
`

const highlightText = css`
  font-weight: bold;
  margin-top: 0.5rem;
  color: #0ea5e9;
`

const subduedText = css`
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.3rem;
`

const infoText = css`
  font-size: 0.85rem;
  color: #4b5563;
  margin-top: 0.8rem;
`

const termBarContainer = css`
  margin-top: 0.5rem;
  background: #eee;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
`

const termBar = (value: number, total: number) => css`
  width: ${Math.min((value / total) * 100, 100)}%;
  background-color: #f97316;
  height: 100%;
  transition: width 0.5s ease;
`

const ctaBox = css`
  padding: 1rem;
  background: #fefce8;
  border-radius: 8px;
  text-align: center;
`

const ctaButton = css`
  margin-top: 0.5rem;
  background: #facc15;
  border: none;
  border-radius: 4px;
  padding: 0.6rem 1.2rem;
  font-weight: bold;
  cursor: pointer;
`