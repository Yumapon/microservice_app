/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaSearch, FaCalculator, FaPenFancy, FaFileAlt } from 'react-icons/fa'

const steps = [
  { icon: <FaSearch />, title: '保険商品を探す', description: 'あなたにぴったりの保険商品を一覧から選べます' },
  { icon: <FaCalculator />, title: '見積もりを取得', description: '簡単な入力で、保険料と保障内容をシミュレーション' },
  { icon: <FaPenFancy />, title: 'オンライン申込', description: 'スマホやPCで申込完了！書類提出もオンラインで' },
  { icon: <FaFileAlt />, title: '契約・確認', description: '契約後はいつでもアプリから内容確認できます' },
]

export const FlowSection = () => {
  const theme = useTheme()

  return (
    <div>
      <h2 css={titleStyle}>ご利用の流れ</h2>
      <div css={stepListStyle}>
        {steps.map((step, index) => (
          <div key={index} css={stepStyle(theme)}>
            <div css={iconStyle(theme)}>{step.icon}</div>
            <h3>{step.title}</h3>
            <p>{step.description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

// ----------------------------
// Style Definitions
// ----------------------------

const titleStyle = css`
  font-size: 2rem;
  text-align: center;
  margin-bottom: 3rem;
  font-weight: 700;
`

const stepStyle = (theme: any) => css`
  flex: 1 1 220px;
  max-width: 280px;
  background: white;
  border-radius: ${theme.radius.md};
  padding: 24px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
  text-align: center;

  h3 {
    font-size: 18px;
    margin-top: 16px;
    color: ${theme.colors.text};
  }

  p {
    font-size: 14px;
    color: ${theme.colors.subText};
    margin-top: 8px;
  }

  @media (max-width: 768px) {
    padding: 16px 12px;

    h3 {
      font-size: 15px;
      margin-top: 12px;
    }

    p {
      font-size: 12px;
      margin-top: 6px;
    }
  }
`

const iconStyle = (theme: any) => css`
  font-size: 32px;
  color: ${theme.colors.primary};
  margin-bottom: 8px;

  @media (max-width: 768px) {
    font-size: 24px;
    margin-bottom: 4px;
  }
`

const stepListStyle = css`
  display: flex;
  justify-content: center;
  gap: 40px;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    gap: 16px;
  }
`