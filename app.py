from flask import Flask, request, jsonify
from db import engine
import pandas as pd
import joblib
import os

model = joblib.load("pipeline.pkl")

app = Flask(__name__)

@app.route("/")
def home():
    return "Sales Prediction API Running!"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        store_id = data["store_id"]
        date = pd.to_datetime(data["date"])
        promo = data.get("promo", 0)
        stateholiday = str(data.get("stateholiday", "0"))
        schoolholiday = data.get("schoolholiday", 0)

        df = pd.DataFrame([{
            "store_id": store_id,
            "date": date,
            "promo": promo,
            "stateholiday": stateholiday,
            "schoolholiday": schoolholiday
        }])
        print(pd.read_sql("SELECT * FROM stores_agg LIMIT 1", engine).columns)
        store_query = f"""
        SELECT store, storetype, assortment, competitiondistance,
               competitionopensincemonth, competitionopensinceyear,
               promo2, promo2sinceweek, promo2sinceyear, promointerval
        FROM stores_agg
        WHERE store = {store_id}
        """

        store_df = pd.read_sql(store_query, engine)

        if store_df.empty:
            return jsonify({"error": "Invalid store_id"})

        df = df.merge(store_df, left_on="store_id", right_on="store", how="left")

        sales_query = f"""
        SELECT date, sales, customers
        FROM sales_data
        WHERE store_id = {store_id}
        ORDER BY date DESC
        LIMIT 30
        """
        # Add default columns expected by pipeline if missing
        for col, default in [
            ('StateHoliday', 0),
            ('SchoolHoliday', 0),
            ('promo2', 0)
        ]:
            if col not in df.columns:
                df[col] = default
        sales_hist = pd.read_sql(sales_query, engine)

        lag_1 = sales_hist.iloc[0]["sales"] if len(sales_hist) >= 1 else 0
        lag_7 = sales_hist.iloc[6]["sales"] if len(sales_hist) >= 7 else 0
        lag_14 = sales_hist.iloc[13]["sales"] if len(sales_hist) >= 14 else 0

        rolling_7 = sales_hist.head(7)["sales"].mean() if len(sales_hist) >= 7 else 0
        rolling_14 = sales_hist.head(14)["sales"].mean() if len(sales_hist) >= 14 else 0
        rolling_30 = sales_hist["sales"].mean() if not sales_hist.empty else 0

        avg_sales = sales_hist["sales"].mean() if not sales_hist.empty else 0
        avg_customers = sales_hist["customers"].mean() if not sales_hist.empty else 0

        df["lag_1"] = lag_1
        df["lag_7"] = lag_7
        df["lag_14"] = lag_14
        df["rolling_7"] = rolling_7
        df["rolling_14"] = rolling_14
        df["rolling_30"] = rolling_30
        df["trend_7_14"] = rolling_7 - rolling_14
        df["avg_sales"] = avg_sales
        df["avg_customers"] = avg_customers

        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["dayofweek"] = df["date"].dt.dayofweek
        df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
        df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
        df["quarter"] = df["date"].dt.quarter
        df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
        df["is_month_end"] = df["date"].dt.is_month_end.astype(int)

        df["stateholiday"] = df["stateholiday"].fillna("0")
        df["schoolholiday"] = df["schoolholiday"].fillna(0)
        df["promo"] = df["promo"].fillna(0)

        df["is_holiday"] = (df["stateholiday"] != "0").astype(int)

        df["competitiondistance"] = df["competitiondistance"].fillna(0)

        df["competition_open"] = (
            (df["year"] - df["competitionopensinceyear"]) * 12 +
            (df["month"] - df["competitionopensincemonth"])
        )
        df["competition_open"] = df["competition_open"].fillna(0)

        df["promo2_active"] = df["promo2"].fillna(0)

        df = df.drop(columns=["date", "store_id", "store"], errors="ignore")

        prediction = model.predict(df)[0]

        return jsonify({"prediction": float(prediction)})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/ingest", methods=["POST"])
def ingest():
    try:
        data = request.get_json()
        df = pd.DataFrame(data)

        from ingest import dataframe_updation
        df = dataframe_updation(df)

        df.to_sql("sales_data", engine, if_exists="append", index=False)

        return jsonify({"message": "Data ingested successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/bulk_predict", methods=["POST"])
@app.route("/bulk_predict", methods=["POST"])
def bulk_predict():
    try:
        data = request.get_json()
        df = pd.DataFrame(data)

        df["date"] = pd.to_datetime(df["date"])
        df["promo"] = df.get("promo", 0)

        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["dayofweek"] = df["date"].dt.dayofweek
        df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
        df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)

        df = df.drop(columns=["date"], errors="ignore")

        predictions = model.predict(df)

        return jsonify([{"prediction": float(p)} for p in predictions])
    except Exception as e:
        return jsonify({"error": str(e)})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))