import { createSlice } from "@reduxjs/toolkit";
import { userInfo } from "../../types/user";

const initialState: userInfo = {
  login_id: "",
  name: "",
  nickname: "",
  email: "",
  role: "department_member",
  department_id: 0,
  isLogined: false,
  token: "",
};

const userInfoSlice = createSlice({
  name: "userInfo",
  initialState,
  reducers: {
    setLogin(state, action) {
      state.isLogined = true;
      state.token = action.payload.token;
      state.login_id = action.payload.login_id;
      state.name = action.payload.name;
      state.nickname = action.payload.nickname;
      state.email = action.payload.email;
      state.role = action.payload.role;
      state.department_id = action.payload.department_id;
    },
    setLogout(state) {
      state.isLogined = false;
      state.token = "";
      state.login_id = "";
      state.name = "";
      state.nickname = "";
      state.email = "";
      state.role = "department_member";
      state.department_id = 0;
    },
    readFromLocalStorage(state) {
      const userInfo = localStorage.getItem("userInfo");
      if (userInfo) {
        const parsedUserInfo = JSON.parse(userInfo);
        state.isLogined = true;
        state.token = parsedUserInfo.token;
        state.login_id = parsedUserInfo.login_id;
        state.name = parsedUserInfo.name;
        state.nickname = parsedUserInfo.nickname;
        state.email = parsedUserInfo.email;
        state.role = parsedUserInfo.role;
        state.department_id = parsedUserInfo.department_id;
      }
    },
    setLocalStorage(state) {
      localStorage.setItem("userInfo", JSON.stringify(state));
    },
  },
});

export const { setLogin, setLogout, readFromLocalStorage } =
  userInfoSlice.actions;
export default userInfoSlice.reducer;
