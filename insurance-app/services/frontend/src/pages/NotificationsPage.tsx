/** @jsxImportSource @emotion/react */
import { css, keyframes } from '@emotion/react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { useAppDispatch } from '@/hooks/useAppDispatch'

import { NotificationDetailModal } from '@/components/NotificationsPage/NotificationDetailModal'
import {
  loadNotificationsWithReadStatus,
  fetchUnreadCount,
  postReadNotification,
} from '@/store/notificationThunks'
import {
  setSelectedNotification,
  markNotificationAsRead,
} from '@/store/notificationSlice'

import type { RootState } from '@/store'
import type { Notification as StoreNotification } from '@/types/notification'
import type { Notification as DisplayNotification, NotificationType } from '@/components/NotificationsPage/NotificationItem'

import MyPageLayout from '@/components/layout/MyPageLayout'

// ----------------------------
// 定数定義
// ----------------------------
const typeColorMap: Record<NotificationType, string> = {
  info: '#2563EB',
  warning: '#F59E0B',
  error: '#DC2626',
  promotion: '#10B981',
  alert: '#B91C1C',
  progress: '#3B82F6',
}

const typeLabelMap: Record<NotificationType | 'all', string> = {
  all: 'すべて',
  info: 'お知らせ',
  warning: '注意',
  error: 'エラー',
  promotion: 'キャンペーン・特典',
  alert: '重要警告',
  progress: '進捗中',
}

const typeIconMap: Record<NotificationType | 'all', string> = {
  all: '',
  info: 'ℹ️',
  warning: '⚠️',
  error: '❌',
  promotion: '🎁',
  alert: '🚨',
  progress: '🔄',
}

const ITEMS_PER_PAGE = 30

