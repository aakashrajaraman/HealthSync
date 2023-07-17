# create flask app
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
from dotenv import load_dotenv
import os
from google.cloud import storage
from itertools import chain
import re
import pickle
import json
import numpy as np

app = Flask(__name__)

# Load the rf model using pickle
with open("final_rf_model.pkl", "rb") as file:
    loaded_rf_model = pickle.load(file)

# Load the specialized_dict from JSON
with open("disease_specialist_dict.json", "r") as file:
    loaded_specialized_dict = json.load(file)

# Load the prediction_encoder classes from JSON
with open("encoder_data.json", "r") as file:
    encoder_data = json.load(file)

with open("X.pkl", "rb") as file:
    X = pickle.load(file)

symptoms = X.columns.values

# Creating a symptom index dictionary to encode the
# input symptoms into numerical form
symptom_index = {}
for index, value in enumerate(symptoms):
    symptom = " ".join([i.capitalize() for i in value.split("_")])
    symptom_index[symptom] = index

data_dict = {
    "symptom_index": symptom_index,
    "prediction_classes": encoder_data,
}

# Function to convert string to camel case format
def to_camel_case(string):
    return re.sub(r"(?:^|_)(\w)", lambda x: x.group(1).capitalize(), string)







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
                        session['name'] = user_data['name']
                        session['date'] = user_data['date']
                        session['user_id'] = doc.id
                        session['username'] = user_data['username']
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




@app.route('/userRedir', methods =['POST', 'GET'])
def userRedir():
    return render_template('userSignUp.html')

@app.route('/patientRedir', methods =['POST', 'GET'])
def patientRedir():
    name = session['name']
    age = current_date-datetime.datetime.strptime(session['date'], '%m%d%Y').date()
    years = age.days//365
    return render_template('patient_dashboard.html', name = name, age = years)

@app.route('/clinicRedir', methods =['POST', 'GET'])
def clinicRedir():
    specialties = ['Dermatology', 'Allergology', 'Gastroenterology', 
                   'Hepatology', 'Infectious Diseases', 'Endocrinology', 
                   'Pulmonology', 'Cardiology', 'Neurology', 'Orthopedics', 
                   'Internal Medicine', 'Proctology', 'Vascular Surgery', 
                   'Rheumatology', 'Otolaryngology', 'Urology']
    
    return render_template('clinicSignUp.html', specialties = specialties)

@app.route('/uploadRedir', methods =['POST', 'GET'])
def uploadRedir():
    return render_template('upload.html')


@app.route('/userSignUp', methods =['POST'])
def userSignUp():
    print('usershere')
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
    gender = request.form['gender']
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
        'checkbox_values': checkbox_values,
        'gender': gender
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
    pdf = request.files['file']
    metadata = request.form['metadata']
    name = request.form['name']
    bucket = client.get_bucket(bucket_path)
    path = session['username']+'/'+name+'.pdf'
    print(path)
    blob = bucket.blob(path)
    
    
    blob.content_disposition = 'inline'
    blob.metadata = {'metadata': metadata}

    blob.upload_from_file(pdf)  

    return render_template('patient_dashboard.html')




@app.route('/showDocs', methods = ['POST', 'GET'])
def showDocs():
    user_id = session['user_id']
    bucket = client.get_bucket(bucket_path)
    blobs = bucket.list_blobs(prefix='aakashrajaraman/') 
    prefixes = set()
    toBeRendered =[]

    for blob in chain(*blobs.pages):
        prefixes.add(blob.name.split('/')[0])
        if blob.name.endswith('.pdf'):
            pdf_name = blob.name
            pdf_link = f"https://storage.googleapis.com/{bucket_path}/{blob.name}"
            metadata = blob.metadata
            tbu = {'pdf_name': pdf_name, 'pdf_link': pdf_link, 'metadata': metadata}
            toBeRendered.append(tbu)
        
    return render_template('yourDocs.html',toBeRendered = toBeRendered)



@app.route("/recommender", methods=["GET", "POST"])
def reccomender():
    if request.method == "POST":
        symptom1 = request.form.get("symptom1")
        symptom2 = request.form.get("symptom2")
        symptom3 = request.form.get("symptom3")

        symptoms = [to_camel_case(symptom1), to_camel_case(symptom2), to_camel_case(symptom3)]
        input_data = [0] * len(data_dict["symptom_index"])
        for symptom in symptoms:
            index = data_dict["symptom_index"].get(symptom)
            if index is not None:
                input_data[index] = 1

        input_data = np.array(input_data).reshape(1, -1)
        final_prediction = data_dict["prediction_classes"][loaded_rf_model.predict(input_data)[0]]
        specialist_info = loaded_specialized_dict.get(final_prediction)
        if specialist_info is None:
            specialist_department = "Unknown"
            severity = "Unknown"
            observed_symptoms = []
        else:
            specialist_department = specialist_info.get("department", "Unknown")
            severity = specialist_info.get("severity", "Unknown")
            observed_symptoms = specialist_info.get("observed_symptoms", [])

        response = {
            "suspected_disease": final_prediction,
            "specialist_department": specialist_department,
            "severity": severity,
            "observed_symptoms": observed_symptoms
        }

        return render_template("result.html", **response)

    return render_template("recommender_html.html")





if __name__ == '__main__':
    app.run(port=3000, debug=True)