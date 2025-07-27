/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'

type Props = {
  label: string
  onClick: () => void
}

export const Button = ({ label, onClick }: Props) => {
  return (
    <button css={buttonStyle} onClick={onClick}>
      {label}
    </button>
  )
}

export const buttonStyle = css`
  background-color: #0070f3;
  color: white;
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 112, 243, 0.3);

  &:hover {
    background-color: #0059c1;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 112, 243, 0.35);
  }

  &:active {
    transform: translateY(1px);
    box-shadow: 0 2px 6px rgba(0, 112, 243, 0.2);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 112, 243, 0.4);
  }
`