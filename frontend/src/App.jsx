import React from 'react';
import { Dashboard } from './pages/Dashboard';
import { ShieldCheck, Activity, Cpu } from 'lucide-react';

export default function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-primary)' }}>
      {/* Top Navbar */}
      <header style={{
        background: 'rgba(14, 20, 34, 0.85)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border-light)',
        padding: '14px 24px',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {/* Logo & Title */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              background: 'linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-cyan) 100%)',
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#070a11',
              boxShadow: '0 0 15px rgba(0, 242, 254, 0.3)'
            }}>
              <Cpu size={22} fontWeight={800} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h1 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.3px', margin: 0 }}>
                  HACKVERSE <span style={{ color: 'var(--accent-cyan)' }}>FIN-INTEL</span>
                </h1>
                <span style={{
                  fontSize: '0.65rem',
                  padding: '2px 6px',
                  background: 'rgba(0, 242, 254, 0.1)',
                  color: 'var(--accent-cyan)',
                  border: '1px solid rgba(0, 242, 254, 0.3)',
                  borderRadius: '4px',
                  fontWeight: 700
                }}>
                  PS-01
                </span>
              </div>
              <span style={{ fontSize: '0.725rem', color: 'var(--text-subtle)' }}>
                Multi-Agent Autonomous Financial Intelligence System
              </span>
            </div>
          </div>

          {/* System Status Pill */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              background: 'rgba(0, 230, 118, 0.08)',
              border: '1px solid rgba(0, 230, 118, 0.25)',
              borderRadius: '20px',
              padding: '6px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.78rem',
              color: 'var(--accent-green)',
              fontWeight: 600
            }}>
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: 'var(--accent-green)',
                boxShadow: '0 0 8px var(--accent-green)'
              }} />
              <span>3 AGENTS ONLINE</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Page View */}
      <main style={{ flexGrow: 1 }}>
        <Dashboard />
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-light)',
        padding: '16px 24px',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-subtle)',
        background: 'var(--bg-secondary)'
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <span>HACKVERSE: INTO THE WEB — PS-01 Multi-Agent Financial Intelligence</span>
          <span>FastAPI • LangGraph Architecture • RAG Grounding • React Vite</span>
        </div>
      </footer>
    </div>
  );
}
