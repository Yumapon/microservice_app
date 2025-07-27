/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'

export const EducationHero = () => {
  return (
    <section css={heroSection}>
      <div css={contentWrapper}>
        <div css={textBlock}>
          <h1 css={title}>お子さまの未来を支える、確かな学資保険</h1>
          <p css={description}>
            教育資金の備えを、いまから安心してはじめませんか？<br />
          </p>
          <a href="#simulation" css={ctaButton}>
            ▶ 今すぐ見積もり
          </a>
        </div>
        <div css={imageBlock}>
          <img
            src="/images/学資保険.png"
            alt="学資保険イメージ"
            css={imageStyle}
          />
        </div>
      </div>
    </section>
  )
}

const heroSection = css`
  padding: 4rem 1.5rem;
  background: linear-gradient(to right, #f0f9ff, #e0f7fa);
`

const contentWrapper = css`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
  }
`

const textBlock = css`
  flex: 1;
  min-width: 280px;
  padding: 1rem;
`

const title = css`
  font-size: 2.2rem;
  font-weight: 700;
  color: #0077b6;
  margin-bottom: 1rem;

  @media (max-width: 768px) {
    font-size: 1.8rem;
  }
`

const description = css`
  font-size: 1rem;
  color: #333;
  margin-bottom: 2rem;
  line-height: 1.6;

  @media (max-width: 768px) {
    font-size: 0.95rem;
  }
`

const ctaButton = css`
  display: inline-block;
  background-color: #0070f3;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  font-weight: bold;
  text-decoration: none;
  transition: background-color 0.3s;

  &:hover {
    background-color: #005fc1;
  }
`

const imageBlock = css`
  flex: 1;
  min-width: 280px;
  padding: 1rem;
  display: flex;
  justify-content: center;
`

const imageStyle = css`
  width: 100%;
  max-width: 320px;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
`