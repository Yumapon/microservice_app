/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaPiggyBank, FaShieldAlt, FaChartLine, FaMobileAlt } from 'react-icons/fa'

export const PensionFeatures = () => {
  const theme = useTheme()

  const features = [
    {
      icon: <FaPiggyBank />,
      title: '積立型で着実に貯蓄',
      description: '毎月コツコツ積み立てて、老後に備える安定した資産形成をサポートします。',
    },
    {
      icon: <FaShieldAlt />,
      title: '最低保証付きで安心',
      description: '契約時に利率が確定。万一の金利低下にも備えられる最低保証を完備。',
    },
    {
      icon: <FaChartLine />,
      title: '税制優遇あり',
      description: '個人年金保険料控除の対象。税金面でもメリットがあります。',
    },
    {
      icon: <FaMobileAlt />,
      title: 'ネットで簡単申込',
      description: 'スマホやPCから手軽に申込完了。書類提出も不要でスムーズ。',
    },
  ]

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>個人年金保険の特徴</h2>
      <div css={gridStyle}>
        {features.map((feature, index) => (
          <div key={index} css={cardStyle(theme)}>
            <div css={iconStyle(theme)}>{feature.icon}</div>
            <h3 css={featureTitle}>{feature.title}</h3>
            <p css={featureDesc}>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

const sectionStyle = css`
  padding: 4rem 1.5rem;
  background-color: #f7fafc;
`

const titleStyle = css`
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 3rem;
  color: #0077b6;

  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`

const gridStyle = css`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`

const cardStyle = (theme: any) => css`
  background-color: white;
  border-radius: ${theme.radius.md};
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  text-align: center;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-4px);
  }
`

const iconStyle = (theme: any) => css`
  font-size: 2rem;
  color: ${theme.colors.primary};
  margin-bottom: 1rem;
`

const featureTitle = css`
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
`

const featureDesc = css`
  font-size: 0.95rem;
  color: #555;
  line-height: 1.6;
`