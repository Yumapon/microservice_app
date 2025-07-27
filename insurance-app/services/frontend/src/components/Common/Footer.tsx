/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { useNavigate } from 'react-router-dom'

const Footer = () => {
  const theme = useTheme()
  const navigate = useNavigate()

  return (
    
    <footer css={footerStyle(theme)}>
      <div className="links">
        <a onClick={() => navigate(`/terms`)}>利用規約</a>
        <a onClick={() => navigate(`/privacy-policy`)}>プライバシーポリシー</a>
      </div>
      <div className="copyright">
        &copy; {new Date().getFullYear()} 保険アプリ All Rights Reserved.
      </div>
    </footer>
  )
}

export default Footer

// ----------------------------
// Emotion スタイル定義
// ----------------------------
const footerStyle = (theme: any) => css`
  background-color: ${theme.colors.surface};
  color: ${theme.colors.text};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-top: 1px solid ${theme.colors.muted};
  text-align: center;
  font-size: ${theme.fontSize.sm};

  .links {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-bottom: ${theme.spacing.sm};

    a {
      text-decoration: none;
      color: ${theme.colors.text};
      transition: color 0.2s;

      &:hover {
        color: ${theme.colors.primary};
      }
    }
  }

  .copyright {
    color: ${theme.colors.muted};
  }
`