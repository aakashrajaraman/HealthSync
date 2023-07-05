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
    return render_template('clinicSignUp.html')
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
    render_template('clinicSignUp.html')



if __name__ == '__main__':
    app.run(port=3000, debug=True)