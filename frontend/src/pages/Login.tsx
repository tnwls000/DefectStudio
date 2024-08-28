const Login = () => {
  return (
    <div className="relative overflow-hidden w-full min-h-screen flex flex-row">
      {/* 움직이는 화면 넣는 곳 */}
      <section className="w-1/2 h-screen hidden lg:block bg-slate-400"></section>

      {/* 로그인 폼 */}
      <section className="w-full lg:w-1/2 flex flex-col justify-center items-center">
        <p className="text-3xl font-black text-center text-black mb-6">Welcome to Defect Studio</p>
        <p className="text-base text-center mb-6">
          <span className="text-base text-black">Don’t have an account? </span>
          <span className="text-base font-black text-[#6200ea]">Sign up for free</span>
        </p>
        {/* Id */}
        <input
          type="text"
          id="Username"
          name="Username"
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
          required
        />
        <button className="w-[400px] h-[50px] rounded-[100px] bg-[#6200ea] text-lg font-black text-white mb-10">
          Log in
        </button>
        {/* or */}
        <div className="w-[350px] h-[37px] my-4 relative">
          <svg
            width={350}
            height={1}
            viewBox="0 0 350 1"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="absolute left-[-1px] top-4"
            preserveAspectRatio="none"
          >
            <line y1="0.5" x2={350} y2="0.5" stroke="#CCCCCC" />
          </svg>
          <div className="w-[53px] h-[37px] absolute left-[147px] top-[-1px] bg-white" />
          <p className="absolute left-[161px] top-[5px] text-base text-left text-[#696969]">OR</p>
        </div>
        {/* Google Login */}
        <div className="w-[350px] h-[50px] relative">
          <div className="w-[350px] h-[50px] absolute left-[-1px] top-[-1px] rounded-[100px] border border-[#ccc]" />
          <p className="absolute left-[106px] top-3 text-base text-left text-black">Log in with Google</p>
          <img src={'./src/assets/google.svg'} className="w-5 h-5 absolute left-[19px] top-3.5 object-contain" />
        </div>
      </section>
    </div>
  );
};

export default Login;
