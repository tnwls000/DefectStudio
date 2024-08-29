import { configureStore } from '@reduxjs/toolkit';
import levelReducer from './levelSlice';

const store = configureStore({
  reducer: {
    level: levelReducer,
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
