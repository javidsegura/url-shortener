import { useState } from 'react';
import LogInForm from './log_in';
import RegisterForm from './register';
import { GoogleAuthButton } from './federated_providers/federated-providers';

export default function AuthForm() {
  const [registerActive, setRegisterActive] = useState(true);

  return (
    <div
      id="main-space"
      className="flex items-center justify-center w-full h-full bg-gradient-to-br from-gray-50 to-gray-100"
    >
      <div className="flex flex-col w-[400px] bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
        <h1 className="text-3xl font-semibold text-center mb-6 text-gray-800">
          {registerActive ? 'Create an account' : 'Welcome back'}
        </h1>

        <div
          id="manual-form-with-federated-providers"
          className="flex flex-col space-y-4"
        >
          <div id="form-layout">
            {registerActive ? (
              <RegisterForm setRegisterActive={setRegisterActive} />
            ) : (
              <LogInForm setRegisterActive={setRegisterActive} />
            )}
          </div>

          <div className="relative flex items-center my-2">
            <div className="flex-grow border-t border-gray-300"></div>
            <span className="px-3 text-sm text-gray-500 bg-white">or</span>
            <div className="flex-grow border-t border-gray-300"></div>
          </div>

          <GoogleAuthButton />
        </div>

        <p
          className="mt-6 text-center text-sm text-gray-600 hover:text-primary-600 cursor-pointer transition-colors"
          onClick={() => setRegisterActive(!registerActive)}
        >
          {registerActive ? (
            <>
              Already have an account?{' '}
              <u className="font-medium">Log in here</u>
            </>
          ) : (
            <>
              Don’t have an account?{' '}
              <u className="font-medium">Register here</u>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
