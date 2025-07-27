// store.ts
import { configureStore } from '@reduxjs/toolkit'
import sessionReducer from './sessionSlice'
import contractsReducer from './contractsSlice'
import notificationsReducer from './notificationSlice' 
import quotationsReducer from './quotationsSlice'

export const store = configureStore({
  reducer: {
    session: sessionReducer,
    contracts: contractsReducer,
    notification: notificationsReducer, 
    quotations: quotationsReducer,
  },
})

// アプリ全体で使う型定義
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch