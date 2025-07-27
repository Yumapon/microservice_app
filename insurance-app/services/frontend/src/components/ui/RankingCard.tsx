import { css } from '@emotion/react'

type Props = {
  rank: number
  name: string
  description: string
}

export const RankingCard = ({ rank, name, description }: Props) => {
  return (
    <div css={cardStyle}>
      <div css={rankStyle}>{rank}位</div>
      <h3 css={nameStyle}>{name}</h3>
      <p css={descStyle}>{description}</p>
    </div>
  )
}

const cardStyle = (theme: any) => css`
  background-color: ${theme.colors.background};
  border-radius: ${theme.radius.md};
  padding: 24px;
  width: 220px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`

const rankStyle = (theme: any) => css`
  font-size: ${theme.fontSize.base};
  color: ${theme.colors.primaryDark};
  margin-bottom: 8px;
`

const nameStyle = (theme: any) => css`
  font-size: ${theme.fontSize.lg};
  margin-bottom: 8px;
`

const descStyle = (theme: any) => css`
  font-size: ${theme.fontSize.sm};
  color: ${theme.colors.muted};
`