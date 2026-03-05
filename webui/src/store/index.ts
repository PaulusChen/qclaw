/**
 * Redux/Pinia Store Configuration
 */

import { configureStore } from '@reduxjs/toolkit'
import marketReducer from './slices/marketSlice'
import adviceReducer from './slices/adviceSlice'

export const store = configureStore({
  reducer: {
    market: marketReducer,
    advice: adviceReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
