# create flask app
from flask import Flask, render_template, request, redirect, url_for, session, flash
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
import torch

os.environ['USE_TORCH'] = '1'

from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import io 
predictor = torch.load(r"D:\Backup\Desktop\programs\HealthSync\text_extraction_model.pth")
clinic_data = {}
global userType
apps = []
app = Flask(__name__)

# Load the rf model using pickle
with open(r"D:\Backup\Desktop\programs\HealthSync\final_rf_model.pkl", "rb") as file:
    loaded_rf_model = pickle.load(file)

# Load the specialized_dict from JSON
with open(r"D:\Backup\Desktop\programs\HealthSync\disease_specialist_dict.json", "r") as file:
    loaded_specialized_dict = json.load(file)

# Load the prediction_encoder classes from JSON
with open("D:\Backup\Desktop\programs\HealthSync\encoder_data.json", "r") as file:
    encoder_data = json.load(file)

with open(r"D:\Backup\Desktop\programs\HealthSync\X.pkl", "rb") as file:
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
                        if userType == 'patient':
                            session['date'] = user_data['date']
                        session['user_id'] = doc.id
        
                        if userType == 'patient':
                            #get info of patient to render on page
                            name = user_data['name']
                            age = current_date-datetime.datetime.strptime(user_data['date'], '%m%d%Y').date()
                            years = age.days//365
                            gender = user_data['gender']
                            session['userType'] = 'patient'
                            session['username'] = user_data['username']
                            session['phone'] = user_data['phone']
                            session['address'] = user_data['address']
                            session['user_bio'] = user_data['user_bio']
                            session['gender'] = user_data['gender']
                            session['user_email'] = user_data['user_email']
                            user_bio = user_data['user_bio']

                            return render_template('patient_dashboard.html', name = name, age = years, gender = gender, user_bio = user_data['user_bio'])
                        elif userType == 'clinic':
                            #get info of clinic to render on page
                            name = user_data['name']
                            username = user_data['username']
                            doctors = user_data['doctors']
                            session['userType'] = 'clinic'
                            total_patients = 0
                            upcoming_patients = 0


                            appointmentsDB = firestoreDB.collection('appointments')
                            appointments = appointmentsDB.where('clinic', '==', username).stream()
                            
                            
                            for doc in appointments:
                                app_data = doc.to_dict()
                                app_date = app_data.get('time')
                                findate = datetime.datetime.strptime(app_date, '%d-%m-%Y %I:%M %p').date()
                                if findate > current_date:
                                    upcoming_patients += 1
                                    patient_username = app_data.get('patient')
                                    if patient_username:
                                        total_patients += 1
                                        patient_doc = firestoreDB.collection('patients').where('username', '==', patient_username).limit(1).stream()
                                        patient_doc = list(patient_doc)
                                        if patient_doc:
                                            app_data['patient_name'] = patient_doc[0].to_dict().get('name')
                                            days= current_date-datetime.datetime.strptime(patient_doc[0].to_dict().get('date'), '%m%d%Y').date()
                                            years = days.days//365
                                            app_data['p_username']= patient_doc[0].to_dict().get('username')
                                            app_data['patient_age'] = years
                                    apps.append(app_data)
                                
                            session['apps'] = apps
                            clinic_data = {
                                "name": name,
                                "doctors": doctors,
                                "total_patients": int(total_patients),
                                "upcoming_patients": int(upcoming_patients),
                                "current_date": current_date.strftime("%d-%m-%Y"),
                            }
                            session['clinic_data'] = clinic_data
                            
                            return render_template('clinic_dashboard.html', clinic_data = clinic_data, appointments = apps)
            else:#wrong password
                return render_template('login.html')
        else:#wrong username
            return render_template('login.html')
                
#create route for protected 
@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')




@app.route('/userRedir', methods =['POST', 'GET'])
def userRedir():
    return render_template('userSignUp.html')

@app.route('/patientRedir', methods =['POST', 'GET'])
def patientRedir():
    name = session['name']
    user_bio = session['user_bio']
    age = current_date-datetime.datetime.strptime(session['date'], '%m%d%Y').date()
    years = age.days//365
    return render_template('patient_dashboard.html', name = name, age = years, user_bio = user_bio, gender = session['gender'])

@app.route('/clinicRedir', methods =['POST', 'GET'])
def clinicRedir():
    specialties = ['Dermatology', 'Allergology', 'Gastroenterology', 
                   'Hepatology', 'Infectious Diseases', 'Endocrinology', 
                   'Pulmonology', 'Cardiology', 'Neurology', 'Orthopedics', 
                   'Internal Medicine', 'Proctology', 'Vascular Surgery', 
                   'Rheumatology', 'Otolaryngology', 'Urology']
    
    return render_template('clinicSignUp.html', specialties = specialties)
