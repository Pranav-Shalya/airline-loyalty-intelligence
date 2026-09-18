from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

try:
    df = pd.read_csv('data/processed/scored_customers.csv')
    segment_map = {0: 'Occasional Savers', 1: 'High-Value Business', 2: 'Steady Commuters', 3: 'At-Risk Inactives'}
    df['Persona'] = df['Segment_ID'].map(segment_map)
except Exception as e:
    df = pd.DataFrame()

@app.get('/api/dashboard')
def get_dashboard():
    if df.empty:
        return {'error': 'Data not loaded'}
    
    high_risk_threshold = 0.60
    at_risk_df = df[df['Churn_Probability'] >= high_risk_threshold].copy()
    
    total_active = len(df)
    total_at_risk = len(at_risk_df)
    revenue_at_risk = float(at_risk_df['CLV'].sum())
    
    # Sort by the most severe deceleration (Flight_EMA_Ratio ascending), then CLV
    action_queue = at_risk_df.sort_values(
        by=['Flight_EMA_Ratio', 'CLV', 'Churn_Probability'], 
        ascending=[True, False, False]
    ).head(15)
    
    queue_data = action_queue[['Loyalty Number', 'Persona', 'CLV', 'Flight_EMA_Ratio', 'Points_6M_Var', 'Churn_Probability']].to_dict(orient='records')
    
    return {
        'kpis': {
            'total_customers': total_active,
            'customers_at_risk': total_at_risk,
            'revenue_at_risk': revenue_at_risk
        },
        'action_queue': queue_data
    }
