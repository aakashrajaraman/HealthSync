import React, { useState } from 'react';
import '../styles/login-styles.css'

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState('');

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleUserTypeChange = (e) => {
    setUserType(e.target.value);
  };

  const handleLogin = () => {
    // Logic for handling login
  };

  const handleRegistration = () => {
    if (userType === 'patient') {
      // Logic for registering as a patient
    } else if (userType === 'practitioner') {
      // Logic for registering as a practitioner
    }
  };

  return (
    <>
    <h1 className='heading'> HealthSync</h1>
  <div class="container" id="container">
  
  
    <div class="form sign_in">
      <form action="#">
        <h1>Login</h1>
       
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Password" />
        <button className='login'>Login</button>
      </form>
    </div>
    <div class="overlay-container">
      <div class="overlay">
        <div class="overlay-pannel overlay-left">
          <h1>Already have an account</h1>
          <p>Please Login</p>
          <button id="signIn" class="overBtn">SignIn</button>
        </div>
        <div class="overlay-pannel overlay-right">
          <h1>Create Account</h1>
          <p>Start Your Journey with Us</p>
          <button className='clinic-reg'> Onboard Your Clinic</button>
          <button className='patient-reg'> Sign-Up as a Patient</button>
        <button className='practioner-reg'> Sign-Up as a Practioner</button>
        </div>
      </div>
    </div>
  </div>
</>

  );
};

export default LoginPage;
