/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'

type RecommendedPlan = {
  id: string
  name: string
  reason: string
  estimatedMonthlyPremium: number
  tags: ('人気' | '新着' | '節税')[]
  type: 'saving' | 'term'
}

// データが空のケースで表示確認したいときは以下を空にする
const mockRecommended: RecommendedPlan[] = [
  {
    id: 'pension',
    name: '個人年金保険',
    reason: '将来の年金対策におすすめです',
    estimatedMonthlyPremium: 10000,
    tags: ['節税', '人気'],
    type: 'saving',
  },
  {
    id: 'medical',
    name: '医療保険',
    reason: '医療費の備えとして必要性が高いです',
    estimatedMonthlyPremium: 4000,
    tags: ['新着'],
    type: 'term',
  },
]

export const RecommendationSection = () => {
  const noRecommendation = mockRecommended.length === 0

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>あなたへのおすすめ保険</h2>
      <p css={diagnosedComment}>診断結果に基づくおすすめ保険を表示しています。</p>

      {noRecommendation ? (
        <div css={emptyBox}>
          <p css={emptyText}>現在おすすめできる保険はありません！</p>
          <p css={emptySubText}>すでに必要な保険に加入済みです。</p>
        </div>
      ) : (
        <div css={resultGrid}>
          {mockRecommended.map((plan) => (
            <div key={plan.id} css={cardStyle(plan.type)}>
              <div css={headerRow}>
                <h3 css={planTitle}>{plan.name}</h3>
                <div css={badgeGroup}>
                  {plan.tags.map((tag) => (
                    <span key={tag} css={badgeStyle(tag)}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              <p>{plan.reason}</p>
              <p css={highlightText}>
                おすすめ保険料：{plan.estimatedMonthlyPremium.toLocaleString()}円/月
              </p>
              <button css={buttonStyle}>見積もりへ</button>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

export default RecommendationSection

// ----------------------------
// CSS
// ----------------------------
const sectionStyle = css`
  padding: 1rem 0;
  border-top: 1px solid #ddd;
`

const titleStyle = css`
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
`

const diagnosedComment = css`
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
`

const resultGrid = css`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`

const cardStyle = (type: 'saving' | 'term') => css`
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background: ${type === 'saving' ? '#f0f9ff' : '#fff7ed'};
`

const headerRow = css`
  display: flex;
  justify-content: space-between;
  align-items: center;
`

const planTitle = css`
  font-size: 1rem;
  font-weight: bold;
`

const badgeGroup = css`
  display: flex;
  gap: 0.4rem;
`

const badgeStyle = (tag: string) => css`
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  background-color: ${
    tag === '人気' ? '#dbeafe' : tag === '新着' ? '#fef9c3' : '#dcfce7'
  };
  color: #333;
`

const highlightText = css`
  font-weight: bold;
  margin-top: 0.5rem;
  color: #0ea5e9;
`

const buttonStyle = css`
  margin-top: 1rem;
  padding: 0.5rem 1.2rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;

  &:hover {
    background: rgb(119, 194, 228);
  }
`

const emptyBox = css`
  background: #f9fafb;
  border: 1px dashed #ccc;
  padding: 2rem;
  text-align: center;
  border-radius: 8px;
`

const emptyText = css`
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
`

const emptySubText = css`
  font-size: 0.9rem;
  color: #555;
`