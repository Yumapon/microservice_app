/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import type { ReactNode } from 'react'

type Props = {
  children: ReactNode
}

const Container = ({ children }: Props) => {
  return <div css={containerStyle}>{children}</div>
}

export default Container

const containerStyle = css`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
  box-sizing: border-box;

  @media (max-width: 768px) {
    padding: 1.5rem 1rem;
  }
`