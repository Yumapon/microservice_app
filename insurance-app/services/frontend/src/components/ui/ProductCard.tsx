/** @jsxImportSource @emotion/react */
import styled from '@emotion/styled'

type Props = {
  title: string
  subtitle: string
  icon: string
  features: string[]
  recommended?: boolean
}

const Card = styled.article`
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid #e0e0e0;
  border-radius: ${({ theme }) => theme.radius.lg};
  padding: 1.5rem;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  position: relative;
  width: 260px;
  transition: 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.1);
  }
`

const Ribbon = styled.div`
  position: absolute;
  top: 0;
  right: 0;
  background: ${({ theme }) => theme.colors.accent};
  color: white;
  padding: 0.4rem 0.8rem;
  font-size: 0.7rem;
  font-weight: bold;
  border-bottom-left-radius: 8px;
`

const Image = styled.img`
  width: 60px;
  height: 60px;
  object-fit: contain;
  margin: 0 auto 1rem;
`

const Title = styled.h3`
  font-size: ${({ theme }) => theme.fontSize.lg};
  text-align: center;
  color: ${({ theme }) => theme.colors.primaryDark};
`

const Subtitle = styled.p`
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.muted};
  text-align: center;
  margin: 0.5rem 0 1rem;
`

const FeatureList = styled.ul`
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  justify-content: center;
  padding: 0;
  margin: 0 0 1rem;
  font-size: 0.75rem;

  li {
    background: #e0f7f5;
    border-radius: 999px;
    padding: 0.3rem 0.6rem;
    border: 1px solid #0f766e40;
    color: #0f766e;
  }
`

const Actions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: auto;

  button {
    flex: 1;
    padding: 0.5rem;
    font-size: 0.85rem;
    border-radius: 999px;
    border: none;
    background: ${({ theme }) => theme.colors.primary};
    color: white;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: ${({ theme }) => theme.colors.primaryDark};
    }
  }
`

export const ProductCard = ({ title, subtitle, icon, features, recommended }: Props) => {
  return (
    <Card>
      {recommended && <Ribbon>おすすめ</Ribbon>}
      <Image src={icon} alt={`${title}ロゴ`} />
      <Title>{title}</Title>
      <Subtitle>{subtitle}</Subtitle>
      <FeatureList>
        {features.map((f, idx) => <li key={idx}>{f}</li>)}
      </FeatureList>
      <Actions>
        <button>🔍 詳細</button>
        <button>🧮 見積</button>
      </Actions>
    </Card>
  )
}