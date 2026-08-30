from flask import Flask, render_template, request
import joblib
import pandas as pd
import mysql.connector


app = Flask(__name__)

# Load model
pipeline = joblib.load('models/bank_pipeline.pkl')

def save_bulk_predictions(df):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shravani@8668",
        database="bank_churn_dashboard"
    )

    cursor = conn.cursor()

    sql = """
    INSERT INTO bank_churn_predictions(
        age,
        contact,
        b_month,
        day_of_week,
        emp_var_rate,
        cons_price_idx,
        cons_conf_idx,
        euribor3m,
        nr_employed,
        job_admin,
        job_blue_collar, 
        job_entrepreneur, 
        job_housemaid,
        job_management, 
        job_retired, 
        job_self_employed, 
        job_services,
        job_student, 
        job_technician, 
        job_unemployed, 
        marital_divorced,
        marital_married, 
        marital_single, 
        poutcome_failure,
        poutcome_nonexistent, 
        poutcome_success,
        churn_prediction,
        churn_probability
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = []

    for _, row in df.iterrows():

        values.append((
            row["age"],
            row["contact"],
            row["b_month"],
            row["day_of_week"],
            row["emp_var_rate"],
            row["cons_price_idx"],
            row["cons_conf_idx"],
            row["euribor3m"],
            row["nr_employed"],
            row["job_admin"],
            row["job_blue_collar"],
            row["job_entrepreneur"],
            row["job_housemaid"],
            row["job_management"],
            row["job_retired"],
            row["job_self_employed"],
            row["job_services"],
            row["job_student"],
            row["job_technician"],
            row["job_unemployed"],
            row["marital_divorced"],
            row["marital_married"],
            row["marital_single"],
            row["poutcome_failure"],
            row["poutcome_nonexistent"],
            row["poutcome_success"],
            row["prediction_text"],
            row["probability"]
            
        ))

    cursor.executemany(sql, values)

    conn.commit()

    cursor.close()
    conn.close()
    
@app.route("/")
def home():

    return render_template("index.html")

    
@app.route("/bulk_predict", methods=["POST"])
def bulk_predict():

    file = request.files["file"]

    if file.filename == "":
        return "No file selected"

    df = pd.read_csv(file)

    # Columns expected by the model
    required_columns = [
        "age","contact",
        "b_month",
        "day_of_week",
        "emp_var_rate",
        "cons_price_idx", 
        "cons_conf_idx",
        "euribor3m",
        "nr_employed",
        "job_admin",
        "job_blue_collar",
        "job_entrepreneur", 
        "job_housemaid",
        "job_management", 
        "job_retired",
        "job_self_employed", 
        "job_services",
        "job_student", 
        "job_technician", 
        "job_unemployed", 
        "marital_divorced",
        "marital_married",
        "marital_single", 
        "poutcome_failure",
        "poutcome_nonexistent", 
        "poutcome_success"
    ]

    # Check columns
    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        return f"Missing columns: {missing_columns}"

    # Select required features
    X = df[required_columns]

    # Predict all customers
    predictions = pipeline.predict(X)

    probabilities = pipeline.predict_proba(X)[:, 1]

    # Add predictions to dataframe
    df["prediction"] = predictions
    df["probability"] = probabilities

    # Convert prediction to readable text
    df["prediction_text"] = df["prediction"].apply(
        lambda x:
        "Customer likely to subscribe"
        if x == 1
        else
        "Customer unlikely to subscribe"
    )
    
    # Save to SQL
    save_bulk_predictions(df)

    return render_template(
        "results.html",
        tables=[
            df.to_html(
                classes="table",
                index=False
            )
        ]
    )
    

if __name__ == "__main__":
    app.run(debug=True)
