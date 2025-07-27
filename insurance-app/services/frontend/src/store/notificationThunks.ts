// store/notificationThunks.ts
import { createAsyncThunk } from '@reduxjs/toolkit'
import {
  setNotifications,
  setUnreadCount,
  setIsLoading,
  setIsInitialized,
  updateReadStatus,
} from '@/store/notificationSlice'
import type { Notification } from '@/types/notification'

/**
 * 通知一覧と既読情報をまとめて取得し、Reduxステートに反映
 */
export const loadNotificationsWithReadStatus = createAsyncThunk<
  void,
  string
>('notifications/loadWithReadStatus', async (userId, { dispatch }) => {
  console.log('[THUNK] loadNotificationsWithReadStatus: 開始 userId =', userId)
  dispatch(setIsLoading(true))
  await dispatch(fetchUserNotifications(userId))
  await dispatch(fetchAndUpdateReadStatus(userId))
  dispatch(setIsLoading(false))
  dispatch(setIsInitialized(true)) // ← 追加
  console.log('[THUNK] loadNotificationsWithReadStatus: 終了')
})

/**
 * 通知一覧を取得
 * GET /api/v1/user_notification/:user_id
 */
export const fetchUserNotifications = createAsyncThunk(
  'notification/fetchUserNotifications',
  async (userId: string, { dispatch }) => {
    console.log('[THUNK] fetchUserNotifications: 開始 userId =', userId)
    try {
      const res = await fetch(`/api/v1/user_notification/${userId}`, {
        credentials: 'include',
      })
      console.log('[THUNK] fetchUserNotifications: response.status =', res.status)

      if (!res.ok) {
        console.error('[THUNK] fetchUserNotifications: レスポンスエラー status =', res.status)
        throw new Error('通知一覧の取得に失敗しました')
      }

      const data: Notification[] = await res.json()
      console.log('[THUNK] fetchUserNotifications: 通知件数 =', data.length)
      dispatch(setNotifications(data))
    } catch (error) {
      console.error('[THUNK] fetchUserNotifications: エラー発生', error)
      dispatch(setNotifications([]))
    } finally {
      console.log('[THUNK] fetchUserNotifications: 終了')
    }
  }
)

/**
 * 未読通知一覧を取得
 * GET /api/v1/user_notification/:user_id
 */
export const fetchUnreadUserNotifications = createAsyncThunk(
  'notification/fetchUnreadUserNotifications',
  async (userId: string, { dispatch }) => {
    console.log('[THUNK] fetchUnreadUserNotifications: 開始 userId =', userId)
    try {
      const res = await fetch(`/api/v1/user_notification/unread/${userId}`, {
        credentials: 'include',
      })
      console.log('[THUNK] fetchUnreadUserNotifications: response.status =', res.status)

      if (!res.ok) {
        console.error('[THUNK] fetchUnreadUserNotifications: レスポンスエラー status =', res.status)
        throw new Error('未読通知一覧の取得に失敗しました')
      }

      const data: Notification[] = await res.json()
      console.log('[THUNK] fetchUnreadUserNotifications: 未読通知件数 =', data.length)
      dispatch(setNotifications(data))
    } catch (error) {
      console.error('[THUNK] fetchUnreadUserNotifications: エラー発生', error)
      dispatch(setNotifications([]))
    } finally {
      console.log('[THUNK] fetchUnreadUserNotifications: 終了')
    }
  }
)

/**
 * 未読件数を取得
 * GET /api/v1/user_notification/unread_count/:user_id
 */
export const fetchUnreadCount = createAsyncThunk(
  'notification/fetchUnreadCount',
  async (userId: string, { dispatch }) => {
    console.log('[THUNK] fetchUnreadCount: 開始 userId =', userId)
    try {
      const res = await fetch(`/api/v1/user_notification/unread_count/${userId}`, {
        credentials: 'include',
      })
      console.log('[THUNK] fetchUnreadCount: response.status =', res.status)

      if (!res.ok) {
        console.error('[THUNK] fetchUnreadCount: レスポンスエラー status =', res.status)
        throw new Error('未読件数の取得に失敗しました')
      }

      const count: number = await res.json()
      console.log('[THUNK] fetchUnreadCount: 未読件数 =', count)
      dispatch(setUnreadCount(count))
    } catch (error) {
      console.error('[THUNK] fetchUnreadCount: エラー発生', error)
      dispatch(setUnreadCount(0))
    } finally {
      console.log('[THUNK] fetchUnreadCount: 終了')
    }
  }
)

/**
 * 既読メッセージを取得し、Reduxステートに反映
 * GET /api/v1/user_notification/read/:user_id
 */
export const fetchAndUpdateReadStatus = createAsyncThunk<
  void,
  string
>('notifications/fetchAndUpdateReadStatus', async (userId, { dispatch }) => {
  console.log('[THUNK] fetchAndUpdateReadStatus: 開始 userId =', userId)
  try {
    const response = await fetch(`/api/v1/user_notification/read/${userId}`)
    console.log('[THUNK] fetchAndUpdateReadStatus: response.status =', response.status)

    if (!response.ok) {
      console.error('[THUNK] fetchAndUpdateReadStatus: レスポンスエラー status =', response.status)
      throw new Error('既読通知の取得に失敗しました')
    }

    const readMessageIds: string[] = await response.json()
    console.log('[THUNK] fetchAndUpdateReadStatus: 既読ID件数 =', readMessageIds.length)
    dispatch(updateReadStatus(readMessageIds))
  } catch (error) {
    console.error('[THUNK] fetchAndUpdateReadStatus: エラー発生', error)
  } finally {
    console.log('[THUNK] fetchAndUpdateReadStatus: 終了')
  }
})

/**
 * 通知の既読状態をサービスに通知
 * POST /api/v1/user_notification/read/:user_id
 */
interface MarkReadRequest {
  userId: string
  messageIds: string[]
}

export const postReadNotification = createAsyncThunk<
  void,
  MarkReadRequest
>('notifications/postReadNotification', async ({ userId, messageIds }) => {
  console.log('[THUNK] postReadNotification: 開始 userId =', userId, ' messageIds =', messageIds)
  try {
    const res = await fetch(`/api/v1/user_notification/read/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message_ids: messageIds }),
    })
    console.log('[THUNK] postReadNotification: response.status =', res.status)

    if (!res.ok) {
      console.error('[THUNK] postReadNotification: レスポンスエラー status =', res.status)
      throw new Error('既読通知の送信に失敗しました')
    }

    console.log('[THUNK] postReadNotification: 成功')
  } catch (error) {
    console.error('[THUNK] postReadNotification: エラー発生', error)
  } finally {
    console.log('[THUNK] postReadNotification: 終了')
  }
})