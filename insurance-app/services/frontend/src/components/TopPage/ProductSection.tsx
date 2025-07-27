/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { useRef, useEffect, useState } from 'react'
import { FaExternalLinkAlt } from 'react-icons/fa'
import { Link } from 'react-router-dom'

const mockProducts = [
  {
    id: 'pension',
    name: '個人年金保険',
    description: '将来に備える安心の年金プラン。税制優遇も魅力。',
    icon: '/images/個人年金保険.png',
    link: '/detail/pension',
  },
  {
    id: 'education',
    name: '学資保険',
    description: '子供の未来に備える保険。コツコツ貯めましょう',
    icon: '/images/学資保険.png',
    link: '/detail/education',
  },
  {
    id: 'work',
    name: '就業不能保険',
    description: '万が一働けなくなった時のサポートに。',
    icon: '/images/就業不能保険.png',
    link: '/under-construction',
  },
  {
    id: 'cancer',
    name: 'がん保険',
    description: 'がん治療に特化した手厚いサポート。',
    icon: '/images/がん保険.png',
    link: '/under-construction',
  },
  {
    id: 'medical',
    name: '医療保険',
    description: '入院・手術を幅広くカバーする基本の保険。',
    icon: '/images/医療保険.png',
    link: '/under-construction',
  },
]

export const ProductSection = () => {
  const theme = useTheme()
  const scrollRef = useRef<HTMLDivElement>(null)
  const [scrollRatio, setScrollRatio] = useState(0)

  const updateScrollState = () => {
    const el = scrollRef.current
    if (!el) return
    const maxScrollLeft = el.scrollWidth - el.clientWidth
    const current = el.scrollLeft
    setScrollRatio(maxScrollLeft === 0 ? 0 : current / maxScrollLeft)
  }

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    updateScrollState()
    el.addEventListener('scroll', updateScrollState)
    window.addEventListener('resize', updateScrollState)
    return () => {
      el.removeEventListener('scroll', updateScrollState)
      window.removeEventListener('resize', updateScrollState)
    }
  }, [])

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>保険商品一覧</h2>

      <div css={scrollWrapperStyle}>
        <div ref={scrollRef} css={productGrid}>
          {mockProducts.map((product) => (
            <div key={product.id} css={cardStyle(theme)}>
              <img src={product.icon} alt={product.name} css={iconStyle} />
              <h3 css={productTitle}>{product.name}</h3>
              <p css={productDesc}>{product.description}</p>
              <Link to={product.link} css={buttonStyle}>
                詳細を見る <FaExternalLinkAlt />
              </Link>
            </div>
          ))}
        </div>

        <div css={indicatorContainer(scrollRatio)}>
          <div css={indicator(scrollRatio)} />
        </div>
      </div>
    </section>
  )
}

// ----------------------------
// Emotion スタイル定義
// ----------------------------
const sectionStyle = css`
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 6rem 2rem;

  @media (max-width: 768px) {
    padding: 3rem 1rem;
  }
`

const titleStyle = css`
  font-size: 2rem;
  text-align: center;
  margin-bottom: 3rem;
  font-weight: 700;
`

const productGrid = css`
  display: flex;
  flex-direction: row;
  gap: 1.5rem;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x mandatory;
  padding-bottom: 1rem;
  position: relative;

  &::-webkit-scrollbar {
    display: none;
  }
  scrollbar-width: none;

  @media (max-width: 768px) {
    gap: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
  }
`

const cardStyle = (theme: any) => css`
  flex: 0 0 280px;
  scroll-snap-align: start;
  background-color: ${theme.colors.tile};
  border-radius: ${theme.radius.lg};
  padding: 2rem;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  display: flex;
  flex-direction: column;
  align-items: center;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  }

  @media (max-width: 480px) {
    flex: 0 0 85%;
    padding: 1.5rem;
  }
`

const iconStyle = css`
  width: 96px;
  height: 96px;
  margin-bottom: 1.25rem;
  object-fit: contain;
`

const productTitle = css`
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
`

const productDesc = css`
  font-size: 0.95rem;
  color: #555;
  margin-bottom: 1.5rem;
  line-height: 1.6;
  text-align: left;
  hyphens: auto;
  overflow-wrap: break-word;
`

const buttonStyle = css`
  padding: 0.5rem 1.25rem;
  background-color: #0070f3;
  color: white;
  border: none;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #005fc1;
  }
`

const scrollWrapperStyle = css`
  position: relative;
`

const indicatorContainer = (scrollRatio: number) => css`
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 100%;
  height: 4px;
  background: #e0f2e9;
  border-radius: 2px;
  overflow: hidden;
  pointer-events: none;

  &::before,
  &::after {
    content: '';
    position: absolute;
    top: 0;
    width: 24px;
    height: 100%;
    z-index: 1;
  }

  &::before {
    left: 0;
    background: linear-gradient(to right, #f1f8f4, transparent);
    opacity: ${scrollRatio > 0 ? 1 : 0};
    transition: opacity 0.2s ease;
  }

  &::after {
    right: 0;
    background: linear-gradient(to left, #f1f8f4, transparent);
    opacity: ${scrollRatio < 0.999 ? 1 : 0};
    transition: opacity 0.2s ease;
  }
`

const indicator = (ratio: number) => css`
  height: 100%;
  width: ${ratio * 100}%;
  background: #4caf50;
  transition: width 0.1s ease;
`