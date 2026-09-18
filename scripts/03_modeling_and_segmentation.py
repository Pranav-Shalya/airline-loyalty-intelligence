import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import xgboost as xgb
import shap
import joblib
import os

print('Loading refined feature matrix...')
df = pd.read_csv('data/processed/model_training_data.csv')

print('Executing K-Means Value Segmentation (with Standard Scaling)...')
# Using the log-transformed variables for clustering
cluster_features = ['CLV', 'Burn_Rate', 'Historical_Flights', 'Salary']
scaler = StandardScaler()
X_clust = scaler.fit_transform(df[cluster_features])

# Train KMeans
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Segment_ID'] = kmeans.fit_predict(X_clust)

print('Training XGBoost Churn Classifier...')
# Isolate predictive features, drop IDs and Target
X = df.drop(columns=['Loyalty Number', 'Silent_Churn', 'Segment_ID'])
y = df['Silent_Churn']

# Stratified split to maintain churn ratio
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Train XGBoost with scale_pos_weight to handle class imbalance
clf = xgb.XGBClassifier(
    n_estimators=150, 
    max_depth=4, 
    learning_rate=0.05, 
    eval_metric='logloss', 
    scale_pos_weight=(len(y)-sum(y))/sum(y)
)
clf.fit(X_train, y_train)

print('Calculating SHAP Feature Importances on Clean Data...')
explainer = shap.TreeExplainer(clf)
shap_values = explainer.shap_values(X_test)

plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_test, show=False)
plt.title('SHAP Value Impact on Churn Probability (Optimized)')
plt.tight_layout()
plt.savefig('visualizations/07_shap_summary_optimized.png')
plt.close()

print('Scoring the network base...')
df_scored = df.copy()
# Re-align columns to match training matrix exactly
X_all = df.drop(columns=['Loyalty Number', 'Silent_Churn', 'Segment_ID'])
X_all = X_all.reindex(columns=X_train.columns, fill_value=0)
df_scored['Churn_Probability'] = clf.predict_proba(X_all)[:, 1]

print('Exporting artifacts to backend/models/...')
os.makedirs('backend/models', exist_ok=True)
joblib.dump(clf, 'backend/models/xgboost_churn_model.pkl')
joblib.dump(kmeans, 'backend/models/kmeans_segmentation.pkl')
joblib.dump(scaler, 'backend/models/scaler.pkl')
joblib.dump(list(X_train.columns), 'backend/models/model_features.pkl')

df_scored.to_csv('data/processed/scored_customers.csv', index=False)
print('Phase 3 Complete. Optimized models serialized and customer base scored.')
