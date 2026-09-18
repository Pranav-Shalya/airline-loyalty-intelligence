# Airline Loyalty: Retention Intelligence Strategy Memo
**Target Audience:** Chief Marketing Officer & Chief Financial Officer

## 1. Executive Summary
The traditional approach to airline loyalty relies heavily on historical Customer Lifetime Value (CLV) and static demographic profiling. This reactive model blinds the airline to active flight deceleration, resulting in high-margin customers abandoning the network silently. 

By architecting a leakage-free predictive intelligence engine, we have identified **1,123 high-value customers** exhibiting immediate silent churn behavior. This memo outlines the shift from reactive rewards to a predictive, margin-aware operational queue that deploys targeted interventions before the customer formally cancels.

## 2. The Evolution of the Data Strategy
Our approach evolved significantly from initial exploratory analysis to the final production model to ensure mathematical rigor and eliminate predictive blind spots.

### Phase 1: The Initial Demographic Approach (And Its Flaws)
Initially, the feature matrix relied on demographic data (Salary, Education, Province) and discrete quarterly flight counts (Q1 vs. Q2). 
* **The Anomaly:** 100% of college-educated users were missing salary data. We successfully salvaged this cohort using median imputation between the High School and Bachelor tiers.
* **The Failure of Demographics:** Early SHAP (SHapley Additive exPlanations) analysis revealed that demographics possessed zero predictive power for churn. A high-income executive is just as likely to silently abandon the airline as a lower-income student. 
* **The Outlier Problem:** Flight Distance and Points Accumulated exhibited extreme right-skewness (kurtosis > 88), which warped clustering algorithms by accommodating a tiny fraction of 'Super Elite' fliers.

### Phase 2: The Optimized Time-Series Approach
To isolate the true behavioral drivers of loyalty, we rebuilt the feature engineering pipeline:
* **Kurtosis Smoothing:** We applied a `Log1p` transformation to all financial and flight volume metrics, compressing the extreme tails while preserving relative customer rankings.
* **Dimensionality Reduction:** We explicitly dropped `Gender`, `Marital Status`, and `Province` to reduce noise and force the XGBoost model to focus purely on behavioral momentum.
* **Continuous Time-Series Panel:** Instead of comparing static quarters (Q1 vs Q2), we calculated Exponential Moving Averages (EMA). We generated a 3-month and 6-month EMA of flight activity, alongside a 6-month rolling variance of points accumulated, to capture micro-fluctuations in travel habits.

## 3. Advanced SHAP Insights
The optimized XGBoost model relies almost entirely on our engineered time-series features:
* **The Momentum Indicator (3M/6M EMA Ratio):** The single strongest predictor of churn is the `Flight_EMA_Ratio`. If a customer's recent 3-month flight average drops below their 6-month baseline, it signals a breaking habit.
* **Behavioral Volatility:** The 6-month rolling variance of points accurately identifies customers whose previously stable corporate schedules have become erratic.

## 4. Value Segmentation & Smart Retention Playbook
We deployed K-Means clustering on the log-transformed matrix to segment the active base into strategic personas, mapped to specific interventions:
1. **High-Value Business (Intervention: Status Extension):** Lucrative corporate travelers exhibiting a sudden velocity drop. Extending their Aurora/Nova tier by 6 months secures high-margin retention without giving away free flights.
2. **Occasional Savers (Intervention: 1.5x Burn-to-Earn Multiplier):** Customers hoarding points with near-zero burn rates. We offer a time-limited multiplier on non-flight redemptions, actively burning financial liability off the balance sheet while re-engaging the user.
3. **Steady Commuters (Intervention: Win-Back Bundle):** Regional fliers extending their time between flights. We offer a complimentary lounge pass for their next booking, leveraging fixed-cost assets to artificially inflate the value of loyalty.

## 5. The Operational Prototype
We deployed a live React/FastAPI intelligence interface. The system surfaces a **Priority Action Queue**, dynamically sorting customers by the severity of their momentum drop (e.g., 3-month EMA falling to 10% of their historical baseline) and mapping them explicitly to the optimal retention playbook action.
