/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import type { ReactNode } from 'react'

type Props = {
  children: ReactNode
}

const TwoColumnWrapper = ({ children }: Props) => {
  return <section css={wrapperStyle}>{children}</section>
}

export default TwoColumnWrapper

// ----------------------------
// CSS
// ----------------------------
const wrapperStyle = css`
  border-top: 1px solid #ddd;
  padding-top: 2rem;
  margin-top: 2rem;
  margin-bottom: 2rem;

  display: flex;
  flex-wrap: wrap;
  gap: 1rem;

  > * {
    flex: 1 1 100%;
  }

  @media (min-width: 768px) {
    > * {
      flex: 1 1 calc(50% - 0.5rem);
    }
  }
`