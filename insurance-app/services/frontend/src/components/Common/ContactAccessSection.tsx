/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useNavigate } from 'react-router-dom'

const ContactAccessSection = () => {
  const navigate = useNavigate()

  return (
    <div css={sectionStyle}>
      <div>
        <p css={labelStyle}>お問い合わせ</p>
        <p css={descriptionStyle}>ご不明点はお気軽にお問い合わせください</p>
      </div>
      <button css={buttonStyle} onClick={() => navigate('/contact')}>
        開く
      </button>
    </div>
  )
}

export default ContactAccessSection

// ----------------------------
// CSS
// ----------------------------
const sectionStyle = css`
  background: #fefce8;
  border: 1px solid #fde68a;
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
  color: #92400e;
  margin-top: 0.2rem;
`

const buttonStyle = css`
  background-color: #facc15;
  color: #1f2937;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #eab308;
  }
`