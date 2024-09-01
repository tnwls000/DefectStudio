import axios from 'axios';
import { signUpFormType } from '../types/signup';

export const signupHTTP = async (data: signUpFormType) => {
  try {
    const response = axios.post('http://localhost:4000/signup', data);
    return response;
  } catch (error) {
    throw new Error('Signup failed');
  }
};
