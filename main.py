# create flask app
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
from dotenv import load_dotenv
import os
from google.cloud import storage

load_dotenv()
path = os.getenv('FIREBASE_KEY_PATH')
bucket_path = "healthsync-c9b49.appspot.com"
current_date = datetime.date.today()



cred  = credentials.Certificate(path)
firebase_admin.initialize_app(cred)
client = storage.Client.from_service_account_json(path)




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
        query = user_ref.where('username', '==', id).limit(1).stream()
        if query:
            for doc in query:
                    user_data = doc.to_dict()
                    if user_data['password'] == password:
                        session['user_id'] = doc.id
                        print(session['user_id'])

                        if userType == 'patient':
                            #get info of patient to render on page
                            name = user_data['name']
                            age = current_date-datetime.datetime.strptime(user_data['date'], '%m%d%Y').date()
                            years = age.days//365
                            print(years)






                            return render_template('patient_dashboard.html', name = name, age = years)
                        elif userType == 'clinic':
                            return render_template('clinic_dashboard.html')
                    else:#wrong password
                        return render_template('login.html')
        else:#wrong username
            return render_template('login.html')
                
#create route for protected 
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('login.html')
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

    foldername= username
    bucket = client.get_bucket(bucket_path)
    blob = bucket.blob(foldername+'/')
    blob.upload_from_string('')



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



@app.route('/upload', methods = ['POST'])
def upload():
    pdf = request.files['pdf_file']
    bucket = client.get_bucket(bucket_path)
    blob = bucket.blob(f'kashkash/{pdf.filename}')
    
    
    blob.content_disposition = 'inline'

    blob.upload_from_file(pdf)  

    return render_template('login.html')



if __name__ == '__main__':
    app.run(port=3000, debug=True)