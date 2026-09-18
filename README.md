# Airline Loyalty: Retention Intelligence Engine

An end-to-end machine learning pipeline and full-stack operational dashboard designed to predict and prevent 'silent churn' in airline loyalty programs.

## 📌 Project Overview
Traditional loyalty programs rely on historical spending and demographics to identify valuable customers. This project replaces that reactive approach with a **predictive time-series architecture**. By calculating Exponential Moving Averages (EMA) and rolling behavioral variance, the XGBoost engine identifies high-value customers the exact moment their travel habits begin to decelerate—allowing the airline to intervene before the customer defects to a competitor.

## 🛠 Architecture & Tech Stack
* **Data Engineering & Analysis:** Pandas, NumPy, Scikit-Learn
* **Predictive Modeling:** XGBoost, SHAP (Explainable AI), K-Means Clustering
* **Backend API:** FastAPI (Python), Uvicorn, Joblib (Model Serialization)
* **Frontend UI:** React.js, Vite

## 🧠 The Analytical Evolution
This project went through two distinct modeling phases to achieve production-ready accuracy:

**1. The Baseline Approach (Demographics + Static Quarters)**
We initially engineered features based on discrete time blocks (Q2 flights minus Q1 flights) and included demographic data. 
* *Result:* SHAP analysis proved demographics (Salary, Education, Gender) had zero predictive power. Static quarters failed to account for a user's individual historical baseline.

**2. The Optimized Approach (Time-Series EMA + Log Transformations)**
We rebuilt the pipeline to meet rigorous statistical standards:
* Applied `Log1p` transformations to smooth extreme kurtosis (outliers) in Distance and Points features.
* Dropped non-predictive demographic variables to reduce dimensionality.
* Built a continuous month-over-month panel to extract a **3-Month vs 6-Month EMA Ratio** and **6-Month Rolling Variance**. 
* *Result:* The EMA ratio became the dominant predictor of churn, accurately flagging customers actively breaking their historical travel habits.

## 🚀 How to Run the Prototype Locally

### 1. Start the FastAPI Backend
Ensure your Python virtual environment is activated, then run:
```bash
uvicorn backend.main:app --reload --port 8000
```
*The API will serve the scored customer matrix and serialized machine learning models.*

### 2. Start the React Frontend
Open a new terminal window, navigate to the frontend directory, and start the Vite server:
```bash
cd frontend
npm run dev
```
*Navigate to `http://localhost:5173` in your browser to view the Priority Action Queue dashboard.*

## 📂 Repository Structure
* `/data` - Raw and processed feature matrices (ignored in version control)
* `/scripts` - Feature engineering, data cleaning, and XGBoost modeling pipelines
* `/visualizations` - SHAP summary plots and distribution charts
* `/backend` - FastAPI application and serialized `.pkl` ML models
* `/frontend` - React UI for the marketing operations team
