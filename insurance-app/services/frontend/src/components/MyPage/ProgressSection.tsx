/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'

const steps = [
  {
    title: 'Step 1. 見積もり',
    description: '保険商品の内容を確認し、ご希望の条件で保険料や受取額のシミュレーションを行います。',
  },
  {
    title: 'Step 2. 申込',
    description: '見積もり結果をもとに、必要事項を入力して保険申込を行います。本人確認が必要です。',
  },
  {
    title: 'Step 3. 契約完了',
    description: '審査・確認が完了後、契約内容が確定し、マイページからいつでもご確認いただけます。',
  },
]

const ProgressSection = () => {
  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>ご契約までの流れ</h2>
      <div css={stepWrapper}>
        {steps.map((step, index) => (
          <div key={index} css={stepCard}>
            <div css={stepCircle}>{index + 1}</div>
            <h3 css={stepTitle}>{step.title}</h3>
            <p css={stepDesc}>{step.description}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

export default ProgressSection

const sectionStyle = css`
  padding: 2rem 0;
  border-top: 1px solid #ddd;
`

const titleStyle = css`
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 2rem;
`

const stepWrapper = css`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  @media (min-width: 768px) {
    flex-direction: row;
    justify-content: space-between;
  }
`

const stepCard = css`
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  flex: 1;
`

const stepCircle = css`
  width: 36px;
  height: 36px;
  margin: 0 auto 0.8rem;
  border-radius: 50%;
  background-color: #0ea5e9;
  color: white;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
`

const stepTitle = css`
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
`

const stepDesc = css`
  font-size: 0.9rem;
  color: #555;
`