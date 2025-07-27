/** @jsxImportSource @emotion/react */
import { css, keyframes } from '@emotion/react'
import { FaHardHat, FaTools, FaExclamationTriangle } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'

export const UnderConstruction = () => {
  const navigate = useNavigate()

  const handleReload = () => {
    location.reload()
  }

  const handleBack = () => {
    navigate(-1)
  }

  return (
    <div css={containerStyle}>
      <div css={iconWrapper}>
        <FaHardHat css={iconStyle} />
        <FaTools css={[iconStyle, wrenchAnimation]} />
      </div>
      <h1 css={titleStyle}>ただいま工事中です</h1>
      <p css={messageStyle}>
        この保険ページは現在、準備中です。<br />
        安全第一で作業中ですので、今しばらくお待ちください。
      </p>
      <FaExclamationTriangle css={warningIcon} />
      <div css={barrierStyle}>
        <div />
        <div />
        <div />
        <div />
      </div>
      <div css={buttonGroupStyle}>
        <button onClick={handleBack} css={buttonStyle('#0077b6')}>前のページに戻る</button>
        <button onClick={handleReload} css={buttonStyle('#ffa500')}>再読み込み</button>
      </div>
    </div>
  )
}

// ------------------------
// Styles
// ------------------------

const containerStyle = css`
  padding: 5rem 1rem;
  background-color: #fef9ef;
  min-height: 100vh;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`

const iconWrapper = css`
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
`

const iconStyle = css`
  font-size: 3rem;
  color: #ffa500;
`

const wrenchKeyframe = keyframes`
  0% { transform: rotate(0deg); }
  50% { transform: rotate(15deg); }
  100% { transform: rotate(0deg); }
`

const wrenchAnimation = css`
  animation: ${wrenchKeyframe} 2s infinite ease-in-out;
`

const titleStyle = css`
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;

  @media (max-width: 600px) {
    font-size: 1.5rem;
  }
`

const messageStyle = css`
  font-size: 1rem;
  color: #555;
  line-height: 1.6;
  max-width: 500px;
  margin-bottom: 2rem;
`

const warningIcon = css`
  font-size: 2rem;
  color: #ff6347;
  margin: 1rem 0;
`

const barrierStyle = css`
  display: flex;
  gap: 0.5rem;
  margin: 2rem 0;
  div {
    width: 40px;
    height: 20px;
    background: repeating-linear-gradient(
      45deg,
      #ffcc00,
      #ffcc00 10px,
      #000 10px,
      #000 20px
    );
    border: 1px solid #333;
  }
`

const buttonGroupStyle = css`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
`

const buttonStyle = (color: string) => css`
  padding: 0.75rem 1.5rem;
  background-color: ${color};
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    opacity: 0.85;
  }

  @media (max-width: 480px) {
    width: 100%;
  }
`