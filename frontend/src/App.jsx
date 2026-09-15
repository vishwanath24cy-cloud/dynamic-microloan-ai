import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [healthData, setHealthData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://127.0.0.1:8000/health')
      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`)
      }
      const data = await response.json()
      setHealthData(data)
    } catch (err) {
      setError(err.message || 'Unable to connect to backend service')
      setHealthData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
  }, [])

  return (
    <div className="app-container">
      <header className="header">
        <span className="badge">College Hackathon Prototype</span>
        <h1 className="title">AI-Based Dynamic Microloan Repayment & Cash-Flow Planner</h1>
        <p className="subtitle">
          Intelligent financial stability tool that forecasts borrower cash flows and adapts microloan repayment installments dynamically to prevent defaults.
        </p>
      </header>

      {/* Backend API Health Card */}
      <section className="status-card">
        <div className="status-header">
          <div>
            <h2>Backend API Status</h2>
            <small style={{ color: '#64748b' }}>Connecting to http://127.0.0.1:8000/health</small>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button className="btn-refresh" onClick={fetchHealth} disabled={loading}>
              {loading ? 'Checking...' : 'Refresh Status'}
            </button>
            <div className={`status-indicator ${loading ? 'loading' : healthData ? 'healthy' : 'error'}`}>
              <span className="status-dot"></span>
              <span>
                {loading ? 'Checking...' : healthData ? 'Backend Online' : 'Backend Disconnected'}
              </span>
            </div>
          </div>
        </div>

        {healthData && (
          <table className="details-table">
            <tbody>
              <tr>
                <td>Service Name</td>
                <td>{healthData.service}</td>
              </tr>
              <tr>
                <td>System Status</td>
                <td><strong style={{ color: '#16a34a' }}>{healthData.status.toUpperCase()}</strong></td>
              </tr>
              <tr>
                <td>Database (SQLite)</td>
                <td>{healthData.database}</td>
              </tr>
              <tr>
                <td>Checked At</td>
                <td>{new Date(healthData.timestamp).toLocaleString()}</td>
              </tr>
            </tbody>
          </table>
        )}

        {error && (
          <div style={{ marginTop: '1rem', padding: '0.85rem', background: '#fef2f2', borderRadius: '0.5rem', color: '#991b1b', fontSize: '0.9rem' }}>
            ⚠️ <strong>Connection Warning:</strong> {error}. Start the FastAPI backend with <code>python -m uvicorn app.main:app --reload</code> in the <code>backend/</code> folder.
          </div>
        )}
      </section>

      {/* Feature Pillars */}
      <section className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">📈</div>
          <h3>Cash-Flow Forecasting</h3>
          <p>
            Machine learning models analyze historical revenue cycles, seasonal fluctuations, and daily inflows to project borrower repayment capacity.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🔄</div>
          <h3>Dynamic Repayment Plans</h3>
          <p>
            Rather than rigid fixed EMIs, loan installments flex up or down based on predicted cash flow, preventing liquidity crunches.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🛡️</div>
          <h3>Microfinance Risk Shield</h3>
          <p>
            Identifies early stress signals before a missed payment occurs, enabling proactive lender-borrower loan restructuring.
          </p>
        </div>
      </section>

      {/* Tech Stack & Architecture Overview */}
      <section className="architecture-card">
        <h3>Project Architecture</h3>
        <p>
          Configured with a clean modular separation of concerns designed for rapid hackathon feature iteration:
        </p>
        <div className="tech-tags">
          <span className="tag">⚛️ React 18</span>
          <span className="tag">⚡ Vite</span>
          <span className="tag">🐍 FastAPI (Python)</span>
          <span className="tag">🗄️ SQLite Database</span>
          <span className="tag">🤖 ML Cash-Flow Stub</span>
        </div>
      </section>

      <footer className="footer">
        <p>AI-Based Dynamic Microloan Repayment & Cash-Flow Planner &bull; Hackathon Foundation Scaffold</p>
      </footer>
    </div>
  )
}

export default App
