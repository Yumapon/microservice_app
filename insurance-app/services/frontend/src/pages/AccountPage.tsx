/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useNavigate } from 'react-router-dom'

import MyPageHeader from '@/components/Common/MyPageHeader'
import Footer from '@/components/Common/Footer'
import ProfileSection from '@/components/AccountPage/ProfileSection'

const AccountPage = () => {
  const navigate = useNavigate()

  return (
    <div css={pageWrapper}>
      <MyPageHeader />
      <main css={mainStyle}>
        <div css={navBarStyle}>
          <button css={backButtonStyle} onClick={() => navigate('/mypage/profile')}>
            ← マイページに戻る
          </button>
        </div>
        <h1 css={titleStyle}>ご本人情報</h1>
        <ProfileSection />
      </main>
      <Footer />
    </div>
  )
}

export default AccountPage

// ----------------------------
// Emotion CSS
// ----------------------------
const pageWrapper = css`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`

const mainStyle = css`
  flex: 1;
  padding: 2rem 1rem;
  max-width: 1024px;
  margin: 0 auto;
`

const titleStyle = css`
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 2rem;
`

const navBarStyle = css`
  margin-bottom: 1rem;
`

const backButtonStyle = css`
  background: none;
  border: none;
  color: #0ea5e9;
  font-size: 0.95rem;
  text-decoration: underline;
  cursor: pointer;

  &:hover {
    opacity: 0.8;
  }
`