import { useForm } from "react-hook-form";
import { loginRequest } from "../../api/loginHTTP";
import { useState } from "react";
import { message } from "antd";
interface loginForm {
  username: string;
  password: string;
}

const onSubmit = async (
  data: loginForm,
  setErrorMessage: React.Dispatch<React.SetStateAction<string>>
) => {
  try {
    const response = await loginRequest(data.username, data.password);
    console.log(response);
    setErrorMessage("");
  } catch (error) {
    message.error("Login failed Try again later");
  }
};

const LoginForm = () => {
  const [errorMessage, setErrorMessage] = useState("");
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<loginForm>();

  return (
    <>
      <form onSubmit={handleSubmit((data) => onSubmit(data, setErrorMessage))}>
        {/* Id */}
        <input
          type="text"
          id="username"
          {...register("username", { required: true })}
          className="mt-3 mb-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-[400px] h-[50px] p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="Username"
          required
        />
        {/* pw */}
        <input
          type="password"
          id="password"
          {...register("password", { required: true })}
          className="mt-1 mb-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-[400px] h-[50px]  p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="Password"
          autoComplete="off"
          required
        />
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-[400px] h-[50px] rounded-[100px] bg-[#6200ea] text-lg font-black text-white "
        >
          {isSubmitting ? "Logging in..." : "Login"}
        </button>
        {errorMessage && <div style={{ color: "red" }}>{errorMessage}</div>}
      </form>
    </>
  );
};

export default LoginForm;
