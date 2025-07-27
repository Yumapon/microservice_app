/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaGraduationCap, FaCalendarCheck, FaCoins, FaMobileAlt } from 'react-icons/fa'

export const EducationFeatures = () => {
  const theme = useTheme()

  const features = [
    {
      icon: <FaGraduationCap />,
      title: '教育資金を計画的に準備',
      description: '進学時に必要な資金を、計画的に積み立てることができます。',
    },
    {
      icon: <FaCalendarCheck />,
      title: '満期時に確実な給付',
      description: 'お子さまの進学にあわせて給付金が支払われます。',
    },
    {
      icon: <FaCoins />,
      title: '保護者に万一があっても安心',
      description: '契約者が死亡・高度障害となった場合も、保険料の払込が免除され、保障が継続されます。',
    },
    {
      icon: <FaMobileAlt />,
      title: 'スマホで完結',
      description: '見積もりから申し込みまで、すべてオンラインで完結可能です。',
    },
  ]

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>学資保険の特徴</h2>
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