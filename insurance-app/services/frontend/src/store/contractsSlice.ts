// store/contractsSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

export interface ContractSummary {
  contractId: string
  productName: string
  status: string
}

export interface ContractDetail extends ContractSummary {
  details: string // 実際には詳細型に
}

interface ContractsState {
  list: ContractSummary[]
  selected: ContractDetail | null
  isLoading: boolean
  error?: string
}

const initialState: ContractsState = {
  list: [],
  selected: null,
  isLoading: false,
}

const contractsSlice = createSlice({
  name: 'contracts',
  initialState,
  reducers: {
    setContractList(state, action: PayloadAction<ContractSummary[]>) {
      state.list = action.payload
    },
    setSelectedContract(state, action: PayloadAction<ContractDetail>) {
      state.selected = action.payload
    },
    setContractLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload
    },
    setContractError(state, action: PayloadAction<string>) {
      state.error = action.payload
    },
  },
})

export const {
  setContractList,
  setSelectedContract,
  setContractLoading,
  setContractError,
} = contractsSlice.actions

export default contractsSlice.reducer