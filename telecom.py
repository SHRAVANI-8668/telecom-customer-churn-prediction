from flask import Flask, render_template, request
import joblib
import pandas as pd
import mysql.connector

app = Flask(__name__)

# Load model
pipeline = joblib.load('models/telecom_pipeline.pkl')
       
def save_bulk_predictions(df):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shravani@8668",
        database="tele_churn_dashboard"
    )

    cursor = conn.cursor()
    
    sql = """
INSERT INTO tele_churn_predictions(
    intl_plan,
    intl_calls,
    intl_charge,
    day_mins,
    day_charge,
    eve_charge,
    night_mins,
    customer_calls,
    churn_prediction,
    churn_probability
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

    values = []

    for _, row in df.iterrows():

        values.append((
            row["intl_plan"],
            row["intl_calls"],
            row["intl_charge"],
            row["day_mins"],
            row["day_charge"],
            row["eve_charge"],
            row["night_mins"],
            row["customer_calls"],
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
    'intl_plan',
    'intl_calls',
    'intl_charge',
    'day_mins',
    'day_charge',
    'eve_charge',
    'night_mins',
    'customer_calls'
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
        "Customer likely to Churn"
        if x == 1
        else
        "Customer unlikely to Churn "
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

