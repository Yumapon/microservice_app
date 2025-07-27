/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import type { Notification } from './NotificationItem'

type Props = {
  notification: Notification | null
  onClose: () => void
}

export const NotificationDetailModal = ({ notification, onClose }: Props) => {
  if (!notification) return null

  return (
    <div css={overlayStyle}>
      <div css={modalStyle}>
        <h2 css={titleStyle}>{notification.title}</h2>
        <p css={dateStyle}>{new Date(notification.date).toLocaleString('ja-JP')}</p>
        <p css={messageStyle}>{notification.message}</p>
        <button css={closeButton} onClick={onClose}>閉じる</button>
      </div>
    </div>
  )
}

const overlayStyle = css`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`

const modalStyle = css`
  background: white;
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
`

const titleStyle = css`
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
`

const dateStyle = css`
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 1rem;
`

const messageStyle = css`
  font-size: 1rem;
  margin-bottom: 1.5rem;
`

const closeButton = css`
  background: #0ea5e9;
  color: white;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
`