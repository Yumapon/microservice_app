/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { FaPhoneAlt, FaEnvelope } from 'react-icons/fa'

export const SupportInfo = () => {
  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>サポート・お問い合わせ</h2>
      <p css={descText}>ご契約内容や各種お手続きに関するお問い合わせは以下までご連絡ください。</p>
      <ul css={listStyle}>
        <li>
          <FaPhoneAlt style={{ marginRight: '0.5rem' }} />
          カスタマーサポート：0120-123-456（平日 9:00〜18:00）
        </li>
        <li>
          <FaEnvelope style={{ marginRight: '0.5rem' }} />
          メール：support@example.com
        </li>
      </ul>
    </section>
  )
}

// ----------------------------
// CSS
// ----------------------------

const sectionStyle = css`
  margin: 3rem 0;
  padding: 1.5rem;
  background: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
`

const titleStyle = css`
  font-size: 1.4rem;
  font-weight: bold;
  margin-bottom: 1rem;
`

const descText = css`
  margin-bottom: 1rem;
  font-size: 0.95rem;
`

const listStyle = css`
  list-style: none;
  padding: 0;
  font-size: 0.95rem;

  li {
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
  }
`