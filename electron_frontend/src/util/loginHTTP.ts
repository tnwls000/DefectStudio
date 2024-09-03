import axios from "axios";
import apiServer from "./apiSERVER";

export const loginRequest = async (username: string, password: string) => {
  const response = await axios.post(
    apiServer + "api/auth/login",
    { username, password },
    {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    }
  );
  return response;
};
