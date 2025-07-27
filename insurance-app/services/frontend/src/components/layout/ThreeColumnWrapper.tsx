/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import type { ReactNode } from 'react'

type Props = {
  children: ReactNode
}

const ThreeColumnWrapper = ({ children }: Props) => {
  return <section css={sectionWrapper}>{children}</section>
}

export default ThreeColumnWrapper

// ----------------------------
// CSS
// ----------------------------
const sectionWrapper = css`
  border-top: 1px solid #ddd;
  padding-top: 2rem;
  margin-top: 2rem;

  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;

  > * {
    flex: 1 1 100%;
  }

  @media (min-width: 640px) {
    > * {
      flex: 1 1 calc(50% - 0.5rem);
    }
  }

  @media (min-width: 1024px) {
    > * {
      flex: 1 1 calc(33.33% - 0.67rem);
    }
  }
`