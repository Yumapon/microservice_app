/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import type { ReactNode } from 'react'

import MyPageHeader from '@/components/Common/MyPageHeader'
import Footer from '@/components/Common/Footer'

type Props = {
  children: ReactNode
}

const MyPageLayout = ({ children }: Props) => {
  return (
    <div css={layoutStyle}>
      <MyPageHeader />
      <main css={mainStyle}>{children}</main>
      <Footer />
    </div>
  )
}

export default MyPageLayout

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