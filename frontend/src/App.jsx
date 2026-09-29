import React, { useState, useEffect } from 'react';
import { api } from './api';
import './App.css';

// Helper for Indian Rupee currency formatting
const formatINR = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(val);
};

export default function App() {
  const [summary, setSummary] = useState(null);
  const [borrowers, setBorrowers] = useState([]);
  const [selectedBorrowerId, setSelectedBorrowerId] = useState(1);
  const [recommendation, setRecommendation] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recLoading, setRecLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initial load: Portfolio summary and borrowers list
  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, bRes] = await Promise.all([
        api.getDashboardSummary(),
        api.getBorrowers(),
      ]);
      setSummary(sumRes);
      setBorrowers(bRes);
      if (bRes.length > 0 && !selectedBorrowerId) {
        setSelectedBorrowerId(bRes[0].borrower_id);
      }
    } catch (err) {
      console.error('Failed to load portfolio data:', err);
      setError('Cannot connect to FastAPI backend at http://localhost:8000. Please ensure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  // Load borrower details & dynamic recommendation when active borrower changes
  const loadBorrowerData = async (id) => {
    setRecLoading(true);
    try {
      const [recRes, txRes] = await Promise.all([
        api.getBorrowerRecommendation(id),
        api.getBorrowerTransactions(id),
      ]);
      setRecommendation(recRes);
      setTransactions(txRes || []);
    } catch (err) {
      console.error(`Failed to load data for borrower ${id}:`, err);
      setError(`Failed to fetch analytics for Borrower #${id}. Please check backend logs.`);
    } finally {
      setRecLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedBorrowerId) {
      loadBorrowerData(selectedBorrowerId);
    }
  }, [selectedBorrowerId]);

  const activeBorrower = borrowers.find((b) => b.borrower_id === selectedBorrowerId) || {};

  // Badge styling helpers
  const getStressBadgeClass = (level) => {
    switch (level?.toUpperCase()) {
      case 'LOW':
        return 'badge-green';
      case 'MEDIUM':
        return 'badge-amber';
      case 'HIGH':
      case 'SEVERE':
        return 'badge-rose';
      default:
        return 'badge-slate';
    }
  };

  const getRecBadgeClass = (rec) => {
    switch (rec?.toUpperCase()) {
      case 'NORMAL_PAYMENT':
        return 'rec-normal';
      case 'SPLIT_PAYMENT':
        return 'rec-split';
      case 'REDUCED_PAYMENT':
        return 'rec-reduced';
      case 'REVIEW_REQUIRED':
        return 'rec-review';
      default:
        return 'rec-default';
    }
  };

  const getPersistenceBadge = (status) => {
    switch (status) {
      case 'NONE':
        return <span className="tag-pill tag-stable">✅ Stable</span>;
      case 'TEMPORARY_STRESS':
        return <span className="tag-pill tag-warn">⚠️ 1 Month Transient Shock</span>;
      case 'PERSISTENT_STRESS':
        return <span className="tag-pill tag-danger">🚨 2 Months Persistent Stress</span>;
      case 'SEVERE_PERSISTENT_STRESS':
        return <span className="tag-pill tag-severe">⛔ 3+ Months Chronic Distress</span>;
      default:
        return <span className="tag-pill">{status}</span>;
    }
  };

  return (
    <div className="dashboard-container">
      {/* Top Navigation / Header */}
      <header className="navbar">
        <div className="navbar-brand">
          <div className="brand-icon">💳</div>
          <div>
            <h1 className="brand-title">Dynamic Microloan AI Planner</h1>
            <p className="brand-subtitle">AI-Driven Cash-Flow Forecasting & Adaptive Microfinance Repayment</p>
          </div>
        </div>
        <div className="navbar-actions">
          <span className={`status-pill ${error ? 'status-down' : 'status-live'}`}>
            <span className="pulse-dot"></span>
            {error ? 'Backend Offline' : 'FastAPI Live (:8000)'}
          </span>
          <button className="btn-secondary" onClick={() => { loadInitialData(); loadBorrowerData(selectedBorrowerId); }} title="Refresh All Data">
            🔄 Refresh
          </button>
        </div>
      </header>

      {/* Global Error Banner */}
      {error && (
        <div className="error-banner">
          <div className="error-icon">⚠️</div>
          <div className="error-content">
            <h4>Backend Connection Error</h4>
            <p>{error}</p>
            <small>Command to run: <code>python -m uvicorn app.main:app --port 8000</code> inside the <code>backend/</code> folder.</small>
          </div>
          <button className="btn-retry" onClick={loadInitialData}>Retry</button>
        </div>
      )}

      {/* 1. Portfolio KPI Summary Bar */}
      {summary && (
        <section className="portfolio-summary-bar">
          <div className="kpi-card">
            <span className="kpi-label">Total Borrowers</span>
            <span className="kpi-value">{summary.total_borrowers}</span>
            <span className="kpi-sub">5 Microfinance Personas</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">Active Loans</span>
            <span className="kpi-value">{summary.total_loans}</span>
            <span className="kpi-sub">100% Active Portfolio</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">Total Loan Volume</span>
            <span className="kpi-value">{formatINR(summary.total_loan_volume)}</span>
            <span className="kpi-sub">Principal Disbursed</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">Total Monthly EMI</span>
            <span className="kpi-value">{formatINR(summary.total_monthly_emi)}</span>
            <span className="kpi-sub">Scheduled Collections</span>
          </div>
          <div className="kpi-card kpi-risk">
            <span className="kpi-label">Portfolio Stress Profile</span>
            <div className="stress-distribution">
              <span className="dist-chip low" title="Low Stress">{summary.stress_distribution?.LOW || 0} Low</span>
              <span className="dist-chip med" title="Medium Stress">{summary.stress_distribution?.MEDIUM || 0} Med</span>
              <span className="dist-chip high" title="High / Severe Stress">
                {(summary.stress_distribution?.HIGH || 0) + (summary.stress_distribution?.SEVERE || 0)} High
              </span>
            </div>
            <span className="kpi-sub highlight-warn">
              {summary.persistent_stress_count} Persistent Cases Flagged
            </span>
          </div>
        </section>
      )}

      {/* Main Content Area */}
      <div className="main-layout">
        {/* 2. Borrower Selector Sidebar / Panel */}
        <aside className="borrower-sidebar">
          <div className="sidebar-header">
            <h3>Demo Borrowers</h3>
            <span className="sub-count">Select a persona</span>
          </div>

          <div className="borrower-list">
            {borrowers.map((b) => {
              const isSelected = b.borrower_id === selectedBorrowerId;
              return (
                <button
                  key={b.borrower_id}
                  className={`borrower-item ${isSelected ? 'selected' : ''}`}
                  onClick={() => setSelectedBorrowerId(b.borrower_id)}
                >
                  <div className="borrower-item-top">
                    <span className="borrower-id-tag">ID #{b.borrower_id}</span>
                    <span className={`stress-mini-tag ${getStressBadgeClass(b.latest_stress_level)}`}>
                      {b.latest_stress_level}
                    </span>
                  </div>
                  <div className="borrower-name">{b.name}</div>
                  <div className="borrower-meta">
                    <span>{b.occupation}</span>
                    <span className="emi-tag">EMI: {formatINR(b.monthly_emi)}</span>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="sidebar-legend">
            <h4>Scenario Coverage</h4>
            <ul>
              <li><strong>B1:</strong> Stable (Full EMI)</li>
              <li><strong>B2:</strong> Transient Dip (Split)</li>
              <li><strong>B3:</strong> 2-Mo Stress (Review)</li>
              <li><strong>B4:</strong> Seasonal Surge (Normal)</li>
              <li><strong>B5:</strong> Chronic Deficit (Workout)</li>
            </ul>
          </div>
        </aside>

        {/* 3. Detail & Recommendations View */}
        <main className="dashboard-content">
          {loading ? (
            <div className="loader-box">
              <div className="spinner"></div>
              <p>Loading borrower analytics & ML inference...</p>
            </div>
          ) : recLoading ? (
            <div className="loader-box">
              <div className="spinner"></div>
              <p>Evaluating cash-flow & repayment stress for Borrower #{selectedBorrowerId}...</p>
            </div>
          ) : recommendation ? (
            <>
              {/* Active Borrower Overview Banner */}
              <div className="borrower-hero-banner">
                <div className="hero-info">
                  <span className="hero-badge">Borrower Profile #{recommendation.borrower_id}</span>
                  <h2>{recommendation.borrower_name}</h2>
                  <p className="hero-sub">
                    <strong>Occupation:</strong> {activeBorrower.occupation || 'Self-Employed'} &bull; 
                    <strong> Age:</strong> {activeBorrower.age || '—'} &bull; 
                    <strong> Active Loan:</strong> {formatINR(activeBorrower.total_loan_amount)} &bull; 
                    <strong> Contracted EMI:</strong> {formatINR(recommendation.current_emi)}
                  </p>
                </div>
                <div className="hero-status">
                  <span className="status-title">Current Risk State</span>
                  <div className="hero-badges">
                    <span className={`badge-lg ${getStressBadgeClass(recommendation.stress_level)}`}>
                      {recommendation.stress_level} STRESS
                    </span>
                    {getPersistenceBadge(recommendation.persistent_stress_status)}
                  </div>
                </div>
              </div>

              {/* Step 4 & 5 Analytics Cards Grid */}
              <div className="metrics-grid">
                {/* Current Liquidity */}
                <div className="metric-box">
                  <div className="metric-header">
                    <span className="metric-title">Current Liquidity</span>
                    <span className="metric-icon">💵</span>
                  </div>
                  <div className="metric-primary">{formatINR(recommendation.current_available_cash)}</div>
                  <div className="metric-breakdown">
                    <div className="breakdown-row">
                      <span>Monthly Contracted EMI:</span>
                      <strong>{formatINR(recommendation.current_emi)}</strong>
                    </div>
                    <div className="breakdown-row">
                      <span>Cash-to-EMI Coverage:</span>
                      <strong className={recommendation.current_available_cash >= recommendation.current_emi ? 'text-green' : 'text-danger'}>
                        {recommendation.important_financial_factors?.cash_to_emi_ratio != null
                          ? `${recommendation.important_financial_factors.cash_to_emi_ratio}x`
                          : (recommendation.current_available_cash / (recommendation.current_emi || 1)).toFixed(2) + 'x'}
                      </strong>
                    </div>
                    <div className="breakdown-row">
                      <span>Payment Delinquency:</span>
                      <span className={recommendation.important_financial_factors?.days_late > 0 ? 'text-danger' : 'text-green'}>
                        {recommendation.important_financial_factors?.days_late || 0} Days Late
                      </span>
                    </div>
                  </div>
                </div>

                {/* Step 4 ML Cash-Flow Forecast */}
                <div className="metric-box ml-box">
                  <div className="metric-header">
                    <div>
                      <span className="metric-title">ML Projected Cash Flow</span>
                      <span className="sub-tag">Step 4 Forecast</span>
                    </div>
                    <span className="metric-icon">🔮</span>
                  </div>
                  <div className={`metric-primary ${recommendation.predicted_available_cash >= 0 ? 'text-green' : 'text-danger'}`}>
                    {formatINR(recommendation.predicted_available_cash)}
                  </div>
                  <div className="metric-breakdown">
                    <div className="breakdown-row">
                      <span>Predicted Income:</span>
                      <strong>{formatINR(recommendation.predicted_income)}</strong>
                    </div>
                    <div className="breakdown-row">
                      <span>Predicted Expenses:</span>
                      <strong>{formatINR(recommendation.predicted_expenses)}</strong>
                    </div>
                    <div className="formula-callout">
                      <code>Available Cash = Income − Expenses</code>
                    </div>
                  </div>
                </div>

                {/* Step 5 & 5B Repayment Stress & Persistence */}
                <div className="metric-box">
                  <div className="metric-header">
                    <div>
                      <span className="metric-title">Stress & Governance</span>
                      <span className="sub-tag">Step 5 & 5B Policy</span>
                    </div>
                    <span className="metric-icon">🛡️</span>
                  </div>
                  <div className="stress-hero">
                    <span className={`stress-badge-large ${getStressBadgeClass(recommendation.stress_level)}`}>
                      {recommendation.stress_level} STRESS
                    </span>
                  </div>
                  <div className="metric-breakdown">
                    <div className="breakdown-row">
                      <span>Consecutive High Stress:</span>
                      <strong>{recommendation.consecutive_high_stress_months || 0} Month(s)</strong>
                    </div>
                    <div className="breakdown-row">
                      <span>Governance Protocol:</span>
                      <strong>
                        {recommendation.lender_review_required
                          ? '⚠️ Underwriter Review Locked'
                          : '✅ Automated Adjustment Eligible'}
                      </strong>
                    </div>
                    <div className="breakdown-row">
                      <span>Late Payments (Last 3m):</span>
                      <span>{recommendation.important_financial_factors?.late_payments_last_3m || 0}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 6 Dynamic Repayment Recommendation Card */}
              <div className={`recommendation-card ${getRecBadgeClass(recommendation.recommendation)}`}>
                <div className="rec-top-row">
                  <div className="rec-badge-group">
                    <span className="rec-flag-label">Dynamic Recommendation (Step 6)</span>
                    <h3 className="rec-title">{recommendation.recommendation.replace('_', ' ')}</h3>
                  </div>
                  <div className="rec-amount-box">
                    <span className="amount-label">Suggested Repayment Amount</span>
                    <span className="amount-val">
                      {recommendation.suggested_payment_amount != null
                        ? formatINR(recommendation.suggested_payment_amount)
                        : 'Review Required'}
                    </span>
                    {recommendation.suggested_payment_amount && recommendation.suggested_payment_amount !== recommendation.current_emi && (
                      <span className="amount-diff">
                        (Contracted: {formatINR(recommendation.current_emi)})
                      </span>
                    )}
                  </div>
                </div>

                <div className="rec-structure-box">
                  <div className="structure-title">📅 Suggested Schedule & Structure:</div>
                  <div className="structure-desc">{recommendation.suggested_payment_structure}</div>
                </div>

                <div className="rec-governance-notice">
                  {recommendation.lender_review_required ? (
                    <div className="guardrail-box alert-review">
                      🔒 <strong>Lender Review Guardrail Triggered:</strong> Because stress has persisted or severe chronic insolvency was detected, automated restructuring is halted. An underwriter must review this case.
                    </div>
                  ) : (
                    <div className="guardrail-box alert-safe">
                      ⚡ <strong>Automated Safe Advisory:</strong> Repayment plan matches borrower liquidity buffer without requiring manual loan committee intervention.
                    </div>
                  )}
                </div>
              </div>

              {/* Step 7 Explainable AI (XAI) Panel */}
              <div className="xai-panel">
                <div className="xai-header">
                  <div className="xai-title-wrap">
                    <span className="xai-icon">🧠</span>
                    <div>
                      <h3>Explainable AI (XAI) Insights</h3>
                      <p>Transparent feature contribution & institutional decision attribution</p>
                    </div>
                  </div>
                  <span className="xai-pill">Zero Black-Box Logic</span>
                </div>

                {/* Executive Summary */}
                <div className="xai-summary-card">
                  <span className="summary-label">Executive Synthesis:</span>
                  <p className="summary-text">{recommendation.summary || recommendation.reason}</p>
                </div>

                {/* Top Contributing Factors */}
                <div className="factors-section">
                  <h4>Top Contributing Decision Factors</h4>
                  <div className="factors-list">
                    {recommendation.top_factors && recommendation.top_factors.length > 0 ? (
                      recommendation.top_factors.map((factor, idx) => (
                        <div key={idx} className="factor-chip">
                          <span className="factor-num">#{idx + 1}</span>
                          <span className="factor-text">{factor}</span>
                        </div>
                      ))
                    ) : (
                      <p className="no-factors">Standard repayment parameters apply.</p>
                    )}
                  </div>
                </div>

                {/* Full Human Narrative */}
                <div className="xai-narrative-card">
                  <h4>Underwriting Narrative & Policy Explanation</h4>
                  <p>{recommendation.explanation || recommendation.reason}</p>
                </div>
              </div>

              {/* Cash-Flow Transaction History Table */}
              {transactions && transactions.length > 0 && (
                <div className="history-section">
                  <div className="history-header">
                    <h4>Historical Monthly Cash Flow Cycles</h4>
                    <span className="history-sub">Last {transactions.length} Recorded Cycles</span>
                  </div>
                  <div className="table-responsive">
                    <table className="history-table">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Inflow (Income)</th>
                          <th>Outflow (Expenses)</th>
                          <th>Net Margin (Income − Exp)</th>
                          <th>Cash Balance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {transactions.slice(-6).map((tx, idx) => {
                          const netMargin = tx.income - tx.expenses;
                          return (
                            <tr key={idx}>
                              <td>{tx.date}</td>
                              <td>{formatINR(tx.income)}</td>
                              <td>{formatINR(tx.expenses)}</td>
                              <td className={netMargin < 0 ? 'text-danger' : 'text-green'}>
                                {formatINR(netMargin)}
                              </td>
                              <td className={tx.cash_balance < 0 ? 'text-danger' : 'text-green'}>
                                {formatINR(tx.cash_balance)}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <p>No borrower selected. Choose a demo persona from the sidebar.</p>
            </div>
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="footer-bar">
        <p>AI-Based Dynamic Microloan Repayment & Cash-Flow Planner &bull; Academic Mini-Project Demonstration</p>
        <p className="footer-sub">Stack: React + Vite &bull; FastAPI &bull; SQLite &bull; Scikit-Learn ML</p>
      </footer>
    </div>
  );
}
