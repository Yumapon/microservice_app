// types/notification.ts
export type NotificationType = 'info' | 'warning' | 'error' | 'promotion' | 'alert' | 'progress'

export interface MultilingualText {
  ja: string
  en: string
}

export interface Notification {
  message_id: string
  user_id: string
  type: NotificationType
  title: MultilingualText
  message_summary: MultilingualText
  message_detail: MultilingualText
  is_important: boolean
  is_read: boolean
  created_at: string
  updated_at: string
}