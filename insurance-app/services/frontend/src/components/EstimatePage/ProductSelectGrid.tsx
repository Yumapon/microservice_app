/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { FaChevronRight } from 'react-icons/fa'

type Product = {
  id: string
  name: string
  icon: string
  description: string
}

type Props = {
  selectedId: string | null
  onSelect: (id: string) => void
}

const products: Product[] = [
  {
    id: 'pension',
    name: '個人年金保険',
    description: '将来に備える安心の年金プラン。税制優遇も魅力。',
    icon: '/images/個人年金保険.png',
  },
  {
    id: 'education',
    name: '学資保険',
    description: '子供の未来に備える保険。コツコツ貯めましょう',
    icon: '/images/学資保険.png',
  },
  {
    id: 'work',
    name: '就業不能保険',
    description: '万が一働けなくなった時のサポートに。',
    icon: '/images/就業不能保険.png',
  },
  {
    id: 'cancer',
    name: 'がん保険',
    description: 'がん治療に特化した手厚いサポート。',
    icon: '/images/がん保険.png',
  },
  {
    id: 'medical',
    name: '医療保険',
    description: '入院・手術を幅広くカバーする基本の保険。',
    icon: '/images/医療保険.png',
  },
]

export const ProductSelectGrid = ({ selectedId, onSelect }: Props) => {
  return (
    <div css={gridContainer}>
      {products.map((product) => (
        <div
          key={product.id}
          css={card(selectedId === product.id)}
          onClick={() => onSelect(product.id)}
        >
          <img src={product.icon} alt={product.name} css={iconStyle} />
          <h3 css={title}>{product.name}</h3>
          <p css={desc}>{product.description}</p>
          <div css={selectHint}>
            詳細入力へ <FaChevronRight />
          </div>
        </div>
      ))}
    </div>
  )
}

// ----------------------------
// Styles
// ----------------------------
const gridContainer = css`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
  margin-bottom: 2.5rem;
`

const card = (isSelected: boolean) => css`
  background: white;
  border: 2px solid ${isSelected ? '#0ea5e9' : '#eee'};
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  box-shadow: ${isSelected ? '0 0 0 3px rgba(14,165,233,0.2)' : '0 1px 4px rgba(0,0,0,0.05)'};
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`

const iconStyle = css`
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 1rem;
`

const title = css`
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
`

const desc = css`
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 1rem;
`

const selectHint = css`
  font-size: 0.85rem;
  color: #0ea5e9;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.25rem;
  font-weight: 600;
`