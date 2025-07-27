/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { useState } from 'react'

interface ChangePaymentModalProps {
  onClose: () => void
}

export const ChangePaymentModal = ({ onClose }: ChangePaymentModalProps) => {
  const theme = useTheme()
  const [selectedMethod, setSelectedMethod] = useState('credit')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    alert(`支払方法「${paymentLabel(selectedMethod)}」に変更しました。`)
    onClose()
  }

  return (
    <div css={overlayStyle}>
      <div css={modalStyle}>
        <h3 css={titleStyle}>支払方法を変更</h3>
        <form onSubmit={handleSubmit}>
          <div css={formGroup}>
            <label>
              <input
                type="radio"
                name="payment"
                value="credit"
                checked={selectedMethod === 'credit'}
                onChange={(e) => setSelectedMethod(e.target.value)}
              />
              クレジットカード
            </label>
            <label>
              <input
                type="radio"
                name="payment"
                value="bank"
                checked={selectedMethod === 'bank'}
                onChange={(e) => setSelectedMethod(e.target.value)}
              />
              銀行口座振替
            </label>
            <label>
              <input
                type="radio"
                name="payment"
                value="convenience"
                checked={selectedMethod === 'convenience'}
                onChange={(e) => setSelectedMethod(e.target.value)}
              />
              コンビニ支払い
            </label>
          </div>
          <div css={buttonRow}>
            <button type="submit" css={primaryButton(theme)}>変更を保存</button>
            <button type="button" onClick={onClose} css={cancelButton}>キャンセル</button>
          </div>
        </form>
      </div>
    </div>
  )
}

const paymentLabel = (value: string) => {
  switch (value) {
    case 'credit': return 'クレジットカード'
    case 'bank': return '銀行口座振替'
    case 'convenience': return 'コンビニ支払い'
    default: return ''
  }
}

// ----------------------------
// Emotion Styles
// ----------------------------
const overlayStyle = css`
  position: fixed;
  top: 0;
  left: 0;
  z-index: 2000;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
`

const modalStyle =  css`
  background: #fff;
  border-radius: 10px;
  padding: 2rem;
  width: 90%;
  max-width: 480px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
`

const titleStyle = css`
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
`

const formGroup = css`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;

  label {
    font-size: 1rem;
  }

  input[type='radio'] {
    margin-right: 0.5rem;
  }
`

const buttonRow = css`
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
`

const primaryButton = (theme: any) => css`
  background: ${theme.colors.primary};
  color: white;
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
`

const cancelButton = css`
  background: transparent;
  color: #666;
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  cursor: pointer;
`