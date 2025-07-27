// store/quotationsSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

export interface QuotationSummary {
  quoteId: string
  productType: string
  createdAt: string
}

export interface QuotationDetail extends QuotationSummary {
  detail: string // 実際には詳細型に
}

interface QuotationsState {
  list: QuotationSummary[]
  selected: QuotationDetail | null
  isLoading: boolean
}

const initialState: QuotationsState = {
  list: [],
  selected: null,
  isLoading: false,
}

const quotationsSlice = createSlice({
  name: 'quotations',
  initialState,
  reducers: {
    setQuotations(state, action: PayloadAction<QuotationSummary[]>) {
      state.list = action.payload
    },
    setSelectedQuotation(state, action: PayloadAction<QuotationDetail>) {
      state.selected = action.payload
    },
    setQuotationLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload
    },
  },
})

export const {
  setQuotations,
  setSelectedQuotation,
  setQuotationLoading,
} = quotationsSlice.actions

export default quotationsSlice.reducer