from flask import Flask, render_template, request
import joblib
import pandas as pd
import mysql.connector

app = Flask(__name__)

# Load model
pipeline = joblib.load('models/telecom_pipeline.pkl')
       
def save_prediction(
    intl_calls,
    intl_charge,
    day_mins,
    day_charge,
    eve_mins,
    eve_charge,
    night_mins,
    night_charge,
    customer_calls,
    intl_plan,
    churn_prediction,
    churn_probability):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shravani@8668",
        database="tele_churn_dashboard"
    )

    cursor = conn.cursor()
    
    sql = """
INSERT INTO tele_churn_predictions(
    intl_calls,
    intl_charge,
    day_mins,
    day_charge,
    eve_mins,
    eve_charge,
    night_mins,
    night_charge,
    customer_calls,
    intl_plan,
    churn_prediction,
    churn_probability
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

    values = (
    intl_calls,
    intl_charge,
    day_mins,
    day_charge,
    eve_mins,
    eve_charge,
    night_mins,
    night_charge,
    customer_calls,
    intl_plan,
    churn_prediction,
    churn_probability
)

    cursor.execute(sql, values)
    conn.commit()

    cursor.close()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    intl_calls = float(request.form["intl_calls"])
    intl_charge = float(request.form["intl_charge"])
    day_mins = float(request.form["day_mins"])
    day_charge = int(request.form["day_charge"])
    eve_mins = float(request.form["eve_mins"])
    eve_charge = int(request.form["eve_charge"])
    night_mins = int(request.form["night_mins"])
    night_charge = float(request.form["night_charge"])
    customer_calls = float(request.form["customer_calls"])
    intl_plan = float(request.form["intl_plan"])
   
   

    data = pd.DataFrame({
        "intl_calls":[intl_calls],
        "intl_charge":[intl_charge],
        "day_mins":[day_mins],
        "day_charge":[day_charge],
        "eve_mins":[eve_mins],
        "eve_charge":[eve_charge],
        "night_mins":[night_mins],
        "night_charge":[night_charge],
        "customer_calls":[customer_calls],
        "intl_plan":[intl_plan]
    
    })


    prediction = pipeline.predict(data)[0]
    probability = pipeline.predict_proba(data)[0][1]

    if prediction == 1:
        result = "Customer has not left the company"
    else:
        result = "Customer has left the company"

    save_prediction(
        intl_calls,
        intl_charge,
        day_mins,
        day_charge,
        eve_mins,
        eve_charge,
        night_mins,
        night_charge,
        customer_calls,
        intl_plan,
        result,
        probability)
    
    return render_template(
        "index.html",
        prediction_text=result
    )

    

if __name__ == "__main__":
    app.run(debug=True)

