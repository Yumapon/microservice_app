/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { type ReactNode } from 'react'

type CardProps = {
  children: ReactNode
  style?: React.CSSProperties
}

export const Card = ({ children, style }: CardProps) => {
  return (
    <div css={cardStyle} style={style}>
      {children}
    </div>
  )
}

export const CardContent = ({ children }: { children: ReactNode }) => {
  return <div css={cardContentStyle}>{children}</div>
}

const cardStyle = css`
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  padding: 1.6rem;
  width: 100%;
  transition: box-shadow 0.2s ease-in-out;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  }
`

const cardContentStyle = css`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`