# create flask app
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
from dotenv import load_dotenv
import os
from google.cloud import storage
from itertools import chain

os.environ['USE_TORCH'] = '1'

from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import io 

load_dotenv()
path = os.getenv('FIREBASE_KEY_PATH')
bucket_path = "healthsync-c9b49.appspot.com"
current_date = datetime.date.today()



cred  = credentials.Certificate(path)
firebase_admin.initialize_app(cred)
client = storage.Client.from_service_account_json(path)

predictor = torch.load("D:\\Jacob's Documents D Drive\\Health Hackathon\\HelathSync-20230713T064444Z-001\\HelathSync\\text_extraction_model.pth")

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

@app.route('/ocr', methods=['POST'])
def ocr():
    file = request.files['file']
    doc = DocumentFile.from_pdf(io.BytesIO(file.read()))
    result = predictor(doc)
    synthetic_pages = result.synthesize() #synthesized image output
    extracted_text = result.export() #json format outpu

if __name__ == '__main__':
    app.run(port=3000, debug=True)
