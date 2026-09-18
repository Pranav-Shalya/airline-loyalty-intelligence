# Airline Loyalty: Retention Intelligence Strategy Memo
**Author:** Pranav Shalya
**Target Audience:** Chief Marketing Officer & Chief Financial Officer

## 1. Executive Summary
The traditional approach to airline loyalty relies heavily on historical Customer Lifetime Value (CLV) and static demographic profiling. This reactive model blinds the airline to active flight deceleration, resulting in high-margin customers abandoning the airline silently. 

By engineering a leakage-free predictive intelligence engine, we have identified **1,318 high-value customers** exhibiting immediate silent churn behavior. This cohort represents exactly **$9,688,343 in at-risk revenue**. This memo outlines the shift from reactive rewards to a predictive, margin-aware operational queue that deploys targeted interventions before the customer formally cancels.

## 2. Data Strategy & Leakage Prevention
Rigorous data cleaning and strict temporal boundaries were enforced to ensure the model's performance in a real-world production environment.
* **The 'Ghost' Cohort Excision:** 1,561 enrolled users recorded zero flights and zero redemptions across the 24-month period. These users were removed from the training matrix, as a predictive model cannot learn retention signals from users who never activated.
* **Demographic Imputation:** 100% of college-educated users (4,238 records) were missing salary data. Rather than dropping this demographic entirely, we applied a median interpolation (~$66,977) between the High School and Bachelor tiers, preserving the cohort without skewing the network's income distribution.
* **Defeating Data Leakage:** To predict H2 2018 churn, the target was strictly defined as zero activity between July and December 2018. All predictive features (such as Q1-to-Q2 Velocity Delta) were strictly calculated using data prior to July 1, 2018.

## 3. The SHAP Insights: Behavior over Demographics
The XGBoost model utilized SHAP (SHapley Additive exPlanations) to extract the mathematical drivers of loyalty attrition.
* **The Death of Demographics:** Variables such as `Salary`, `Gender`, and `Education` demonstrated zero predictive power for churn. Wealth and education do not predict loyalty.
* **The Velocity Delta Warning:** The single strongest predictor of churn is the momentum shift (`Q2_Flights` minus `Q1_Flights`). Measuring this delta successfully flags disengaging fliers while filtering out standard seasonal dips (such as the historical network-wide drop every January).
* **The CLV Trap:** Historical CLV had minimal impact on the prediction. Relying on historic spend to identify who needs attention causes the airline to miss newly disengaging customers.

## 4. Value Segmentation & Smart Retention Playbook
We deployed K-Means clustering to segment the active base into strategic personas, mapped to specific, cost-effective interventions:
1. **High-Value Business (Intervention: Status Extension):** These are lucrative corporate travelers exhibiting a sudden velocity drop. Because it costs the airline almost nothing to extend their Aurora/Nova tier by 6 months, we secure high-margin retention without giving away free flights.
2. **Occasional Savers (Intervention: 1.5x Burn-to-Earn Multiplier):** These customers hoard points (high accumulated, near-zero burn rate) until they disengage. We offer a time-limited multiplier on hotel/car partner redemptions, actively burning financial liability off the balance sheet while re-engaging the user.
3. **Steady Commuters (Intervention: Win-Back Bundle):** Regional fliers extending their time between flights. We offer a complimentary lounge pass for their next booking, leveraging fixed-cost assets to artificially inflate the value of loyalty rather than discounting ticket prices.

## 5. The Operational Prototype
To bridge the gap between backend analytics and frontend marketing operations, we deployed a live intelligence interface. The system does not merely output raw probabilities; it surfaces a **Priority Action Queue**. Customers are sorted dynamically by their velocity drop (highlighting active decelerators) and explicitly mapped to the optimal retention playbook action.
