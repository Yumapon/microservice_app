/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'

export const ContactHero = () => {
  return (
    <section css={heroSection}>
      <div css={inner}>
        <h1 css={title}>お問い合わせ</h1>
        <p css={description}>
          商品に関するご質問やご不明点がございましたら、お気軽にご連絡ください。<br />
          担当者より折り返しご連絡いたします。
        </p>
      </div>
    </section>
  )
}

const heroSection = css`
  padding: 4rem 1.5rem;
  background-color: #f5fbf9;

  @media (max-width: 768px) {
    padding: 3rem 1rem;
  }
`

const inner = css`
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
`

const title = css`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;

  @media (max-width: 768px) {
    font-size: 2rem;
  }
`

const description = css`
  font-size: 1rem;
  color: #555;
  line-height: 1.8;
`