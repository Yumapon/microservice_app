/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'

const MyPageHeader = () => {
  const theme = useTheme()

  const handleLogout = async () => {
    try {
      const response = await fetch('http://localhost:8010/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include', // sessionID を Cookie で送信
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error('ログアウトに失敗しました')
      }

      console.log('ログアウト成功')
      // 仮処理：トップページへ遷移、またはリロード
      window.location.href = '/'
    } catch (error) {
      console.error('ログアウト処理中にエラー:', error)
      alert('ログアウトに失敗しました。')
    }
  }

  return (
    <header role="banner" css={headerStyle(theme)}>
      <div css={innerStyle}>
        <h1 css={titleStyle}>マイページ</h1>
        <button onClick={handleLogout} css={logoutButtonStyle}>
          ログアウト
        </button>
      </div>
    </header>
  )
}

export default MyPageHeader

// ----------------------------
// スタイル定義
// ----------------------------
const headerStyle = (theme: any) => css`
  top: 0;
  width: 100%;
  background-color: ${theme.colors.surface};
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  z-index: 1000;
`

const innerStyle = css`
  max-width: 1024px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`

const titleStyle = css`
  font-size: 1.2rem;
  font-weight: bold;
`

const logoutButtonStyle = css`
  background: transparent;
  border: 1px solid #ccc;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;

  &:hover {
    background: #f8f8f8;
  }
`