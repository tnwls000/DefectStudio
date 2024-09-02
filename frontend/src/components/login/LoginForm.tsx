interface LoginFormProps {
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void | undefined;
}

const LoginForm = ({ onSubmit }: LoginFormProps) => {
  return (
    <>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          console.log(e.target.username.value, e.target.password.value);
        }}
      >
        {/* Id */}
        <input
          type="text"
          id="username"
          name="username"
          className="mt-3 mb-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-[400px] h-[50px] p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="Username"
          required
        />
        {/* pw */}
        <input
          type="password"
          id="password"
          name="password"
          className="mt-1 mb-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-[400px] h-[50px]  p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="Password"
          autoComplete="off"
          required
        />
        <button
          type="submit"
          className="w-[400px] h-[50px] rounded-[100px] bg-[#6200ea] text-lg font-black text-white "
        >
          Log in
        </button>
      </form>
    </>
  );
};

export default LoginForm;
