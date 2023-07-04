# create flask app
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore



cred  = credentials.Certificate(r"D:\Backup\Desktop\programs\HealthSync\key.json")
firebase_admin.initialize_app(cred)




app = Flask(__name__)
app.secret_key = "HealthSync"

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
        user_ref = firestore.client().collection(collection)
        query = user_ref.where('id', '==', id).limit(1).stream()
        for doc in query:
                user_data = doc.to_dict()
                if user_data['password'] == password:
                    session['user_id'] = doc.id
                    
                    #return redirect(url_for('protected'))
                
    else:
        print("can't find form inputs")
            


    return render_template('login.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)