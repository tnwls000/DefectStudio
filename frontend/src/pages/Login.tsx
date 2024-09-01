import { Link } from 'react-router-dom';
import LoginForm from '../components/login/LoginForm';
import OrBar from '../components/login/OrBar';

const Login = () => {
  return (
    <div className="relative overflow-hidden w-full min-h-screen flex flex-row">
      {/* 움직이는 화면 넣는 곳 */}
      <section className="w-1/2 h-screen hidden lg:block bg-slate-400 relative">
        <p className="font-black text-white absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-[50px] ">
          Welcome
          <br />
          to
          <br />
          Defect
          <br />
          Studio
        </p>
      </section>

      {/* 로그인 영역 */}
      <section className="w-full lg:w-1/2 flex flex-col justify-center items-center">
        <p className="text-3xl font-black text-center text-black mb-6">Welcome to Defect Studio</p>
        <p className="text-base text-center mb-6">
          <Link to="/signup">
            <span className="text-base text-black">Don’t have an account? </span>
          </Link>
          <span className="text-base font-black text-[#6200ea]">Sign up for free</span>
        </p>

        <LoginForm />
        <OrBar />

        {/* Google Login */}
        <div className="w-[400px] h-[50px] relative">
          <button className="w-[400px] h-[50px] absolute  rounded-[100px] border border-[#ccc] hover:border-purple-400">
            Log in with Google
          </button>
          <img src={'./src/assets/google.svg'} className="w-5 h-5 absolute left-[19px] top-3.5 object-contain" />
        </div>
      </section>
    </div>
  );
};

export default Login;
