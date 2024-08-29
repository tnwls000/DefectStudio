import { useForm } from 'react-hook-form';
import { signUpFormType } from '../types/signup';
import { signupHTTP } from '../util/signupHTTP';

const Signup = () => {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<signUpFormType>();

  const onSubmit = handleSubmit((data) => {
    signupHTTP(data);
  });

  return (
    <div className="w-full h-full min-h-[1024px] relative overflow-hidden bg-white">
      <p className="absolute left-1/2 top-8 transform -translate-x-1/2 text-2xl sm:text-3xl font-black text-center text-black">
        Welcome to Defect Studio
      </p>
      <form onSubmit={onSubmit} className="flex flex-col absolute top-[100px] left-1/2 transform -translate-x-1/2">
        <input
          {...register('login_id', { required: 'Username is required' })}
          type="text"
          placeholder="loginId"
          className={`w-[90%] min-w-[400px] my-5 max-w-[400px] h-[50px] px-4 rounded-[10px] border ${errors.login_id ? 'border-red-500' : 'border-[#ccc]'} text-sm sm:text-base text-[#808080] focus:outline-none`}
        />
        {errors.login_id && <p className="text-red-500 text-sm">{errors.login_id.message}</p>}

        <input
          {...register('password', { required: 'Password is required' })}
          type="password"
          placeholder="Password"
          className={`w-[90%] min-w-[400px] my-5 max-w-[400px] h-[50px] px-4 rounded-[10px] border ${errors.password ? 'border-red-500' : 'border-[#ccc]'} text-sm sm:text-base text-[#808080] focus:outline-none`}
        />
        {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}

        <input
          {...register('name', { required: 'Nickname is required' })}
          type="text"
          placeholder="Nickname"
          className={`w-[90%] min-w-[400px] my-5 max-w-[400px] h-[50px] px-4 rounded-[10px] border ${errors.name ? 'border-red-500' : 'border-[#ccc]'} text-sm sm:text-base text-[#808080] focus:outline-none`}
        />
        {errors.name && <p className="text-red-500 text-sm">{errors.name.message}</p>}

        <input
          {...register('nickname', { required: 'Nickname is required' })}
          type="text"
          placeholder="Nickname"
          className={`w-[90%] min-w-[400px] my-5 max-w-[400px] h-[50px] px-4 rounded-[10px] border ${errors.nickname ? 'border-red-500' : 'border-[#ccc]'} text-sm sm:text-base text-[#808080] focus:outline-none`}
        />
        {errors.nickname && <p className="text-red-500 text-sm">{errors.nickname.message}</p>}

        <input
          {...register('email', {
            required: 'Email is required',
            pattern: { value: /^\S+@\S+$/i, message: 'Invalid email address' }
          })}
          type="email"
          placeholder="Email"
          className={`w-[90%] min-w-[400px] my-5 max-w-[400px] h-[50px] px-4 rounded-[10px] border ${errors.email ? 'border-red-500' : 'border-[#ccc]'} text-sm sm:text-base text-[#808080] focus:outline-none`}
        />
        {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}

        <button
          type="submit"
          className="w-[90%] min-w-[400px] my-5 max-w-[400px] h-[53px] rounded-[100px] bg-[#6200ea] text-lg font-black text-center text-white focus:outline-none"
        >
          Sign Up
        </button>
      </form>
    </div>
  );
};

export default Signup;
