import axios from "axios";
import { signUpFormType } from "../types/user";
import apiServer from "./apiSERVER";

export const signupHTTP = async (data: signUpFormType) => {
  try {
    const response = axios.post(
      apiServer + "api/members/signup",
      JSON.stringify(data),
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    return response;
  } catch (error) {
    throw new Error(error as string);
  }
};
