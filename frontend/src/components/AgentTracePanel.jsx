import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Cpu, FileText, CheckCircle2, ListFilter } from 'lucide-react';

export function AgentTracePanel({ technical, sentiment, fundamental, synthesized, latencyMs }) {
  const [isOpen, setIsOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  if (!technical && !sentiment && !fundamental) return null;

  const citations = fundamental?.citations || [];

  return (
    <div className="glass-panel" style={{ padding: '24px', marginTop: '24px' }}>
      {/* Panel Header */}
      <div style={{
        display: 'flex',
        justify: 'space-between',
        alignItems: 'center',
        cursor: 'pointer',
        userSelect: 'none'
      }} onClick={() => setIsOpen(!isOpen)}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Cpu size={20} color="var(--accent-cyan)" />
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff' }}>
              Agent Reasoning & Citation Trace Panel
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Step-by-step audit logs & RAG grounding verification • Pipeline Latency: {latencyMs || 120}ms
            </span>
          </div>
        </div>
        <button style={{
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid var(--border-light)',
          color: 'var(--text-muted)',
          padding: '6px',
          borderRadius: '6px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center'
        }}>
          {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      {isOpen && (
        <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-light)', paddingTop: '16px' }}>
          {/* Tabs */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', borderBottom: '1px solid var(--border-light)', paddingBottom: '8px' }}>
            {['all', 'technical', 'sentiment', 'fundamental', 'citations'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  background: activeTab === tab ? 'rgba(0, 242, 254, 0.15)' : 'transparent',
                  color: activeTab === tab ? 'var(--accent-cyan)' : 'var(--text-muted)',
                  border: activeTab === tab ? '1px solid rgba(0, 242, 254, 0.3)' : '1px solid transparent',
                  padding: '6px 14px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {tab === 'citations' ? `RAG Citations (${citations.length})` : tab}
              </button>
            ))}
          </div>

          {/* Trace Content */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {(activeTab === 'all' || activeTab === 'technical') && technical && (
              <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: '8px', borderLeft: '3px solid var(--accent-cyan)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                    [Step 1/3] Technical Analysis Agent Dispatch
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontFamily: 'var(--font-mono)' }}>CONFIDENCE: {Math.round((technical.confidence || 0) * 100)}%</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  {technical.reasoning}
                </p>
              </div>
            )}

            {(activeTab === 'all' || activeTab === 'sentiment') && sentiment && (
              <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: '8px', borderLeft: '3px solid var(--accent-blue)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-blue)' }}>
                    [Step 2/3] News & Social Sentiment Agent Dispatch
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontFamily: 'var(--font-mono)' }}>HEADLINES: {sentiment.headline_count}</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  {sentiment.reasoning}
                </p>
              </div>
            )}

            {(activeTab === 'all' || activeTab === 'fundamental') && fundamental && (
              <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: '8px', borderLeft: '3px solid #A78BFA' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#A78BFA' }}>
                    [Step 3/3] Fundamental & RAG Filing Retrieval Agent Dispatch
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontFamily: 'var(--font-mono)' }}>VERDICT: {fundamental.valuation_verdict}</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  {fundamental.reasoning}
                </p>
              </div>
            )}

            {(activeTab === 'all' || activeTab === 'citations') && citations.length > 0 && (
              <div style={{ background: 'rgba(167, 139, 250, 0.05)', padding: '14px', borderRadius: '8px', border: '1px dashed rgba(167, 139, 250, 0.3)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#A78BFA', fontSize: '0.85rem', fontWeight: 700 }}>
                  <FileText size={16} />
                  <span>RAG Grounded Source Citations ({citations.length})</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {citations.map((citation, idx) => (
                    <div key={idx} style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.78rem',
                      color: '#e2e8f0',
                      background: 'rgba(0, 0, 0, 0.4)',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      borderLeft: '2px solid #A78BFA'
                    }}>
                      {citation}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
