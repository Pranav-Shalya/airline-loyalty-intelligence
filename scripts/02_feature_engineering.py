import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

print('Loading processed dataset...')
df = pd.read_csv('data/processed/merged_loyalty_activity.csv')

# Drop ghost users
df = df[df['Is_Ghost'] == False]

# Create Date column
df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-01')

# Strict time cutoff for features (Leakage Prevention)
feature_df = df[df['Date'] < '2018-07-01']

print('Engineering temporal features...')
# 1. Behavioral Aggregates
user_features = feature_df.groupby('Loyalty Number').agg(
    Historical_Flights=('Total Flights', 'sum'),
    Historical_Distance=('Distance', 'sum'),
    Total_Points_Acc=('Points Accumulated', 'sum'),
    Total_Points_Red=('Points Redeemed', 'sum'),
    Last_Active_Date=('Date', 'max')
).reset_index()

# 2. Velocity Metrics (Q2 2018 vs Q1 2018)
q1_18 = feature_df[(feature_df['Date'] >= '2018-01-01') & (feature_df['Date'] <= '2018-03-01')].groupby('Loyalty Number')['Total Flights'].sum().reset_index(name='Q1_Flights')
q2_18 = feature_df[(feature_df['Date'] >= '2018-04-01') & (feature_df['Date'] <= '2018-06-01')].groupby('Loyalty Number')['Total Flights'].sum().reset_index(name='Q2_Flights')

user_features = user_features.merge(q1_18, on='Loyalty Number', how='left').merge(q2_18, on='Loyalty Number', how='left').fillna(0)
user_features['Velocity_Delta'] = user_features['Q2_Flights'] - user_features['Q1_Flights']

# 3. Burn Rate
user_features['Burn_Rate'] = user_features['Total_Points_Red'] / (user_features['Total_Points_Acc'] + 1)

# 4. Recency
reference_date = pd.to_datetime('2018-06-30')
user_features['Months_Since_Last_Activity'] = ((reference_date - user_features['Last_Active_Date']).dt.days / 30).round()

print('Merging target variables and demographics...')
demographics = df[['Loyalty Number', 'Gender', 'Education', 'Salary', 'Marital Status', 'Loyalty Card', 'CLV', 'Silent_Churn']].drop_duplicates()
model_df = user_features.merge(demographics, on='Loyalty Number', how='inner')

# Drop datetime column for ML readiness
model_df = model_df.drop(columns=['Last_Active_Date'])

print('Generating Feature Correlation Heatmap...')
numeric_cols = model_df.select_dtypes(include=[np.number])
plt.figure(figsize=(12,10))
sns.heatmap(numeric_cols.corr(), annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Feature Correlation Matrix (Leakage-Free)')
plt.tight_layout()
plt.savefig('visualizations/04_feature_correlation.png')
plt.close()

print('Saving ML-ready matrix...')
model_df.to_csv('data/processed/model_training_data.csv', index=False)
print('Phase 2 Complete. Feature matrix constructed.')
