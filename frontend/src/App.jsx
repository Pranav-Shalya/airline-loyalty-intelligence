import { useState, useEffect } from 'react'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard')
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(err => console.error(err))
  }, [])

  if (loading) return <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>Loading Intelligence Engine...</div>
  if (data.error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {data.error}. Is the backend reading the CSV?</div>

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ borderBottom: '2px solid #eee', paddingBottom: '1rem' }}>Airline Loyalty: Retention Intelligence</h1>
      
      <div style={{ display: 'flex', gap: '2rem', marginBottom: '3rem', marginTop: '2rem' }}>
        <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px', flex: 1 }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#666' }}>Active Base</h3>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 'bold' }}>{data.kpis.total_customers.toLocaleString()}</p>
        </div>
        <div style={{ background: '#fff0f0', padding: '1.5rem', borderRadius: '8px', flex: 1, border: '1px solid #ffcaca' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#d32f2f' }}>High Risk Customers</h3>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 'bold', color: '#d32f2f' }}>{data.kpis.customers_at_risk.toLocaleString()}</p>
        </div>
        <div style={{ background: '#f0fdf4', padding: '1.5rem', borderRadius: '8px', flex: 1, border: '1px solid #bbf7d0' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#15803d' }}>CLV at Risk</h3>
          <p style={{ fontSize: '2rem', margin: 0, fontWeight: 'bold', color: '#15803d' }}>${Math.round(data.kpis.revenue_at_risk).toLocaleString()}</p>
        </div>
      </div>

      <h2>Priority Action Queue</h2>
      <p style={{ color: '#666' }}>High-value customers exhibiting sudden flight deceleration, sorted by velocity drop.</p>
      
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
        <thead>
          <tr style={{ background: '#f8f9fa', textAlign: 'left' }}>
            <th style={{ padding: '1rem', borderBottom: '2px solid #dee2e6' }}>Loyalty Number</th>
            <th style={{ padding: '1rem', borderBottom: '2px solid #dee2e6' }}>Segment Persona</th>
            <th style={{ padding: '1rem', borderBottom: '2px solid #dee2e6' }}>Lifetime Value</th>
            <th style={{ padding: '1rem', borderBottom: '2px solid #dee2e6' }}>Q1 &rarr; Q2 Flights</th>
            <th style={{ padding: '1rem', borderBottom: '2px solid #dee2e6' }}>Churn Risk</th>
            <th style={{ padding: '1rem', borderBottom: '2px solid #dee2e6' }}>Recommended Action</th>
          </tr>
        </thead>
        <tbody>
          {data.action_queue.map((user) => {
            let btnText = 'Deploy Intervention';
            let btnColor = '#0f172a'; // Default Dark
            
            if (user['Persona'] === 'High-Value Business') {
              btnText = 'Extend Status Tier';
              btnColor = '#1d4ed8'; // Blue
            } else if (user['Persona'] === 'Occasional Savers') {
              btnText = 'Send 1.5x Point Multiplier';
              btnColor = '#15803d'; // Green
            } else if (user['Persona'] === 'Steady Commuters') {
              btnText = 'Offer Commuter Bundle';
              btnColor = '#7e22ce'; // Purple
            } else if (user['Persona'] === 'At-Risk Inactives') {
              btnText = 'Send Win-Back Email';
              btnColor = '#ea580c'; // Orange
            }

            return (
              <tr key={user['Loyalty Number']} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '1rem', fontWeight: 'bold' }}>{user['Loyalty Number']}</td>
                <td style={{ padding: '1rem' }}>{user['Persona']}</td>
                <td style={{ padding: '1rem' }}>${Math.round(user['CLV']).toLocaleString()}</td>
                <td style={{ padding: '1rem' }}>
                  {user['Q1_Flights']} &rarr; <span style={{ color: user['Q2_Flights'] < user['Q1_Flights'] ? 'red' : 'black', fontWeight: user['Q2_Flights'] < user['Q1_Flights'] ? 'bold' : 'normal' }}>{user['Q2_Flights']}</span>
                </td>
                <td style={{ padding: '1rem' }}>
                  <span style={{ background: '#fee2e2', color: '#991b1b', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold' }}>
                    {(user['Churn_Probability'] * 100).toFixed(1)}%
                  </span>
                </td>
                <td style={{ padding: '1rem' }}>
                  <button style={{ background: btnColor, color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', width: '100%' }}>
                    {btnText}
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  )
}
export default App
