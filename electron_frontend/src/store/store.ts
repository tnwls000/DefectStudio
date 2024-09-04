import { configureStore } from "@reduxjs/toolkit";
import levelReducer from "./slices/levelSlice";
import themeReducer from "./slices/themeSlice";

const store = configureStore({
  reducer: {
    level: levelReducer,
    theme: themeReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
