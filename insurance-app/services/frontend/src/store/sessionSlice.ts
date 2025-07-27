import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

export interface SessionState {
  isLoggedIn: boolean
  sessionId: string | null
  userInfo: {
    sub: string
    name: string
    email: string
    locale?: string
  } | null
  loginTime: string | null
}

// ----------------------------------------------
// localStorage から復元（なければ初期値を返す）
// ----------------------------------------------
const loadSessionFromStorage = (): SessionState => {
  try {
    const raw = localStorage.getItem('session')
    if (!raw) return defaultState
    const parsed = JSON.parse(raw)

    return {
      isLoggedIn: parsed.isLoggedIn ?? false,
      sessionId: parsed.sessionId ?? null,
      userInfo: parsed.userInfo ?? null,
      loginTime: parsed.loginTime ?? null,
    }
  } catch (e) {
    console.warn('[Session] セッション復元失敗:', e)
    return defaultState
  }
}

const defaultState: SessionState = {
  isLoggedIn: false,
  sessionId: null,
  userInfo: null,
  loginTime: null,
}

const initialState: SessionState = loadSessionFromStorage()

const sessionSlice = createSlice({
  name: 'session',
  initialState,
  reducers: {
    setSession: (state, action: PayloadAction<Omit<SessionState, 'isLoggedIn'>>) => {
      state.sessionId = action.payload.sessionId
      state.userInfo = action.payload.userInfo
      state.loginTime = action.payload.loginTime
      state.isLoggedIn = true

      // localStorage に保存
      localStorage.setItem(
        'session',
        JSON.stringify({
          sessionId: state.sessionId,
          userInfo: state.userInfo,
          loginTime: state.loginTime,
          isLoggedIn: state.isLoggedIn,
        })
      )
    },
    clearSession: (state) => {
      state.sessionId = null
      state.userInfo = null
      state.loginTime = null
      state.isLoggedIn = false

      // localStorage から削除
      localStorage.removeItem('session')
    },
  },
})

export const { setSession, clearSession } = sessionSlice.actions
export default sessionSlice.reducer