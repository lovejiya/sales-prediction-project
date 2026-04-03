from db import engine
import pandas as pd
import numpy as np

query = """
SELECT s.*, 
       st.storetype, st.assortment, st.competitiondistance,
       st.competitionopensincemonth, st.competitionopensinceyear,
       st.promo2, st.promo2sinceweek, st.promo2sinceyear, st.promointerval
FROM sales_data AS s
LEFT JOIN stores AS st
ON s.store_id = st.store
"""

df = pd.read_sql(query, engine)

df["date"] = pd.to_datetime(df["date"])

df = df[df["open"] == 1]

df = df.sort_values(["store_id", "date"])

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["dayofweek"] = df["date"].dt.dayofweek
df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
df["quarter"] = df["date"].dt.quarter
df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
df["is_month_end"] = df["date"].dt.is_month_end.astype(int)

df["lag_1"] = df.groupby("store_id")["sales"].shift(1)
df["lag_7"] = df.groupby("store_id")["sales"].shift(7)
df["lag_14"] = df.groupby("store_id")["sales"].shift(14)

df["rolling_7"] = df.groupby("store_id")["sales"].shift(1).rolling(7).mean().reset_index(level=0, drop=True)
df["rolling_14"] = df.groupby("store_id")["sales"].shift(1).rolling(14).mean().reset_index(level=0, drop=True)
df["rolling_30"] = df.groupby("store_id")["sales"].shift(1).rolling(30).mean().reset_index(level=0, drop=True)

df["trend_7_14"] = df["rolling_7"] - df["rolling_14"]

df["avg_sales"] = df.groupby("store_id")["sales"].transform(lambda x: x.shift(1).expanding().mean())

df["avg_customers"] = df.groupby("store_id")["customers"].transform(lambda x: x.shift(1).expanding().mean())

df["StateHoliday"] = df["StateHoliday"].fillna("0")
df["SchoolHoliday"] = df["SchoolHoliday"].fillna(0)
df["promo"] = df["promo"].fillna(0)

df["is_holiday"] = (df["StateHoliday"] != "0").astype(int)

df["competitiondistance"] = df["competitiondistance"].fillna(df["competitiondistance"].median())

df["competition_open"] = (
    (df["year"] - df["competitionopensinceyear"]) * 12 +
    (df["month"] - df["competitionopensincemonth"])
)

df["promo2_active"] = df["promo2"].fillna(0)

df = df.dropna()

df = df[df["sales"] > 0]

split_date = df["date"].quantile(0.8)

train = df[df["date"] < split_date]
test = df[df["date"] >= split_date]

X_train = train.drop(columns=["sales", "date", "store_id"])
y_train = train["sales"]

X_test = test.drop(columns=["sales", "date", "store_id"])
y_test = test["sales"]

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

num_cols = [
    "competitiondistance", "promo", "SchoolHoliday",
    "year", "month", "day", "dayofweek", "weekofyear",
    "is_weekend", "quarter", "is_month_start", "is_month_end",
    "lag_1", "lag_7", "lag_14",
    "rolling_7", "rolling_14", "rolling_30",
    "trend_7_14",
    "avg_sales", "avg_customers",
    "is_holiday", "competition_open", "promo2_active"
]

cat_cols = [
    "storetype", "assortment", "StateHoliday", "promointerval"
]

num_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="mean"))
])

cat_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", num_pipe, num_cols),
    ("cat", cat_pipe, cat_cols)
])

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor

def rmspe(y_true, y_pred):
    return np.sqrt(np.mean(((y_true - y_pred) / y_true) ** 2))

models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(),
    "Random Forest": RandomForestRegressor(n_estimators=150, max_depth=20, n_jobs=-1, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=4, subsample=0.8, random_state=42),
    "XGBoost": XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
}

pipelines = {}

for name, model in models.items():
    pipelines[name] = Pipeline([
        ("preprocessing", preprocessor),
        ("model", model)
    ])

results = {}

for name, pipe in pipelines.items():
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    rmspe_val = rmspe(y_test, pred)

    results[name] = {"MAE": mae, "RMSE": rmse, "RMSPE": rmspe_val}

    print(f"{name} → MAE: {mae}, RMSE: {rmse}, RMSPE: {rmspe_val}")

best_model_name = min(results, key=lambda x: results[x]["RMSE"])
best_pipe = pipelines[best_model_name]

print(f"Best model: {best_model_name}")

results_df = pd.DataFrame(results).T
results_df.to_csv("model_results.csv")

import joblib
joblib.dump(best_pipe, "pipeline.pkl")
joblib.dump(results, "metrics.pkl")

print("Model and metrics saved!")