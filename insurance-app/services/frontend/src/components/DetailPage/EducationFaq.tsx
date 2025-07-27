/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { useState } from 'react'
import { FaChevronDown, FaChevronUp } from 'react-icons/fa'

const faqs = [
  {
    question: '学資保険はいつから加入できますか？',
    answer:
      '多くの学資保険はお子さまの出生直後から加入可能です。商品によっては妊娠中に申し込めるものもあります。',
  },
  {
    question: '保険料の払込はいつまでですか？',
    answer:
      '払込年数は契約時に選択でき、一般的には10歳・15歳・18歳までなど複数のプランがあります。',
  },
  {
    question: '大学入学時にまとまった資金を受け取れますか？',
    answer:
      'はい、進学時のタイミングに合わせて祝い金や満期金を一括で受け取れるプランが多くあります。',
  },
  {
    question: '契約者に万一のことがあった場合はどうなりますか？',
    answer:
      '契約者に万一のことがあった場合でも、以降の保険料が免除され、満期時に所定の保険金が支払われる保障があります（保険会社・商品により異なります）。',
  },
]

export const EducationFaq = () => {
  const theme = useTheme()
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const toggle = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle(theme)}>よくあるご質問</h2>
      <div css={faqListStyle}>
        {faqs.map((faq, index) => (
          <div key={index} css={faqItemStyle}>
            <button onClick={() => toggle(index)} css={faqButtonStyle}>
              <span>{faq.question}</span>
              {openIndex === index ? <FaChevronUp /> : <FaChevronDown />}
            </button>
            {openIndex === index && <p css={faqAnswerStyle}>{faq.answer}</p>}
          </div>
        ))}
      </div>
    </section>
  )
}

// ----------------------------
// Style Definitions
// ----------------------------

const sectionStyle = css`
  padding: 4rem 1.5rem;
  background-color: #f9fdfb;
`

const titleStyle = (theme: any) => css`
  font-size: 2rem;
  text-align: center;
  font-weight: 700;
  color: ${theme.colors.primary};
  margin-bottom: 2rem;

  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`

const faqListStyle = css`
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
`

const faqItemStyle = css`
  background: white;
  border-radius: 8px;
  border: 1px solid #ddd;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
`

const faqButtonStyle = css`
  width: 100%;
  padding: 1rem;
  background: none;
  border: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  text-align: left;

  &:hover {
    background-color: #f2f9f6;
  }

  span {
    flex: 1;
  }

  svg {
    margin-left: 0.5rem;
  }
`

const faqAnswerStyle = css`
  padding: 0 1rem 1rem;
  color: #555;
  font-size: 0.95rem;
  line-height: 1.6;
`