import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs('visualizations', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

print('Loading raw datasets...')
loyalty = pd.read_csv('data/raw/Customer Loyalty History.csv')
flights = pd.read_csv('data/raw/Customer Flight Activity.csv')

print('Fixing negative salaries...')
loyalty['Salary'] = loyalty['Salary'].abs()

print('Imputing missing College salaries...')
bachelor_med = loyalty[loyalty['Education'] == 'Bachelor']['Salary'].median()
hs_med = loyalty[loyalty['Education'] == 'High School or Below']['Salary'].median()
college_impute = (bachelor_med + hs_med) / 2
loyalty['Salary'] = loyalty['Salary'].fillna(college_impute)

print('Flagging Ghost Users...')
user_totals = flights.groupby('Loyalty Number').agg({'Total Flights':'sum', 'Points Redeemed':'sum'})
ghosts = user_totals[(user_totals['Total Flights']==0) & (user_totals['Points Redeemed']==0)].index
loyalty['Is_Ghost'] = loyalty['Loyalty Number'].isin(ghosts)

print('Engineering Silent Churn Target Variable...')
active_17 = flights[(flights['Year']==2017) & (flights['Total Flights']>0)]['Loyalty Number'].unique()
active_h2_18 = flights[(flights['Year']==2018) & (flights['Month']>=7) & ((flights['Total Flights']>0) | (flights['Points Redeemed']>0))]['Loyalty Number'].unique()
loyalty['Silent_Churn'] = 0
loyalty.loc[loyalty['Loyalty Number'].isin(active_17) & ~loyalty['Loyalty Number'].isin(active_h2_18), 'Silent_Churn'] = 1

print('Generating Visualizations...')
# 1. Salary Distribution
plt.figure(figsize=(10,6))
sns.histplot(loyalty['Salary'], bins=40, kde=True, color='blue')
plt.title('Salary Distribution (Post-Imputation)')
plt.savefig('visualizations/01_salary_distribution.png')
plt.close()

# 2. Salary by Education Boxplot
plt.figure(figsize=(10,6))
sns.boxplot(x='Education', y='Salary', data=loyalty, order=['High School or Below', 'College', 'Bachelor', 'Master', 'Doctor'])
plt.title('Salary Stratification by Education Tier')
plt.savefig('visualizations/02_salary_by_education.png')
plt.close()

# 3. Flight Seasonality Trend
flights_monthly = flights.groupby(['Year', 'Month'])['Total Flights'].sum().reset_index()
flights_monthly['Date'] = pd.to_datetime(flights_monthly['Year'].astype(str) + '-' + flights_monthly['Month'].astype(str) + '-01')
plt.figure(figsize=(12,5))
sns.lineplot(x='Date', y='Total Flights', data=flights_monthly, marker='o', color='crimson')
plt.title('Total Network Flights Seasonality (2017-2018)')
plt.grid(True)
plt.savefig('visualizations/03_flight_seasonality.png')
plt.close()

print('Merging datasets and saving to processed folder...')
merged_data = pd.merge(flights, loyalty, on='Loyalty Number', how='left')
merged_data.to_csv('data/processed/merged_loyalty_activity.csv', index=False)
print('Pipeline Complete! Check the visualizations folder for EDA graphs.')
