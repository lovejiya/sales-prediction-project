# Sales Prediction System

## Overview

This project is a machine learning-based sales prediction system designed to forecast sales using historical data. It supports both manual input and bulk data ingestion, and provides predictions through an interactive web interface.

---

## Features

* Data preprocessing and cleaning
* Multiple regression models implemented
* Model evaluation and comparison
* Bulk CSV upload for batch predictions
* Manual input prediction
* Interactive web interface using Streamlit
* Progress tracking during prediction

---

## Tech Stack

* Python
* Scikit-learn
* Pandas
* NumPy
* Streamlit
* Flask (for API integration)
* JSON

---

## Project Structure

```
sales-prediction/
│
├── data/                  # Dataset files
├── src/                   # Flask API
│   ├── app.py
│   ├── streamlit_app.py
│   ├── db.py
│   ├── test_db.py
│   ├── ingest.py
│   ├── mapping.py
│   ├── ingest.py
│
├── databases/                    # Database connection files
│   ├── schema.sql
│
├── req.txt                #libraries to download
├── README.md
```

---

## Installation

Clone the repository:

```
git clone https://github.com/your-username/sales-prediction.git
cd sales-prediction
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Running the Application

Start the Streamlit app:

```
streamlit run app/app.py
```

(Optional) Run Flask API:

```
python api/app.py
```

---

## Usage

### Manual Prediction

* Enter feature values through the UI
* Click predict to get results

### Bulk Prediction

* Upload CSV file
* System processes data and returns predictions

### Bulk Ingestion

* Upload CSV file
* System processes data and ingests it for future prediction
---

## Models Used

* Linear Regression
* Decision Tree Regressor
* Random Forest Regressor
* Gradient Boosting Regressor

---

## Evaluation Metrics

* Mean Absolute Error (MAE)
* Mean Squared Error (MSE)
* R² Score

---

## Notes

* Ensure dataset format matches training data
* Handle missing values before prediction
* Large datasets may take longer to process

---

## Future Improvements

* Model tuning and optimization
* Deployment on cloud
* Real-time data integration
* Dashboard for visualization

---

## Author

Jiya Jain
