import React from 'react';
import { Activity, Newspaper, FileText, CheckCircle, AlertCircle, Info } from 'lucide-react';

export function SignalCard({ title, type, signal }) {
  if (!signal) return null;

  let icon = <Activity size={18} color="var(--accent-cyan)" />;
  let badgeText = 'NEUTRAL';
  let badgeClass = 'badge-neutral';

  if (type === 'technical') {
    icon = <Activity size={18} color="var(--accent-cyan)" />;
    badgeText = signal.trend || 'NEUTRAL';
    if (badgeText.includes('BULLISH')) badgeClass = 'badge-bullish';
    else if (badgeText.includes('BEARISH')) badgeClass = 'badge-bearish';
  } else if (type === 'sentiment') {
    icon = <Newspaper size={18} color="var(--accent-blue)" />;
    badgeText = signal.polarity || 'NEUTRAL';
    if (badgeText.includes('POSITIVE')) badgeClass = 'badge-bullish';
    else if (badgeText.includes('NEGATIVE')) badgeClass = 'badge-bearish';
  } else if (type === 'fundamental') {
    icon = <FileText size={18} color="#A78BFA" />;
    badgeText = signal.valuation_verdict || 'FAIRLY_VALUED';
    if (badgeText.includes('UNDERVALUED')) badgeClass = 'badge-bullish';
    else if (badgeText.includes('OVERVALUED')) badgeClass = 'badge-bearish';
  }

  const confidencePct = Math.round((signal.confidence || 0.8) * 100);

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Card Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '8px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {icon}
          </div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>{title}</h3>
        </div>
        <span className={badgeClass} style={{
          padding: '4px 10px',
          borderRadius: '20px',
          fontSize: '0.75rem',
          fontWeight: 700,
          letterSpacing: '0.5px'
        }}>
          {badgeText}
        </span>
      </div>

      {/* Confidence Score */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
          <span>Agent Signal Confidence</span>
          <span style={{ fontWeight: 600, color: '#e2e8f0' }}>{confidencePct}%</span>
        </div>
        <div style={{ height: '4px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '2px', overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            width: `${confidencePct}%`,
            background: badgeClass.includes('bullish') ? 'var(--accent-green)' : badgeClass.includes('bearish') ? 'var(--accent-red)' : 'var(--accent-amber)',
            borderRadius: '2px'
          }} />
        </div>
      </div>

      {/* Domain Specific Data */}
      <div style={{ flexGrow: 1, marginBottom: '16px' }}>
        {type === 'technical' && signal.key_levels && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--border-light)' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>SUPPORT LEVEL</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-green)', fontFamily: 'var(--font-mono)' }}>
                ₹{signal.key_levels.support || 'N/A'}
              </div>
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--border-light)' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>RESISTANCE LEVEL</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-red)', fontFamily: 'var(--font-mono)' }}>
                ₹{signal.key_levels.resistance || 'N/A'}
              </div>
            </div>
          </div>
        )}

        {type === 'sentiment' && signal.top_headlines && signal.top_headlines.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
              RECENT HEADLINES ANALYZED ({signal.headline_count || signal.top_headlines.length})
            </div>
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {signal.top_headlines.slice(0, 2).map((headline, idx) => (
                <li key={idx} style={{ fontSize: '0.78rem', color: '#cbd5e1', marginBottom: '4px', paddingLeft: '10px', borderLeft: '2px solid var(--accent-blue)' }}>
                  "{headline}"
                </li>
              ))}
            </ul>
          </div>
        )}

        {type === 'fundamental' && signal.key_risks && signal.key_risks.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
              KEY FINANCIAL RISKS IDENTIFIED
            </div>
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {signal.key_risks.slice(0, 2).map((risk, idx) => (
                <li key={idx} style={{ fontSize: '0.78rem', color: '#cbd5e1', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertCircle size={12} color="var(--accent-amber)" />
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Reasoning Summary */}
        <div style={{ fontSize: '0.825rem', color: '#94a3b8', lineHeight: '1.5', background: 'rgba(0, 0, 0, 0.2)', padding: '10px 12px', borderRadius: '6px' }}>
          {signal.reasoning || "Agent reasoning analysis compiled from market data input stream."}
        </div>
      </div>
    </div>
  );
}
