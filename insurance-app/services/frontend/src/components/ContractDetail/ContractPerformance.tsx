/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaPiggyBank, FaHeartbeat } from 'react-icons/fa'
import PensionChart from '@/components/ui/PensionChart'

type Props = {
  contractType: 'saving' | 'term'
  totalPaid: number
  currentValue?: number
  totalReturned?: number
  coverage?: string
}

export const ContractPerformance = ({
  contractType,
  totalPaid,
  currentValue,
  totalReturned,
  coverage,
}: Props) => {
  const theme = useTheme()
  const growthRate = currentValue ? currentValue / totalPaid : 0
  const payoutRate = totalReturned ? totalReturned / totalPaid : 0

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle(theme)}>
        {contractType === 'saving' ? <FaPiggyBank /> : <FaHeartbeat />}
        {contractType === 'saving' ? '貯蓄状況' : '保障内容・実績'}
      </h2>

      <div css={contentBox}>
        {contractType === 'saving' && currentValue !== undefined ? (
          <>
            <p>払込総額：{totalPaid.toLocaleString()}円</p>
            <p>現在の貯蓄額：{currentValue.toLocaleString()}円</p>
            <PensionChart totalPaid={totalPaid} currentValue={currentValue} />
            <p css={highlightText}>返戻率：{(growthRate * 100).toFixed(1)}%</p>
            <p css={noteText}>将来見込み額（+15%成長想定）：{Math.round(currentValue * 1.15).toLocaleString()}円</p>
          </>
        ) : (
          <>
            <p>保障内容：{coverage}</p>
            <p>支払済保険金：{(totalReturned ?? 0).toLocaleString()}円</p>
            <p css={highlightText}>支払総額に対する受取率：{(payoutRate * 100).toFixed(1)}%</p>
            <div css={termBarContainer}>
              <div css={termBar(payoutRate)} />
            </div>
          </>
        )}
      </div>
    </section>
  )
}

// ----------------------------
// Emotion CSS
// ----------------------------

const sectionStyle = css`
  margin: 2.5rem 0;
`

const titleStyle = (theme: any) => css`
  font-size: 1.4rem;
  font-weight: bold;
  color: ${theme.colors.primary};
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
`

const contentBox = css`
  background-color: #ffff;
  padding: 1.5rem;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 0.95rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
`

const highlightText = css`
  margin-top: 1rem;
  font-weight: bold;
  color: #0ea5e9;
`

const noteText = css`
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.3rem;
`

const termBarContainer = css`
  margin-top: 0.75rem;
  background: #e5e7eb;
  height: 12px;
  border-radius: 6px;
  overflow: hidden;
`

const termBar = (rate: number) => css`
  width: ${Math.min(rate * 100, 100)}%;
  background-color: #f97316;
  height: 100%;
  transition: width 0.5s ease;
`