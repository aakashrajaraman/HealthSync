import React, { useState } from 'react';
import '../styles/login-styles.css'


import firebase from 'firebase/compat/app';
import 'firebase/compat/firestore';
import 'firebase/compat/auth';

import { useCollectionData } from 'react-firebase-hooks/firestore';




const firebaseConfig = {
    apiKey: "AIzaSyA8nPejv9xijoHDooiF-n6aWTEokgh8A9k",
    authDomain: "healthsync-c9b49.firebaseapp.com",
    projectId: "healthsync-c9b49",
    storageBucket: "healthsync-c9b49.appspot.com",
    messagingSenderId: "109254376080",
    appId: "1:109254376080:web:a4e3f9de4d48126f2f3615",
    measurementId: "G-YB9ZCMTHLH"
  };
  firebase.initializeApp(firebaseConfig);

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
        <div className="form-group user-type-select">
          <label>Login as:     </label>
          <select value={userType} onChange={handleUserTypeChange}>
            <option value="practitioner">Practitioner</option>
            <option value="patient">Patient</option>
          </select>
        </div>
        <input type="email" placeholder="Patient/Pracitioner ID" />
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
