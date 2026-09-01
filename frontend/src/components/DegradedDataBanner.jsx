import React from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

export function DegradedDataBanner({ show = false, message }) {
  if (!show) return null;

  return (
    <div style={{
      background: 'rgba(255, 184, 0, 0.1)',
      border: '1px solid rgba(255, 184, 0, 0.3)',
      borderRadius: '12px',
      padding: '12px 16px',
      marginBottom: '24px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      color: '#FFB800'
    }}>
      <AlertTriangle size={20} style={{ flexShrink: 0 }} />
      <div style={{ flexGrow: 1, fontSize: '0.875rem' }}>
        <strong style={{ fontWeight: 600 }}>System Running in Fallback / Degraded Data Mode</strong>
        <p style={{ color: '#cbd5e1', fontSize: '0.8rem', marginTop: '2px' }}>
          {message || "Live API rate-limit detected or offline cache active. System is maintaining high reliability via cached fixtures."}
        </p>
      </div>
      <span style={{
        fontSize: '0.75rem',
        padding: '2px 8px',
        borderRadius: '6px',
        background: 'rgba(255, 184, 0, 0.2)',
        fontWeight: 600
      }}>
        DEGRADED MODE
      </span>
    </div>
  );
}
