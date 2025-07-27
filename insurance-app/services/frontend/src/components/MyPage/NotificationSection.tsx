import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useAppDispatch } from '@/hooks/useAppDispatch'
import type { RootState } from '@/store'
import { fetchUnreadUserNotifications, fetchUnreadCount, postReadNotification } from '@/store/notificationThunks'
import {
  setSelectedNotification,
  markNotificationAsRead,
} from '@/store/notificationSlice'
import { css } from '@emotion/react'
import type { Notification } from '@/types/notification'

type NotificationType = 'info' | 'warning' | 'error' | 'promotion' | 'alert' | 'progress'

export const NotificationSection = () => {
  const dispatch = useAppDispatch()
  const userId = useSelector((state: RootState) => state.session.userInfo?.sub)
  const notification = useSelector((state: RootState) => state.notification.list)
  const isLoading = useSelector((state: RootState) => state.notification.isLoading)
  const selected = useSelector((state: RootState) => state.notification.selectedNotification)

  const unreadNotifications = notification.filter((n) => !n.is_read)
  const unreadCount = useSelector((state: RootState) => state.notification.unreadCount)

  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 5
  const totalPages = Math.ceil(unreadNotifications.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const paginatedNotifications = unreadNotifications.slice(startIndex, startIndex + itemsPerPage)

  useEffect(() => {
    console.log('[DEBUG] userId:', userId)
    if (userId) {
      dispatch(fetchUnreadUserNotifications(userId))
      dispatch(fetchUnreadCount(userId))
    }
  }, [userId, dispatch])

  const handleSelect = (n: Notification) => {
    if (!n.is_read) {
      dispatch(markNotificationAsRead(n.message_id))
      if (userId) {
        dispatch(postReadNotification({ userId, messageIds: [n.message_id] }))
      }
    }
    dispatch(setSelectedNotification(n))
  }

  return (
    <section css={sectionStyle}>
      <div css={innerBox}>
        <div css={headerStyle}>
          <h2 css={titleStyle}>お知らせ（未読が {unreadCount} 件あります）</h2>
          <a href="/mypage/notifications" css={linkStyle}>すべて見る</a>
        </div>

        {isLoading ? (
          <p css={noInfoText}>読み込み中...</p>
        ) : unreadNotifications.length === 0 ? (
          <p css={noInfoText}>現在表示するお知らせはありません</p>
        ) : (
          <>
            <ul css={listStyle}>
              {paginatedNotifications.map((n) => (
                <li
                  key={n.message_id}
                  css={[cardStyle(false), hoverStyle]}
                  onClick={() => handleSelect(n)}
                >
                  <span css={badgeStyle(typeColorMap[n.type])}>{typeLabelMap[n.type]}</span>
                  <strong css={titleText}>{n.title.ja}</strong>
                  <span css={messageText}>-- {n.message_summary.ja}</span>
                  <time css={dateText}>通知日：{new Date(n.created_at).toLocaleDateString('ja-JP')}</time>
                </li>
              ))}
            </ul>

            {/* ページネーション */}
            <div css={paginationStyle}>
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              >
                前へ
              </button>
              <span>{currentPage} / {totalPages}</span>
              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              >
                次へ
              </button>
            </div>

            {/* 表示件数 */}
            <p css={countTextStyle}>
              表示中: {startIndex + 1}〜{Math.min(startIndex + itemsPerPage, unreadNotifications.length)}件 / 全{unreadNotifications.length}件
            </p>
          </>
        )}
      </div>

      {selected && (
        <div css={modalOverlay} onClick={() => dispatch(setSelectedNotification(null))}>
          <div css={modalContent} onClick={(e) => e.stopPropagation()}>
            <div css={modalHeader}>
              <span css={badgeStyle(typeColorMap[selected.type])}>{typeLabelMap[selected.type]}</span>
              <button css={closeButton} onClick={() => dispatch(setSelectedNotification(null))}>×</button>
            </div>
            <h3 css={modalTitle}>{selected.title.ja}</h3>
            <p css={modalMessage}>{selected.message_detail.ja}</p>
            <time css={modalDate}>{new Date(selected.created_at).toLocaleString('ja-JP')}</time>
          </div>
        </div>
      )}
    </section>
  )
}

export default NotificationSection

// ----------------------------
// CSS
// ----------------------------
const sectionStyle = css`padding: 1rem 0; display: flex; justify-content: center;`
const innerBox = css`background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 1rem; width: 100%;`
const headerStyle = css`display: flex; justify-content: space-between; align-items: center;`
const titleStyle = css`font-size: 1.2rem; font-weight: bold;`
const linkStyle = css`font-size: 0.9rem; color: #0ea5e9; text-decoration: underline; cursor: pointer;`
const noInfoText = css`color: #777; text-align: center; margin: 1rem 0;`
const listStyle = css`list-style: none; padding: 0; margin-top: 1rem; display: flex; flex-direction: column; gap: 0.5rem;`
const cardStyle = (read: boolean) => css`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.8rem;
  border-left: 4px solid ${read ? '#ccc' : '#0ea5e9'};
  background: #fff;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  transition: background 0.2s;
  flex-wrap: wrap;
  @media (min-width: 640px) {
    flex-wrap: nowrap;
  }
`
const hoverStyle = css`&:hover { background: #f4f4f5; }`
const badgeStyle = (color: string) => css`
  background: ${color};
  color: white;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  min-width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  text-align: center;
`
const titleText = css`font-weight: bold; color: #111827;`
const messageText = css`color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 30%; min-width: 100px;`
const dateText = css`font-size: 0.75rem; color: #888; margin-left: auto; white-space: nowrap;`

const paginationStyle = css`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;

  button {
    background: #e5e7eb;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
`

const countTextStyle = css`
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
`

// Modal
const modalOverlay = css`position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.4); display: flex; justify-content: center; align-items: center; z-index: 1000;`
const modalContent = css`background: white; padding: 1.5rem; border-radius: 10px; max-width: 480px; width: 90%; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: relative;`
const modalHeader = css`display: flex; justify-content: space-between; align-items: center;`
const closeButton = css`background: transparent; border: none; font-size: 1.2rem; cursor: pointer; color: #888;`
const modalTitle = css`font-size: 1.1rem; font-weight: bold; margin: 1rem 0 0.5rem;`
const modalMessage = css`color: #333; margin-bottom: 1rem;`
const modalDate = css`font-size: 0.8rem; color: #999;`

const typeColorMap: Record<NotificationType, string> = {
  info: '#2563EB',
  warning: '#F59E0B',
  error: '#DC2626',
  promotion: '#10B981',
  alert: '#B91C1C',
  progress: '#3B82F6',
}

const typeLabelMap: Record<NotificationType, string> = {
  info: 'お知らせ',
  warning: '注意',
  error: 'エラー',
  promotion: 'キャンペーン・特典',
  alert: '重要警告',
  progress: '進捗中',
}