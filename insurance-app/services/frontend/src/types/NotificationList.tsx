import type { Notification } from '@/types/notification'

interface Props {
  notifications: Notification[]
  onSelect: (notification: Notification) => void
}

export const NotificationList = ({ notifications, onSelect }: Props) => {
  return (
    <ul>
      {notifications.map((n) => (
        <li key={n.message_id} onClick={() => onSelect(n)}>
          <strong>{n.title.ja}</strong> - {n.message_summary.ja}
        </li>
      ))}
    </ul>
  )
}