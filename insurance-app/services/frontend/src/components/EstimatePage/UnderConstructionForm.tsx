/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { FaHardHat, FaTools } from 'react-icons/fa'

export const UnderConstructionForm = () => {
  return (
    <div css={wrapper}>
      <div css={iconBox}>
        <FaHardHat css={iconStyle} />
        <FaTools css={animatedIcon} />
      </div>
      <h3>この保険の見積もりフォームは現在準備中です。</h3>
      <p>まもなく公開予定です。しばらくお待ちください。</p>
    </div>
  )
}

const wrapper = css`
  background: #fff7e6;
  border: 1px solid #ffd700;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  margin-top: 2rem;
`

const iconBox = css`
  font-size: 2rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
`

const iconStyle = css`
  color: #ff9800;
`

const animatedIcon = css`
  color: #ff9800;
  animation: rotateWrench 2s infinite ease-in-out;

  @keyframes rotateWrench {
    0% { transform: rotate(0deg); }
    50% { transform: rotate(20deg); }
    100% { transform: rotate(0deg); }
  }
`