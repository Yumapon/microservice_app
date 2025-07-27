import { css } from '@emotion/react'

export const globalStyle = css`
  *,
  *::before,
  *::after {
    box-sizing: border-box;
  }

  html {
    scroll-behavior: smooth;
  }

  body {
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    background-color: #f9f9f9;
    color: #333;
    line-height: 1.6;
  }

  a {
    color: inherit;
    text-decoration: none;
  }

  button {
    font-family: inherit;
    cursor: pointer;
  }
`