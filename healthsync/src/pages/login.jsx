import React, { useState, useEffect } from 'react';
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
  const firestore = firebase.firestore();

const LoginPage = () => {
  const [userType, setUserType] = useState('patient');
  
  

  const handleUserTypeChange = (e) => {
    setUserType(e.target.value);
  };

  const handleLogin = (event) => {
    event.preventDefault();
    const id = document.querySelector('#id').value;
    const password = document.querySelector('#password').value;
    let collectionName = '';
    if (userType === 'practitioner') {
      collectionName = 'practitioners';
    }else if(userType === 'patient'){
      collectionName = 'patients';
    }

   const loginInfo = firestore.collection(collectionName);

   //query
   loginInfo.where('id', '==', id).where('password', '==', password).get().then((querySnapshot) => {
    if (querySnapshot.empty) {
      alert('Invalid Credentials');
      //reset form
    } else {
      querySnapshot.forEach((doc) => {
        alert('Login Successful');
        //redirect to dashboard
      });
    
    }
  });



  };

 

 

  return (
    <>
    <h1 className='heading'> HealthSync</h1>
  <div class="container" id="container">
  
  
    <div class="form sign_in">
      <form onSubmit={handleLogin}>
        <h1>Login</h1>
        <div className="form-group user-type-select">
          <label>Login as:     </label>
          <select value={userType} onChange={handleUserTypeChange}>
            <option value="patient">Patient</option>
            <option value="practitioner">Practitioner</option>
          </select>
        </div>
        <input type="text" placeholder="Patient/Pracitioner ID" id = "id" />
        <input type="password" placeholder="Password" id = "password" />
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
