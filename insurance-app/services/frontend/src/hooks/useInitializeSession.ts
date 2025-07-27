// hooks/useInitializeSession.ts
import { useEffect } from 'react'
import { useAppDispatch } from '@/hooks/useAppDispatch'
import { setSession } from '@/store/sessionSlice'

export const useInitializeSession = () => {
  const dispatch = useAppDispatch()

  useEffect(() => {
    const fetchSessionInfo = async () => {
      console.log('[SessionInit] セッション情報の取得開始')

      try {
        const res = await fetch('/api/v1/auth/login', {
          credentials: 'include',
        })

        console.log('[SessionInit] API呼び出し結果:', res.status)

        if (!res.ok) {
          console.warn('[SessionInit] セッションAPIレスポンス異常: status =', res.status)
          return
        }

        const data = await res.json()
        console.log('[SessionInit] APIレスポンスデータ:', data)

        const sessionId = data.session_id
        console.log('[SessionInit] APIレスポンスから取得した sessionId:', sessionId)

        if (sessionId && data.user) {
          console.log('[SessionInit] Reduxにセッション情報を保存します')

          dispatch(setSession({
            sessionId,
            userInfo: {
              sub: data.user.sub,
              name: data.user.preferred_username,
              email: data.user.email,
              locale: data.user.locale,
            },
            loginTime: data.login_time ?? null,
          }))
        } else {
          console.warn('[SessionInit] sessionId または user 情報が不足しています')
        }
      } catch (err) {
        console.error('[SessionInit] セッション情報取得失敗:', err)
      }
    }

    fetchSessionInfo()
  }, [dispatch])
}