// ----------------------------
// NotificationPage本体
// ----------------------------
const NotificationPage = () => {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  const userId = useSelector((state: RootState) => state.session.userInfo?.sub)
  const isInitialized = useSelector((state: RootState) => state.notification.isInitialized)
  const notifications = useSelector((state: RootState) => state.notification.list)
  const selectedNotification = useSelector((state: RootState) => state.notification.selectedNotification)

  const [readFilter, setReadFilter] = useState<'all' | 'read' | 'unread'>('all')
  const [typeFilter, setTypeFilter] = useState<NotificationType | 'all'>('all')
  const [keywordFilter, setKeywordFilter] = useState('')
  const [currentPage, setCurrentPage] = useState(1)

  useEffect(() => {
    if (userId) {
      dispatch(loadNotificationsWithReadStatus(userId))
      dispatch(fetchUnreadCount(userId))
    }
  }, [userId, dispatch])

  const convertToDisplayNotification = (n: StoreNotification): DisplayNotification => ({
    id: n.message_id,
    title: n.title.ja || 'タイトル未設定',
    message: n.message_summary.ja || '内容未設定',
    type: n.type as DisplayNotification['type'],
    read: n.is_read,
    date: n.created_at,
  })

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

    const filtered = notifications
    .filter(n => {
      if (readFilter === 'unread') return !n.is_read
      if (readFilter === 'read') return n.is_read
      return true
    })
    .filter(n => typeFilter === 'all' || n.type === typeFilter)
    .filter(n => {
      const keyword = keywordFilter.trim().toLowerCase()
      if (!keyword) return true
      return (
        (n.title?.ja?.toLowerCase().includes(keyword) ?? false) ||
        (n.message_summary?.ja?.toLowerCase().includes(keyword) ?? false)
      )
    })

  const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE)
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const paginated = filtered.slice(startIndex, startIndex + ITEMS_PER_PAGE)

  return (
    <MyPageLayout>
      <div css={navBarStyle}>
        <button css={backButtonStyle} onClick={() => navigate('/mypage')}>
          ← MyPageに戻る
        </button>
      </div>

      <h1 css={pageTitle}>お知らせ一覧</h1>

      <div css={filterContainer}>
        <div css={filterGroup}>
          <span>表示:</span>
          <button css={[filterButton, readFilter === 'all' && activeFilter]} onClick={() => setReadFilter('all')}>すべて</button>
          <button css={[filterButton, readFilter === 'unread' && activeFilter]} onClick={() => setReadFilter('unread')}>未読</button>
          <button css={[filterButton, readFilter === 'read' && activeFilter]} onClick={() => setReadFilter('read')}>既読</button>
        </div>
        <div css={filterGroup}>
          <label htmlFor="typeFilter">種別:</label>
          <select
            id="typeFilter"
            css={modernSelect}
            value={typeFilter}
            onChange={e => setTypeFilter(e.target.value as NotificationType)}
          >
            {Object.keys(typeLabelMap).map(type => (
              <option key={type} value={type}>
                {typeIconMap[type as NotificationType]} {typeLabelMap[type as NotificationType]}
              </option>
            ))}
          </select>
        </div>
        <div css={filterGroup}>
          <input
            type="text"
            placeholder="キーワード検索"
            css={searchInput}
            value={keywordFilter}
            onChange={e => {
              setCurrentPage(1)
              setKeywordFilter(e.target.value)
            }}
          />
        </div>
      </div>

      {!isInitialized ? (
        <div css={loadingContainer}>
          <div css={spinner} />
          <p css={loadingText}>読み込み中...</p>
        </div>
      ) : filtered.length === 0 ? (
        <p css={noInfoText}>お知らせはありません</p>
      ) : (
        <>
          <ul css={listStyle}>
            {paginated.map(n => {
              const display = convertToDisplayNotification(n)
              return (
                <li
                  key={display.id}
                  css={[cardStyle(display.read), hoverStyle]}
                  onClick={() => handleSelect(display)}
                >
                  <span css={badgeStyle(typeColorMap[display.type])}>
                    {typeIconMap[display.type]} {typeLabelMap[display.type]}
                  </span>
                  <strong css={titleText}>{display.title}</strong>
                  <span css={messageText}>-- {display.message}</span>
                  <div css={dateContainer}>
                    {!display.read && <span css={unreadBadge}>未読</span>}
                    <time css={dateText}>通知日：{new Date(display.date).toLocaleDateString('ja-JP')}</time>
                  </div>
                </li>
              )
            })}
          </ul>

          <div css={paginationStyle}>
            <button disabled={currentPage === 1} onClick={() => setCurrentPage(p => Math.max(1, p - 1))}>前へ</button>
            <span>{currentPage} / {totalPages}</span>
            <button disabled={currentPage === totalPages} onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}>次へ</button>
          </div>

          <p css={countTextStyle}>
            表示中: {startIndex + 1}〜{Math.min(startIndex + ITEMS_PER_PAGE, filtered.length)}件 / 全{filtered.length}件
          </p>
        </>
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

export default NotificationPage

// ----------------------------
// スタイル定義（CSS）
// ----------------------------
const pageTitle = css`font-size: 1.5rem; font-weight: bold; margin-bottom: 2rem;`
const navBarStyle = css`margin-bottom: 1rem;`
const backButtonStyle = css`
  background: none; border: none; color: #0ea5e9;
  font-size: 0.95rem; text-decoration: underline; cursor: pointer;
  &:hover { opacity: 0.8; }
`
const filterContainer = css`display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; margin-bottom: 1.5rem;`
const filterGroup = css`display: flex; align-items: center; gap: 0.5rem;`
const filterButton = css`background: #f1f5f9; padding: 0.3rem 0.6rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem;`
const activeFilter = css`background: #0ea5e9; color: white;`
const modernSelect = css`padding: 0.3rem 0.6rem; font-size: 0.85rem; border-radius: 6px;`
const searchInput = css`padding: 0.35rem 0.6rem; border: 1px solid #ccc; border-radius: 6px; font-size: 0.85rem; width: 200px; box-shadow: 1px 1px 2px rgba(0,0,0,0.05); &:focus { outline: none; border-color: #0ea5e9; }`
const loadingContainer = css`display: flex; flex-direction: column; align-items: center; margin-top: 3rem;`
const spin = keyframes`0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }`
const spinner = css`border: 6px solid #f3f3f3; border-top: 6px solid #0ea5e9; border-radius: 50%; width: 40px; height: 40px; animation: ${spin} 1s linear infinite; margin-bottom: 1rem;`
const loadingText = css`font-size: 1rem; color: #555;`
const noInfoText = css`color: #777; text-align: center; margin: 1rem 0;`
const listStyle = css`list-style: none; padding: 0; margin-top: 1rem; display: flex; flex-direction: column; gap: 0.5rem;`
const cardStyle = (read: boolean) => css`display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.8rem; border-left: 4px solid ${read ? '#ccc' : '#0ea5e9'}; background: ${read ? '#f5f6f7' : '#ffffff'}; border-radius: 6px; font-size: 0.9rem; cursor: pointer; transition: background 0.2s; flex-wrap: wrap;`
const hoverStyle = css`&:hover { background: #f4f4f5; }`
const badgeStyle = (color: string) => css`background: ${color}; color: white; font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 9999px; min-width: 60px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; text-align: center;`
const titleText = css`font-weight: bold; color: #111827;`
const messageText = css`color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 30%; min-width: 100px;`
const dateContainer = css`display: flex; align-items: center; gap: 0.5rem; margin-left: auto;`
const unreadBadge = css`background: #ef4444; color: white; padding: 0.1rem 0.4rem; font-size: 0.7rem; border-radius: 4px;`
const dateText = css`font-size: 0.75rem; color: #888;`
const paginationStyle = css`display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1rem; button { background: #e5e7eb; border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; &:disabled { opacity: 0.5; cursor: not-allowed; } }`
const countTextStyle = css`text-align: center; font-size: 0.85rem; color: #666; margin-top: 0.5rem;`