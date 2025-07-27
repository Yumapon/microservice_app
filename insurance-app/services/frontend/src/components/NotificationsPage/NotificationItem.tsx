/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import type { JSX } from 'react'
import { FiInfo, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi'

export type NotificationType = 'info' | 'warning' | 'error' | 'promotion' | 'alert' | 'progress'

export type Notification = {
  id: string
  title: string
  message: string
  type: NotificationType
  read: boolean
  date: string
}

const typeColorMap: Record<NotificationType, string> = {
  info: '#2563EB',       // 青 (お知らせ)
  warning: '#F59E0B',    // 橙 (警告)
  error: '#DC2626',      // 赤 (エラー)
  promotion: '#10B981',  // 緑 (キャンペーン・特典)
  alert: '#B91C1C',      // 濃赤 (重要警告)
  progress: '#3B82F6',   // 明るい青 (進捗中)
}

const typeLabelMap: Record<NotificationType, string> = {
  info: 'お知らせ',
  warning: '注意',
  error: 'エラー',
  promotion: 'キャンペーン・特典',
  alert: '重要警告',
  progress: '進捗中',
}

const typeIconMap: Record<NotificationType, JSX.Element> = {
  info: <FiInfo />,
  warning: <FiAlertTriangle />,
  error: <FiAlertTriangle />,
  promotion: <FiCheckCircle />,
  alert: <FiAlertTriangle />,
  progress: <FiInfo />,
}

type Props = {
  notification: Notification
  onClick?: () => void
}

export const NotificationItem = ({ notification, onClick }: Props) => {
  return (
    <li
      css={[cardStyle(notification.read), hoverStyle]}
      onClick={onClick}
    >
      <div css={topRow}>
        <span css={badgeStyle(typeColorMap[notification.type])}>
          {typeIconMap[notification.type]} {typeLabelMap[notification.type]}
        </span>
        
        <span css={dateStyle}>{new Date(notification.date).toLocaleDateString('ja-JP')}</span>
      </div>
      
      <div css={mainRow}>
        {/* メッセージとタイトル */}
        <div css={textContainer}>
          <h3 css={titleStyle}>{notification.title}</h3>
          <p css={messageStyle}>{notification.message}</p>
        </div>

        {/* 未読バッジ */}
        {!notification.read && <span css={unreadBadge}>未読</span>}
      </div>
    </li>
  )
}

// ----------------------------
const cardStyle = (read: boolean) => css`
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  background: ${read ? '#f5f6f7' : '#fff'};
  border-left: 4px solid ${read ? '#ccc' : '#0ea5e9'};
  border-radius: 6px;
  padding: 1.2rem 1.5rem;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
`
const hoverStyle = css`
  &:hover {
    background: #f9fafb;
  }
`

const topRow = css`
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-bottom: 0.4rem;
  color: #666;
`

const dateStyle = css`
  font-size: 0.8rem;
`

const unreadBadge = css`
  background: #ef4444;
  color: white;
  font-size: 0.7rem;
  padding: 0.2rem 0.4rem;
  border-radius: 9999px;
  margin-left: 0.5rem;
  flex-shrink: 0;
`

const mainRow = css`
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;

  @media (min-width: 640px) {
    flex-wrap: nowrap;
  }
`

const badgeStyle = (color: string) => css`
  background: ${color};
  color: white;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  min-width: 80px;
  text-align: center;
  flex-shrink: 0;
`

const textContainer = css`
  flex-grow: 1;
`

const titleStyle = css`
  font-weight: bold;
  margin-bottom: 0.2rem;
`

const messageStyle = css`
  font-size: 0.9rem;
  color: #444;
`