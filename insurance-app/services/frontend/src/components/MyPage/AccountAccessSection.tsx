/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useNavigate } from 'react-router-dom'

const AccountAccessSection = () => {
  const navigate = useNavigate()

  return (
    <div css={sectionStyle}>
      <div>
        <p css={labelStyle}>ご本人情報</p>
        <p css={descriptionStyle}>登録情報の確認・変更はこちら</p>
      </div>
      <button css={buttonStyle} onClick={() => navigate('/mypage/account')}>
        表示する
      </button>
    </div>
  )
}

export default AccountAccessSection

// ----------------------------
// CSS
// ----------------------------
const sectionStyle = css`
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`

const labelStyle = css`
  font-size: 1rem;
  font-weight: bold;
`

const descriptionStyle = css`
  font-size: 0.85rem;
  color: #475569;
  margin-top: 0.2rem;
`

const buttonStyle = css`
  background-color: #0ea5e9;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #0284c7;
  }
`