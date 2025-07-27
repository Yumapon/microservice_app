/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'

export const CtaSection = () => {
  return (
    <section css={containerStyle}>
      <div css={overlayStyle}>
        <h1 css={titleStyle}>ネットで簡単。見積もりから契約まで。</h1>
        <p css={subtitleStyle}>
          ネットで完結する保険サービス。
        </p>
      </div>
    </section>
  )
}

// ----------------------------
// スタイル定義
// ----------------------------
const containerStyle = css`
  width: 100%;
  height: 30vh;
  min-height: 240px;
  background-image: url('/images/hero-background.png');
  background-size: cover;
  background-position: center;
  position: relative;

  @media (max-width: 480px) {
    height: auto;
    padding: 3rem 0;
  }
`

const overlayStyle = css`
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 1.5rem;
  padding: 0 1rem;

  @media (max-width: 480px) {
    position: static;
    padding: 2rem 1rem;
  }
`

const titleStyle = css`
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.3;
  @media (max-width: 768px) {
    font-size: 2rem;
  }
`

const subtitleStyle = css`
  font-size: 1.25rem;
  max-width: 640px;
  @media (max-width: 768px) {
    font-size: 1rem;
  }
`