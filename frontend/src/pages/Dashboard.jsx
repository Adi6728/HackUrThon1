import React, { useState, useEffect } from 'react';
import { Search, Shield, Zap, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';
import { useAnalysis } from '../hooks/useAnalysis';
import { RecommendationBanner } from '../components/RecommendationBanner';
import { SignalCard } from '../components/SignalCard';
import { AgentTracePanel } from '../components/AgentTracePanel';
import { DegradedDataBanner } from '../components/DegradedDataBanner';

const POPULAR_TICKERS = ['RELIANCE', 'TCS', 'INFY', 'NVDA', 'AAPL'];
const RISK_PROFILES = [
  { id: 'CONSERVATIVE', label: 'Conservative', desc: 'Capital preservation & steady yields' },
  { id: 'MODERATE', label: 'Moderate', desc: 'Balanced growth & managed risk' },
  { id: 'AGGRESSIVE', label: 'Aggressive', desc: 'High momentum & maximum capital growth' },
];

export function Dashboard() {
  const [selectedTicker, setSelectedTicker] = useState('RELIANCE');
  const [searchInput, setSearchInput] = useState('');
  const [riskProfile, setRiskProfile] = useState('MODERATE');

  const { loading, error, data, isDegraded, triggerAnalysis } = useAnalysis();

  // Initial fetch on component mount or risk profile change
  useEffect(() => {
    triggerAnalysis(selectedTicker, riskProfile);
  }, [selectedTicker, riskProfile, triggerAnalysis]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      const ticker = searchInput.trim().toUpperCase();
      setSelectedTicker(ticker);
      setSearchInput('');
    }
  };

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '24px 16px 48px 16px' }}>
      
      {/* Top Header / Control Panel */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.5px' }}>
              Multi-Agent Autonomous Intelligence Engine
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '4px' }}>
              Synthesizing real-time market technicals, news sentiment, and RAG regulatory filings.
            </p>
          </div>

          {/* Quick Ticker Search */}
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', gap: '8px', flexGrow: 1, maxWidth: '400px' }}>
            <div style={{ position: 'relative', width: '100%' }}>
              <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                placeholder="Enter ticker (e.g. RELIANCE, TCS)..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid var(--border-light)',
                  borderRadius: '10px',
                  padding: '10px 12px 10px 38px',
                  color: '#ffffff',
                  fontSize: '0.9rem',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--accent-cyan)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--border-light)'}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-cyan) 100%)',
                color: '#070a11',
                border: 'none',
                borderRadius: '10px',
                padding: '10px 18px',
                fontWeight: 700,
                fontSize: '0.875rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                whiteSpace: 'nowrap'
              }}
            >
              {loading ? <RefreshCw size={16} className="animate-spin" /> : <Sparkles size={16} />}
              <span>Analyze</span>
            </button>
          </form>
        </div>

        {/* Ticker Quick Selector & Risk Profile Switcher */}
        <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          
          {/* Quick Ticker Chips */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 600 }}>POPULAR TICKERS:</span>
            {POPULAR_TICKERS.map((t) => (
              <button
                key={t}
                onClick={() => setSelectedTicker(t)}
                style={{
                  background: selectedTicker === t ? 'rgba(0, 242, 254, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                  color: selectedTicker === t ? 'var(--accent-cyan)' : 'var(--text-muted)',
                  border: selectedTicker === t ? '1px solid rgba(0, 242, 254, 0.4)' : '1px solid var(--border-light)',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Risk Profile Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={16} color="var(--accent-cyan)" />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 600 }}>RISK PROFILE:</span>
            <div style={{ display: 'flex', background: 'rgba(0, 0, 0, 0.4)', padding: '3px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              {RISK_PROFILES.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setRiskProfile(p.id)}
                  title={p.desc}
                  style={{
                    background: riskProfile === p.id ? 'var(--bg-secondary)' : 'transparent',
                    color: riskProfile === p.id ? 'var(--accent-cyan)' : 'var(--text-muted)',
                    border: 'none',
                    padding: '4px 12px',
                    borderRadius: '6px',
                    fontSize: '0.78rem',
                    fontWeight: riskProfile === p.id ? 700 : 500,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Degraded Data Warning Banner */}
      <DegradedDataBanner show={isDegraded} />

      {/* Error Message Display */}
      {error && (
        <div style={{ background: 'rgba(255, 75, 75, 0.1)', border: '1px solid rgba(255, 75, 75, 0.3)', color: '#FF4B4B', padding: '16px', borderRadius: '12px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <AlertCircle size={20} />
          <div>
            <strong>Analysis Request Failed</strong>
            <p style={{ fontSize: '0.85rem', color: '#fca5a5' }}>{error}</p>
          </div>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '48px 0' }}>
          <RefreshCw size={36} color="var(--accent-cyan)" style={{ animation: 'spin 1s linear infinite' }} />
          <p style={{ marginTop: '16px', color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Dispatching 3 parallel agents (Technical, Sentiment, Fundamental RAG) for <strong>{selectedTicker}</strong>...
          </p>
        </div>
      )}

      {/* Main Analysis Display */}
      {!loading && data && (
        <>
          {/* Top Recommendation Banner */}
          <RecommendationBanner
            synthesized={data.synthesized}
            ticker={data.ticker}
            riskProfile={data.user_profile}
          />

          {/* 3 Domain Agent Signals Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '24px' }}>
            <SignalCard
              title="Technical Agent"
              type="technical"
              signal={data.technical}
            />
            <SignalCard
              title="Sentiment Agent"
              type="sentiment"
              signal={data.sentiment}
            />
            <SignalCard
              title="Fundamental RAG Agent"
              type="fundamental"
              signal={data.fundamental}
            />
          </div>

          {/* Reasoning & Citations Trace Panel */}
          <AgentTracePanel
            technical={data.technical}
            sentiment={data.sentiment}
            fundamental={data.fundamental}
            synthesized={data.synthesized}
            latencyMs={data.latency_ms}
          />
        </>
      )}
    </div>
  );
}
