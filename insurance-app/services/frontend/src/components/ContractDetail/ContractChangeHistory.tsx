/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'

const mockChanges = [
  {
    date: '2024-10-15',
    title: '支払方法の変更',
    detail: 'クレジットカード → 口座振替',
  },
  {
    date: '2023-07-01',
    title: '保険金受取人の変更',
    detail: '受取人を「佐々木花子」に変更',
  },
]

export const ContractChangeHistory = () => {
  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>契約変更履歴</h2>
      <ul css={listStyle}>
        {mockChanges.map((item, idx) => (
          <li key={idx} css={itemStyle}>
            <span css={dateStyle}>{item.date}</span>
            <div>
              <p css={itemTitle}>{item.title}</p>
              <p css={itemDetail}>{item.detail}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

// ----------------------------
// CSS
// ----------------------------

const sectionStyle = css`
  margin: 2.5rem 0;
`

const titleStyle = css`
  font-size: 1.4rem;
  font-weight: bold;
  margin-bottom: 1rem;
`

const listStyle = css`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
`

const itemStyle = css`
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-left: 4px solid #0ea5e9;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
`

const dateStyle = css`
  font-weight: bold;
  color: #0ea5e9;
  min-width: 90px;
`

const itemTitle = css`
  font-weight: 600;
`

const itemDetail = css`
  font-size: 0.9rem;
  color: #555;
`