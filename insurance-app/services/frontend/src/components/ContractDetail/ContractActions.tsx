/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaExchangeAlt, FaTimesCircle, FaUserEdit } from 'react-icons/fa'

export const ContractActions = () => {
  const theme = useTheme()

  const handleChangePayment = () => {
    alert('支払い方法変更モーダルを表示（実装予定）')
  }

  const handleCancelContract = () => {
    if (window.confirm('本当に解約しますか？')) {
      alert('解約処理を実行（実装予定）')
    }
  }

  const handleEditBeneficiary = () => {
    alert('保険金受取人変更画面に遷移（実装予定）')
  }

  return (
    <section css={wrapper}>
      <h2 css={titleStyle(theme)}>契約内容の変更</h2>
      <div css={actionGrid}>
        <button css={actionCard(theme)} onClick={handleEditBeneficiary}>
          <FaUserEdit size={24} />
          <span>受取人を変更する</span>
        </button>

        <button css={actionCard(theme)} onClick={handleChangePayment}>
          <FaExchangeAlt size={24} />
          <span>支払い方法を変更</span>
        </button>

        <button css={actionCard(theme)} onClick={handleCancelContract}>
          <FaTimesCircle size={24} />
          <span>契約を解約する</span>
        </button>
      </div>
    </section>
  )
}

// ----------------------------
// Emotion CSS
// ----------------------------

const wrapper = css`
  margin-bottom: 3rem;
`

const titleStyle = (theme: any) => css`
  font-size: 1.4rem;
  font-weight: bold;
  color: ${theme.colors.primary};
  margin-bottom: 1.5rem;
`

const actionGrid = css`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
`

const actionCard = (theme: any) => css`
  border-radius: 10px;
  padding: 1.5rem;
  font-weight: 600;
  color: white;
  cursor: pointer;
  text-align: center;
  transition: background-color 0.2s ease, transform 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

  border: none;
  outline: none;

  &:hover {
    transform: translateY(-3px);
  }

  &:nth-of-type(1) {
    background-color: ${theme.colors.primary};
    &:hover {
      background-color: ${theme.colors.primaryHover};
    }
  }

  &:nth-of-type(2) {
    background-color: #43a047;
    &:hover {
      background-color: #388e3c;
    }
  }

  &:nth-of-type(3) {
    background-color: #e53935;
    &:hover {
      background-color: #c62828;
    }
  }

  svg {
    color: white;
    font-size: 1.5rem;
    transition: transform 0.2s ease;
  }

  span {
    font-size: 0.95rem;
  }

  &:hover svg {
    transform: scale(1.1);
  }
`