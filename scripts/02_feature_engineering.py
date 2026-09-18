import pandas as pd
import numpy as np

print('Loading processed dataset...')
df = pd.read_csv('data/processed/merged_loyalty_activity.csv')
df = df[df['Is_Ghost'] == False].copy()

# Temporal Cutoff (Leakage Prevention)
df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-01')
feature_df = df[df['Date'] < '2018-07-01'].copy()

print('Building continuous time-series panel for rolling features...')
# Create a grid of all users and all months up to the cutoff
users = feature_df['Loyalty Number'].unique()
months = pd.date_range(start='2017-01-01', end='2018-06-01', freq='MS')
panel = pd.MultiIndex.from_product([users, months], names=['Loyalty Number', 'Date']).to_frame(index=False)

# Merge actual flight data into the continuous grid
monthly_activity = feature_df.groupby(['Loyalty Number', 'Date'])[['Total Flights', 'Points Accumulated']].sum().reset_index()
ts_df = pd.merge(panel, monthly_activity, on=['Loyalty Number', 'Date'], how='left').fillna(0)

# Sort chronologically for rolling calculations
ts_df = ts_df.sort_values(['Loyalty Number', 'Date'])

print('Calculating EMA and Rolling Variance...')
# 3-Month and 6-Month Exponential Moving Averages for Flights
ts_df['EMA_3M_Flights'] = ts_df.groupby('Loyalty Number')['Total Flights'].transform(lambda x: x.ewm(span=3, adjust=False).mean())
ts_df['EMA_6M_Flights'] = ts_df.groupby('Loyalty Number')['Total Flights'].transform(lambda x: x.ewm(span=6, adjust=False).mean())

# Momentum Signal: 3M vs 6M EMA
ts_df['Flight_EMA_Ratio'] = (ts_df['EMA_3M_Flights'] + 0.01) / (ts_df['EMA_6M_Flights'] + 0.01)

# 6-Month Rolling Variance for Points (captures erratic behavior)
ts_df['Points_6M_Var'] = ts_df.groupby('Loyalty Number')['Points Accumulated'].transform(lambda x: x.rolling(window=6, min_periods=1).var().fillna(0))

# Extract ONLY the final known state (June 2018) for the ML matrix
cutoff_features = ts_df[ts_df['Date'] == '2018-06-01'].drop(columns=['Date', 'Total Flights', 'Points Accumulated'])

print('Aggregating baseline features...')
user_features = feature_df.groupby('Loyalty Number').agg(
    Historical_Flights=('Total Flights', 'sum'),
    Historical_Distance=('Distance', 'sum'),
    Total_Points_Acc=('Points Accumulated', 'sum'),
    Total_Points_Red=('Points Redeemed', 'sum'),
    Last_Active_Date=('Date', 'max')
).reset_index()

# Velocity Delta
q1_18 = feature_df[(feature_df['Date'] >= '2018-01-01') & (feature_df['Date'] <= '2018-03-01')].groupby('Loyalty Number')['Total Flights'].sum().reset_index(name='Q1_Flights')
q2_18 = feature_df[(feature_df['Date'] >= '2018-04-01') & (feature_df['Date'] <= '2018-06-01')].groupby('Loyalty Number')['Total Flights'].sum().reset_index(name='Q2_Flights')
user_features = user_features.merge(q1_18, on='Loyalty Number', how='left').merge(q2_18, on='Loyalty Number', how='left').fillna(0)
user_features['Velocity_Delta'] = user_features['Q2_Flights'] - user_features['Q1_Flights']
user_features['Burn_Rate'] = user_features['Total_Points_Red'] / (user_features['Total_Points_Acc'] + 1)
user_features['Months_Since_Last_Activity'] = ((pd.to_datetime('2018-06-30') - user_features['Last_Active_Date']).dt.days / 30).round()
user_features.drop(columns=['Last_Active_Date'], inplace=True)

# Merge Time-Series Cutoff Features with Baseline Features
user_features = pd.merge(user_features, cutoff_features, on='Loyalty Number', how='inner')

print('Dimensionality Reduction & Demographics...')
demographics = df[['Loyalty Number', 'Province', 'Education', 'Salary', 'Loyalty Card', 'CLV', 'Enrollment Type', 'Silent_Churn']].drop_duplicates()
model_df = user_features.merge(demographics, on='Loyalty Number', how='inner')

print('Applying Log Transformations...')
log_cols = ['CLV', 'Salary', 'Historical_Distance', 'Total_Points_Acc', 'Points_6M_Var']
for col in log_cols:
    model_df[col] = np.log1p(model_df[col])

print('Categorical Encoding...')
edu_map = {'High School or Below': 0, 'College': 1, 'Bachelor': 2, 'Master': 3, 'Doctor': 4}
card_map = {'Star': 0, 'Nova': 1, 'Aurora': 2}
model_df['Education'] = model_df['Education'].map(edu_map)
model_df['Loyalty Card'] = model_df['Loyalty Card'].map(card_map)
model_df = pd.get_dummies(model_df, columns=['Province', 'Enrollment Type'], drop_first=True)

print('Saving Advanced ML Matrix...')
model_df.to_csv('data/processed/model_training_data.csv', index=False)
print('Phase 2 (Advanced Time-Series) Complete.')
