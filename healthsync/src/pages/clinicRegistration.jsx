import React, { useState, useEffect } from 'react';
import '../regStyles/registrations-css.css'


import firebase from 'firebase/compat/app';
import 'firebase/compat/firestore';
import 'firebase/compat/auth';

const ClinicRegistration = () => {



    return (
        <>


            <div class="container-1">
                <div class="title">Registation</div>
                <form action="#" className='form-1'>
                    <div class="input_box">
                        <span class="details">Clinic Name:</span>
                        <input type="text" placeholder="Clinic Name" required />
                    </div>

                    <div class="input_box">
                        <span class="details">Contact Information:</span>
                        <input type="tel" placeholder="Phone Number" required />
                        <input type="email" placeholder="Email Address" required />
                        <input type="text" placeholder="Physical Address" required />
                    </div>

                    <div class="button">
                        <input type="submit" value="Register" />
                    </div>
                </form>
            </div>

        </>

    );

};

export default ClinicRegistration;