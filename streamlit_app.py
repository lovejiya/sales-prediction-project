import streamlit as st
import pandas as pd
import requests
import time

PREDICT_API_URL = "http://127.0.0.1:5001/predict"
BULK_PREDICT_API_URL = "http://127.0.0.1:5001/bulk_predict"
INGEST_API_URL = "http://127.0.0.1:5001/ingest"

st.title("Sales Prediction App")

# ---------------- Manual Prediction ----------------
st.header("Manual Prediction")
store_id = st.number_input("Store ID", min_value=1, step=1)
date = st.date_input("Date")
promo = st.selectbox("Promo", [0, 1])
stateholiday = st.selectbox("State Holiday", ["0", "a", "b", "c"])
schoolholiday = st.selectbox("School Holiday", [0, 1])

if st.button("Predict"):
    payload = {
        "store_id": int(store_id),
        "date": str(date),
        "promo": int(promo),
        "stateholiday": stateholiday,
        "schoolholiday": int(schoolholiday)
    }
    response = requests.post(PREDICT_API_URL, json=payload)
    if response.status_code == 200:
        result = response.json()
        if "prediction" in result:
            st.success(f"Predicted Sales: {result['prediction']:.2f}")
        else:
            st.error(result.get("error", "Unknown error"))
    else:
        st.error("API error")

# ---------------- Bulk Prediction ----------------
st.header("Bulk Prediction (CSV Upload)")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Preview:")
    st.dataframe(df.head())

    columns = df.columns.tolist()
    store_col = st.selectbox("Select Store Column", ["store_id", "None"] + columns)
    date_col = st.selectbox("Select Date Column", ["date", "None"] + columns)
    promo_col = st.selectbox("Select Promo Column", ["promo", "None"] + columns)
    stateholiday_col = st.selectbox("Select State Holiday Column", ["stateholiday", "None"] + columns)
    schoolholiday_col = st.selectbox("Select School Holiday Column", ["schoolholiday", "None"] + columns)

    if st.button("Predict CSV"):
        predictions = []
        progress_bar = st.progress(0)
        total = len(df)

        for i, row in df.iterrows():
            payload = {
                "store_id": int(row[store_col]) if store_col != "None" else int(row.get("store_id", row.get("Store", 1))),
                "date": str(row[date_col]) if date_col != "None" else str(row.get("date", row.get("Date", "2023-01-01"))),
                "promo": int(row[promo_col]) if promo_col != "None" else int(row.get("promo", row.get("Promo", 0))),
                "stateholiday": str(row[stateholiday_col]) if stateholiday_col != "None" else str(row.get("stateholiday", row.get("StateHoliday", "0"))),
                "schoolholiday": int(row[schoolholiday_col]) if schoolholiday_col != "None" else int(row.get("schoolholiday", row.get("SchoolHoliday", 0)))
            }
            try:
                response = requests.post(PREDICT_API_URL, json=payload)
                if response.status_code == 200:
                    res = response.json()
                    predictions.append(res.get("prediction", None))
                else:
                    predictions.append(None)
            except:
                predictions.append(None)

            progress_bar.progress((i + 1) / total)

        df["prediction"] = predictions
        st.write("Results:")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results", csv, "predictions.csv", "text/csv")

# ---------------- Bulk Ingest ----------------
st.header("Bulk Ingest CSV to Database")
ingest_file = st.file_uploader("Upload CSV to Ingest", type=["csv"], key="ingest")
if ingest_file:
    ingest_df = pd.read_csv(ingest_file)
    if st.button("Ingest CSV"):
        data_json = ingest_df.to_dict(orient="records")
        response = requests.post(INGEST_API_URL, json=data_json)
        if response.status_code == 200:
            st.success("Data ingested successfully")
        else:
            st.error(response.json().get("error", "Ingest failed"))