@app.route('/dashRedir', methods =['POST', 'GET'])
def dashRedir():
    clinic_data = session['clinic_data']
    apps = session['apps']
    return render_template('clinic_dashboard.html', clinic_data = clinic_data, appointments = apps)
@app.route('/uploadRedir', methods =['POST', 'GET'])
def uploadRedir():
    return render_template('upload.html')

@app.route('/recRedir', methods =['POST', 'GET'])
def recRedir():
    response = {}
    return render_template('recommender_html.html', response = response)


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
    gender = request.form['gender']
    checkbox_values = request.form.getlist('checkbox')
    #check firestoredb patients collection to see if username/email already exists. if yes, render the register page with an error message.
    phone = int(phone)
    #validation
    patientRef = firestoreDB.collection('patients')
    #username
    query = patientRef.where('username', '==', username).limit(1).stream()
    if len(list(query)) > 0 :
        flash('Username already exists')
        return redirect(url_for('userRedir'))
    #user_email
    query = patientRef.where('user_email', '==', user_email).limit(1).stream()
    if len(list(query)) > 0 :
        flash('User email already exists')
        return redirect(url_for('userRedir'))
    #phone
    query = patientRef.where('phone', '==', phone).limit(1).stream()
    if len(list(query)) > 0 :
        flash('Phone number already exists')
        return redirect(url_for('userRedir'))
    #aadhaar
    query = patientRef.where('aadhaar', '==', aadhaar).limit(1).stream()
    if len(list(query)) > 0 :
        flash('Aadhaar already exists')
        return redirect(url_for('userRedir'))
    foldername= username
    bucket = client.get_bucket(bucket_path)
    blob = bucket.blob(foldername+'/')
    blob.upload_from_string('')
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
    clinicRef = firestoreDB.collection('clinics')
    query = clinicRef.where('username', '==', username).limit(1).stream()
    if len(list(query)) > 0 :
        flash('Username already exists')
        return redirect(url_for('clinicRedir'))
    #user email
    query = clinicRef.where('email', '==', email).limit(1).stream()
    if len(list(query)) > 0 :
        flash('User email already exists')
        return redirect(url_for('clinicRedir'))
    #phone
    query = clinicRef.where('phone', '==', phone).limit(1).stream()
    if len(list(query)) > 0 :
        flash('Phone number already exists')
        return redirect(url_for('clinicRedir'))




    firestoreDB.collection('clinics').add(clinic_data)
    return render_template('login.html')

@app.route('/ocr', methods = ['POST'])
@app.route('/upload', methods = ['POST'])
def upload():
    pdf = request.files['file']
    metadata = request.form['metadata']
    name = request.form['name']
    bucket = client.get_bucket(bucket_path)
    path = session['username']+'/'+name+'.pdf'
    
    blob = bucket.blob(path)
    
    
    blob.content_disposition = 'inline'
    blob.metadata = {'metadata': metadata}

    blob.upload_from_file(pdf)  

    return render_template('patient_dashboard.html')




@app.route('/profile', methods = ['POST', 'GET'])
def profile():
    if session['userType'] == 'patient':
        name = session['name']
        email = session['user_email']
        phone = session['phone']
        age = current_date-datetime.datetime.strptime(session['date'], '%m%d%Y').date()
        age = age.days//365
        address = session['address']
        bio = session['user_bio']
        gender = session['gender']

        patient_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'age': age,
            'address': address,
            'bio': bio,
            'gender': gender
        }
        username = session['username']
        bucket = client.get_bucket(bucket_path)
        blobs = bucket.list_blobs(prefix=username+'/') 
        prefixes = set()
        toBeRendered =[]

        for blob in chain(*blobs.pages):
            prefixes.add(blob.name.split('/')[0])
            if blob.name.endswith('.pdf'):
                pdf_name = blob.name
                pdf_name = pdf_name.split('/')[1]
                pdf_link = f"https://storage.googleapis.com/{bucket_path}/{blob.name}"
                metadata = blob.metadata
                #remove brackets and the word metadata from metadata
                metadata = str(metadata)
                metadata = metadata.replace('metadata', '')
                metadata = metadata.replace('{', '')
                metadata = metadata.replace('}', '')
                metadata = metadata.replace("'", '')
                metadata = metadata.replace(':', '')
                tbu = {'pdf_name': pdf_name, 'pdf_link': pdf_link, 'metadata': metadata}
                toBeRendered.append(tbu)
        return render_template('profile.html', patient_data = patient_data, toBeRendered = toBeRendered)
   
   
    if session['userType'] == 'clinic':
        username = request.args.get('p_username')
        
        patient_doc = firestoreDB.collection('patients').where('username', '==', username).limit(1).stream()
        #get name, email, phone, age in years, address, bio, gender
        patient_doc = list(patient_doc)
        if patient_doc:
            name = patient_doc[0].to_dict().get('name')
            email = patient_doc[0].to_dict().get('user_email')
            phone = patient_doc[0].to_dict().get('phone')
            age = current_date-datetime.datetime.strptime(patient_doc[0].to_dict().get('date'), '%m%d%Y').date()
            years = age.days//365
            address = patient_doc[0].to_dict().get('address')
            bio = patient_doc[0].to_dict().get('user_bio')
            gender = patient_doc[0].to_dict().get('gender')
        patient_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'age': years,
            'address': address,
            'bio': bio,
            'gender': gender
        }
        bucket = client.get_bucket(bucket_path)
        blobs = bucket.list_blobs(prefix=username+'/') 
        prefixes = set()
        toBeRendered =[]

        for blob in chain(*blobs.pages):
            prefixes.add(blob.name.split('/')[0])
            if blob.name.endswith('.pdf'):
                pdf_name = blob.name
                pdf_name = pdf_name.split('/')[1]
                pdf_link = f"https://storage.googleapis.com/{bucket_path}/{blob.name}"
                metadata = blob.metadata
                metadata = str(metadata)
                metadata = metadata.replace('metadata', '')
                metadata = metadata.replace('{', '')
                metadata = metadata.replace('}', '')
                metadata = metadata.replace("'", '')
                metadata = metadata.replace(':', '')
                tbu = {'pdf_name': pdf_name, 'pdf_link': pdf_link, 'metadata': metadata}
                toBeRendered.append(tbu)
        return render_template('viewProfileClinic.html', patient_data = patient_data, toBeRendered = toBeRendered)

