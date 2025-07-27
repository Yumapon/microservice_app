// store/notificationSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { Notification } from '@/types/notification'

interface NotificationState {
  list: Notification[]
  isLoading: boolean
  isInitialized: boolean
  unreadCount: number
  selectedNotification: Notification | null
}

const initialState: NotificationState = {
  list: [],
  isLoading: false,
  isInitialized: false,
  unreadCount: 0,
  selectedNotification: null,
}

const notificationSlice = createSlice({
  name: 'notification',
  initialState,
  reducers: {
    /**
     * 通知一覧をセットする（未読件数の更新は行わない）
     */
    setNotifications: (state, action: PayloadAction<Notification[]>) => {
      state.list = action.payload
    },

    /**
     * 未読件数をセットする（別APIより取得）
     */
    setUnreadCount: (state, action: PayloadAction<number>) => {
      state.unreadCount = action.payload
    },

    /**
     * ローディング状態の切り替え
     */
    setIsLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },

    /**
     * 初期化済みかどうかの状態の切り替え
     */
    setIsInitialized: (state, action: PayloadAction<boolean>) => {
      state.isInitialized = action.payload
    },

    /**
     * 詳細表示中の通知をセット
     */
    setSelectedNotification: (state, action: PayloadAction<Notification | null>) => {
      state.selectedNotification = action.payload
    },

    /**
     * 通知を既読扱いに変更（local状態のみ）
     */
    markNotificationAsRead: (state, action: PayloadAction<string>) => {
      const target = state.list.find(n => n.message_id === action.payload)
      if (target && !target.is_read) {
        target.is_read = true
        state.unreadCount = Math.max(0, state.unreadCount - 1)
      }
    },

    /**
     * 通知全体をクリア
     */
    clearNotifications: (state) => {
      state.list = []
      state.unreadCount = 0
      state.selectedNotification = null
    },

    updateReadStatus: (state, action: PayloadAction<string[]>) => {
      const readIds = new Set(action.payload)
      state.list = state.list.map(n => ({
        ...n,
        is_read: readIds.has(n.message_id) ? true : n.is_read,
      }))
    }
  },
})

export const {
  updateReadStatus,
  setNotifications,
  setUnreadCount,
  setIsLoading,
  setIsInitialized,
  setSelectedNotification,
  markNotificationAsRead,
  clearNotifications,
} = notificationSlice.actions

export default notificationSlice.reducer