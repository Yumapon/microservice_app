/** @jsxImportSource @emotion/react */
import { css, keyframes } from '@emotion/react'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { useAppDispatch } from '@/hooks/useAppDispatch'

import { NotificationList } from '@/components/NotificationsPage/NotificationList'
import { NotificationDetailModal } from '@/components/NotificationsPage/NotificationDetailModal'
import { loadNotificationsWithReadStatus, fetchUnreadCount, postReadNotification } from '@/store/notificationThunks'
import {
  setSelectedNotification,
  markNotificationAsRead,
} from '@/store/notificationSlice'

import type { RootState } from '@/store'
import type { Notification as StoreNotification } from '@/types/notification'
import type { Notification as DisplayNotification } from '@/components/NotificationsPage/NotificationItem'

import MyPageLayout from '@/components/layout/MyPageLayout'

// 通知データをUI用に変換する関数
const convertToDisplayNotification = (n: StoreNotification): DisplayNotification => ({
  id: n.message_id,
  title: n.title.ja || 'タイトル未設定',
  message: n.message_summary.ja || '内容未設定',
  type: n.type as DisplayNotification['type'],
  read: n.is_read,
  date: n.created_at,
})

const NotificationsPage = () => {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  const userId = useSelector((state: RootState) => state.session.userInfo?.sub)
  const isInitialized = useSelector((state: RootState) => state.notification.isInitialized)
  const notifications = useSelector((state: RootState) => state.notification.list)
  const selectedNotification = useSelector((state: RootState) => state.notification.selectedNotification)

  useEffect(() => {
    console.log('[DEBUG] userId:', userId)
    if (userId) {
      console.log('[DEBUG] dispatch fetchUserNotifications')
      dispatch(loadNotificationsWithReadStatus(userId))
      dispatch(fetchUnreadCount(userId))
    }
  }, [userId, dispatch])

  const handleSelect = (displayNotification: DisplayNotification) => {
    const matched = notifications.find(n => n.message_id === displayNotification.id)
    if (!matched) return

    if (!matched.is_read) {
      dispatch(markNotificationAsRead(matched.message_id))
      if (userId) {
        dispatch(postReadNotification({ userId, messageIds: [matched.message_id] }))
      }
    }
    dispatch(setSelectedNotification({ ...matched, is_read: true }))
  }

  const handleClose = () => {
    dispatch(setSelectedNotification(null))
  }

  return (
    <MyPageLayout>
      <div css={navBarStyle}>
        <button css={backButtonStyle} onClick={() => navigate('/mypage')}>
          ← MyPageに戻る
        </button>
      </div>

      <h1 css={pageTitle}>お知らせ一覧</h1>

      {!isInitialized ? (
        <div css={loadingContainer}>
          <div css={spinner} />
          <p css={loadingText}>読み込み中...</p>
        </div>
      ) : (
        <NotificationList
          notifications={notifications.map(convertToDisplayNotification)}
          onSelect={handleSelect}
        />
      )}

      {selectedNotification && (
        <NotificationDetailModal
          notification={convertToDisplayNotification(selectedNotification)}
          onClose={handleClose}
        />
      )}
    </MyPageLayout>
  )
}

export default NotificationsPage

// ----------------------------
// CSS
// ----------------------------
const pageTitle = css`
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 2rem;
`

const navBarStyle = css`
  margin-bottom: 1rem;
`

const backButtonStyle = css`
  background: none;
  border: none;
  color: #0ea5e9;
  font-size: 0.95rem;
  text-decoration: underline;
  cursor: pointer;

  &:hover {
    opacity: 0.8;
  }
`

const loadingContainer = css`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 3rem;
`

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`

const spinner = css`
  border: 6px solid #f3f3f3;
  border-top: 6px solid #0ea5e9;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: ${spin} 1s linear infinite;
  margin-bottom: 1rem;
`

const loadingText = css`
  font-size: 1rem;
  color: #555;
`