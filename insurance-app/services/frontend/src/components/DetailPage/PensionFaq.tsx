/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { useState } from 'react'
import { FaChevronDown, FaChevronUp } from 'react-icons/fa'

const faqs = [
  {
    question: '個人年金保険は何歳から加入できますか？',
    answer: '多くの商品では20歳から60歳まで加入可能です。ただし商品によって異なるため、詳細は各商品ページをご確認ください。',
  },
  {
    question: '途中で解約するとどうなりますか？',
    answer: '解約時には解約返戻金を受け取れますが、払込額を下回る可能性があります。ご契約時の条件をご確認ください。',
  },
  {
    question: '保険料は年末調整や確定申告で控除されますか？',
    answer: '個人年金保険料控除の対象となる場合があります。契約内容や払込方法によって異なるため、証明書をご確認ください。',
  },
  {
    question: '受け取りは一括と年金形式どちらが選べますか？',
    answer: '商品によりますが、年金形式が基本です。一括受け取り可能な商品もありますのでご確認ください。',
  },
]

export const PensionFaq = () => {
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