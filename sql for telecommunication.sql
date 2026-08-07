create database tele_churn_dashboard;

USE tele_churn_dashboard;

CREATE TABLE tele_churn_predictions (
    id  int AUTO_INCREMENT  PRIMARY KEY,
    intl_calls FLOAT,
    intl_charge FLOAT,
    day_mins FLOAT,
    day_charge FLOAT,
    eve_mins FLOAT,
    eve_charge FLOAT,
    night_mins FLOAT,
    night_charge FLOAT,
    customer_calls FLOAT,
    intl_plan FLOAT,
   churn_prediction VARCHAR(50),
   churn_probability float,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from tele_churn_predictions;

