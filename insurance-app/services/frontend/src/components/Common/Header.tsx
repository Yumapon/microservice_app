/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { Link } from 'react-router-dom'

const Header = () => {
  const theme = useTheme()

  return (
    <header css={headerStyle(theme)}>
      <Link to="/" className="logo">WEB保険</Link>
      <nav css={navStyle}>
        <a href="http://localhost:8010/api/v1/auth/login" className="login-button">ログイン</a>
      </nav>
    </header>
  )
}

export default Header

// ----------------------------
// Emotion スタイル定義
// ----------------------------
const headerStyle = (theme: any) => css`
  width: 100%;
  height: 64px;
  background-color: ${theme.colors.surface};
  padding: 0 ${theme.spacing.lg};
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid ${theme.colors.muted};
  position: sticky;
  top: 0;
  z-index: 1000;

  .logo {
    font-size: 1.25rem;
    font-weight: 700;
    color: #000;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
`

const navStyle = css`
  .login-button {
    display: inline-block;
    padding: 0.5rem 1.5rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #000;
    border: 2px solid #000;
    border-radius: 9999px;
    text-decoration: none;
    transition: all 0.25s ease-in-out;

    &:hover {
      background-color: #000;
      color: #fff;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
  }
`