@app.route('/showDocs', methods = ['POST', 'GET'])
def showDocs():
    username = session['username']
    bucket = client.get_bucket(bucket_path)
    blobs = bucket.list_blobs(prefix=username+'/') 
    prefixes = set()
    toBeRendered =[]

    for blob in chain(*blobs.pages):
        prefixes.add(blob.name.split('/')[0])
        if blob.name.endswith('.pdf'):
            pdf_name = blob.name
            pdf_link = f"https://storage.googleapis.com/{bucket_path}/{blob.name}"
            metadata = blob.metadata
            #only get pdfname from '/' onwards
            pdf_name = pdf_name.split('/')[1]
            metadata = str(metadata)
            metadata = metadata.replace('metadata', '')
            metadata = metadata.replace('{', '')
            metadata = metadata.replace('}', '')
            metadata = metadata.replace("'", '')
            metadata = metadata.replace(':', '')

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

        

        clinics = firestoreDB.collection('clinics').where('specialties', 'array_contains', specialist_department).stream()
        clinic_list = []
        for clinic in clinics:
            clinic_list.append(clinic.to_dict())
        response = {
        "suspected_disease": final_prediction,
        "specialist_department": specialist_department,
        "severity": severity,
        "observed_symptoms": observed_symptoms,
        "clinic_data": clinic_list  # Add the clinic data to the response dictionary
    }



        return render_template("recommender_html.html", response = response)

    return render_template("recommender_html.html")

@app.route('/ocr', methods = ['POST'])
def ocr():
    pdf = request.files['file']
    name = request.form['name']

    bucket = client.get_bucket(bucket_path)
    path = session['username']+'/'+name+'.pdf'
    
    blob = bucket.blob(path)

    blob.content_disposition = 'inline'
     
    temp_filename = 'temp.pdf'
    pdf.save(temp_filename)

    doc = DocumentFile.from_pdf(temp_filename)
    result = predictor(doc)
    synthetic_pages = result.synthesize() #synthesized image output
    extracted_text = result.export()

    extracted_words = {}
    for page_info in extracted_text['pages']:
        for block in page_info['blocks']:
            for line in block['lines']:
                for word in line['words']:
                    extracted_words[word['value']] = word['confidence']

    blob.metadata = {'metadata': extracted_words}

    with open(temp_filename, 'rb') as file:
        blob.upload_from_file(file)

    os.remove(temp_filename)

    return render_template('ocr.html')
    
@app.route('/book-appointment', methods = ['POST', 'GET'])
def bookAppointment():
    clinic_username = request.form['clinic_username']
    patient_username = session['username']
    time = request.form['time']
    reason = request.form['reason']
    symptoms = request.form['symptoms']
    department = request.form['department']
    #convert time to time
    appointment_time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M')

    # Format the datetime object to include date, time, and AM/PM.
    formatted_time = appointment_time.strftime('%d-%m-%Y %I:%M %p')


    appointmentData = {
        'clinic': clinic_username,
        'patient': patient_username,
        'time': formatted_time,
        'reason': reason,
        'symptoms': symptoms,
        "department": department
    }
    firestoreDB.collection('appointments').add(appointmentData)
    return render_template('patient_dashboard.html')


if __name__ == '__main__':
    app.run(port=3000, debug=True)