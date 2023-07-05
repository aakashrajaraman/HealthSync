# create flask app
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
import datetime



cred  = credentials.Certificate(r"D:\Backup\Desktop\programs\HealthSync\key.json")
firebase_admin.initialize_app(cred)




app = Flask(__name__)
app.secret_key = "HealthSync"
firestoreDB = firestore.client()

@app.route('/', methods = ['GET'])
def index():
    return render_template('login.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST' and 'id' in request.form and 'password' in request.form and 'userType' in request.form:
        id = request.form['id']
        password = request.form['password']
        userType = request.form['userType']
        if userType == 'patient':
            collection = "patients"
        elif userType == 'clinic':
            collection = "clinics"
        user_ref = firestoreDB.collection(collection)
        query = user_ref.where('id', '==', id).limit(1).stream()
        for doc in query:
                user_data = doc.to_dict()
                if user_data['password'] == password:
                    session['user_id'] = doc.id
                    
                    #return redirect(url_for('protected'))
                
#create route for protected 
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
#should go to the respective dashboard
    return render_template('login.html')
@app.route('/userRedir', methods =['POST', 'GET'])
def userRedir():
    return render_template('userSignUp.html')
@app.route('/clinicRedir', methods =['POST', 'GET'])
def clinicRedir():
    specialties = ['Dermatology', 'Allergology', 'Gastroenterology', 
                   'Hepatology', 'Infectious Diseases', 'Endocrinology', 
                   'Pulmonology', 'Cardiology', 'Neurology', 'Orthopedics', 
                   'Internal Medicine', 'Proctology', 'Vascular Surgery', 
                   'Rheumatology', 'Otolaryngology', 'Urology']
    
    return render_template('clinicSignUp.html', specialties = specialties)
@app.route('/userSignUp', methods =['POST'])
def userSignUp():
    name = request.form['name']
    username = request.form['username']
    user_email = request.form['user_email']
    password = request.form['password']
    address = request.form['address']
    phone = request.form['phone']
    date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d').date().strftime('%m%d%Y')
    aadhaar = request.form['aadhaar']
    user_bio = request.form['user_bio']
    user_job = request.form['user_job']
    checkbox_values = request.form.getlist('checkbox')
    phone = int(phone)
    patient_data = {
        'name': name,
        'username': username,
        'user_email': user_email,
        'password': password,
        'address': address,
        'phone': phone,
        'date': date,
        'aadhaar': aadhaar,
        'user_bio': user_bio,
        'user_job': user_job,
        'checkbox_values': checkbox_values
    }
    firestoreDB.collection('patients').add(patient_data)
    return render_template('login.html')

@app.route('/clinicSignUp', methods =['POST'])
def clinicSignUp():
    name = request.form['name']
    license = request.form['license']
    address = request.form['address']
    doctors = request.form['doctors'].split(',')
    prim_doc = request.form['primDoc']
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    phone = request.form['phone']
    specialties = request.form.getlist('specialties')

    clinic_data = {
        'name': name,
        'license': license,
        'address': address,
        'username': username,
        'password': password,
        'email': email,
        'phone': phone,
        'doctors': doctors,
        'prim_doc': prim_doc,
        'specialties': specialties
    }

    firestoreDB.collection('clinics').add(clinic_data)
    return render_template('login.html')



if __name__ == '__main__':
    app.run(port=3000, debug=True)