from flask import Flask, render_template, request, jsonify
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

@app.route("/", methods=["GET", "POST"])
def index():
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

if __name__ == "__main__":
    app.run()
