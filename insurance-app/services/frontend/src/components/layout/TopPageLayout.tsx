/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import type { ReactNode } from 'react'

import Header from '@/components/Common/Header'
import Footer from '@/components/Common/Footer'

type Props = {
  children: ReactNode
}

const TopPageLayout = ({ children }: Props) => {
  return (
    <div css={layoutStyle}>
      <Header />
      <main css={mainStyle}>{children}</main>
      <Footer />
    </div>
  )
}

export default TopPageLayout

// ----------------------------
// Emotion スタイル
// ----------------------------
const layoutStyle = css`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`

const mainStyle = css`
  flex: 1;
  padding: 2rem 1rem;
  background: #f9f9f9;
`