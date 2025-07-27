/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { NotificationItem } from './NotificationItem'
import type { Notification } from './NotificationItem'

type Props = {
  notifications: Notification[]
  onSelect: (notification: Notification) => void
}

export const NotificationList = ({ notifications, onSelect }: Props) => {
  return (
    <div css={listWrapper}>
      <ul css={listStyle}>
        {notifications.map((n) => (
          <NotificationItem key={n.id} notification={n} onClick={() => onSelect(n)} />
        ))}
      </ul>
    </div>
  )
}

const listStyle = css`
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`

const listWrapper = css`
  display: flex;
  justify-content: center;
  padding: 1rem;
  background: #fff;
`