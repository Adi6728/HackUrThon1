import React from 'react';
import { TrendingUp, ShieldAlert, Award, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export function RecommendationBanner({ synthesized, ticker, riskProfile }) {
  if (!synthesized) return null;

  const { action, confidence, overall_reasoning, risk_caveats } = synthesized;

  const getActionBadge = (act) => {
    switch (act?.toUpperCase()) {
      case 'BUY':
        return {
          bg: 'rgba(0, 230, 118, 0.15)',
          border: 'rgba(0, 230, 118, 0.4)',
          text: '#00E676',
          icon: <ArrowUpRight size={24} />
        };
      case 'SELL':
        return {
          bg: 'rgba(255, 75, 75, 0.15)',
          border: 'rgba(255, 75, 75, 0.4)',
          text: '#FF4B4B',
          icon: <ArrowDownRight size={24} />
        };
      default:
        return {
          bg: 'rgba(255, 184, 0, 0.15)',
          border: 'rgba(255, 184, 0, 0.4)',
          text: '#FFB800',
          icon: <Minus size={24} />
        };
    }
  };

  const badgeStyle = getActionBadge(action);
  const confidencePct = Math.round((confidence || 0) * 100);

  return (
    <div className="glass-panel glass-panel-accent" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '6px' }}>
            <Award size={16} color="var(--accent-cyan)" />
            <span>SYNTHESIZED MULTI-AGENT INVESTMENT RECOMMENDATION</span>
            <span style={{
              background: 'rgba(255, 255, 255, 0.08)',
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '0.75rem',
              color: 'var(--accent-cyan)',
              fontWeight: 600
            }}>
              {riskProfile} PROFILE
            </span>
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '12px' }}>
            {ticker} Analysis Verdict
          </h2>
        </div>

        {/* Action Badge */}
        <div style={{
          background: badgeStyle.bg,
          border: `1px solid ${badgeStyle.border}`,
          borderRadius: '12px',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          boxShadow: `0 0 20px ${badgeStyle.bg}`
        }}>
          {badgeStyle.icon}
          <div>
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', opacity: 0.8, color: badgeStyle.text }}>
              ACTION SIGNAL
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: badgeStyle.text, lineHeight: 1 }}>
              {action}
            </div>
          </div>
        </div>
      </div>

      {/* Confidence Bar */}
      <div style={{ marginTop: '20px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
          <span style={{ color: 'var(--text-muted)' }}>Multi-Agent Confidence Score</span>
          <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>{confidencePct}%</span>
        </div>
        <div style={{ height: '8px', width: '100%', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            width: `${confidencePct}%`,
            background: 'linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-cyan) 100%)',
            borderRadius: '4px',
            transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
          }} />
        </div>
      </div>

      {/* Personalized Reasoning */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.03)',
        borderLeft: '3px solid var(--accent-cyan)',
        padding: '14px 18px',
        borderRadius: '0 8px 8px 0',
        marginBottom: '16px'
      }}>
        <h4 style={{ fontSize: '0.9rem', color: '#e2e8f0', marginBottom: '4px', fontWeight: 600 }}>
          Personalized Reasoning & Strategy
        </h4>
        <p style={{ color: '#cbd5e1', fontSize: '0.925rem', lineHeight: '1.6' }}>
          {overall_reasoning}
        </p>
      </div>

      {/* Risk Caveats */}
      {risk_caveats && risk_caveats.length > 0 && (
        <div style={{ marginTop: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--accent-amber)', fontWeight: 600, marginBottom: '8px' }}>
            <ShieldAlert size={14} />
            <span>CRITICAL RISK CAVEATS</span>
          </div>
          <ul style={{ listStyleType: 'none', padding: 0, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '8px' }}>
            {risk_caveats.map((caveat, idx) => (
              <li key={idx} style={{
                fontSize: '0.825rem',
                color: '#94a3b8',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                padding: '8px 12px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px'
              }}>
                <span style={{ color: 'var(--accent-amber)', fontWeight: 'bold' }}>•</span>
                <span>{caveat}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
