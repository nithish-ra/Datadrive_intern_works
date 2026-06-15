import React from 'react';

export default function Sidebar({ onSave, onClear }) {
  const onDragStart = (event, nodeType, nodeLabel) => {
    event.dataTransfer.setData('application/reactflow-type', nodeType);
    event.dataTransfer.setData('application/reactflow-label', nodeLabel);
    event.dataTransfer.effectAllowed = 'move';
  };

  // LIGHT THEME: Crisp white background, narrower width
  const sidebarStyle = {
    width: '220px', // Shrunk from 280px to save space
    padding: '24px 16px',
    background: '#ffffff', 
    color: '#111827', // Dark gray text for high readability
    borderRight: '1px solid #e5e7eb',
    display: 'flex',
    flexDirection: 'column',
    boxSizing: 'border-box',
    zIndex: 10,
    boxShadow: '2px 0 10px rgba(0,0,0,0.03)'
  };

  const topSectionStyle = {
    flexGrow: 1, 
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  };

  const bottomSectionStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    paddingTop: '20px',
    borderTop: '1px solid #e5e7eb'
  };

  // LIGHT THEME: Soft gray nodes with clean borders
  const nodeStyle = {
    padding: '12px 14px',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    cursor: 'grab',
    backgroundColor: '#f9fafb',
    color: '#374151',
    fontSize: '13px',
    fontWeight: '500',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    transition: 'all 0.2s ease',
    boxShadow: '0 2px 4px -1px rgba(0, 0, 0, 0.05)',
  };

  const buttonStyle = {
    padding: '12px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '600',
    fontSize: '13px',
    border: 'none',
    transition: 'all 0.2s ease',
    letterSpacing: '0.3px'
  };

  return (
    <aside style={sidebarStyle}>
      {/* --- TOP SECTION (AGENTS) --- */}
      <div style={topSectionStyle}>
        <h3 style={{ 
          margin: '0 0 10px 0', 
          fontSize: '12px', 
          color: '#6b7280', 
          fontWeight: '700', 
          letterSpacing: '0.5px', 
          textTransform: 'uppercase' 
        }}>
          Workflow Agents
        </h3>
        
        <div 
          style={nodeStyle} 
          onDragStart={(e) => onDragStart(e, 'custom', 'API Integration')} 
          draggable
          onMouseOver={(e) => { e.target.style.borderColor = '#aa3bff'; e.target.style.color = '#aa3bff'; e.target.style.backgroundColor = 'rgba(170, 59, 255, 0.05)'; }}
          onMouseOut={(e) => { e.target.style.borderColor = '#d1d5db'; e.target.style.color = '#374151'; e.target.style.backgroundColor = '#f9fafb'; }}
        >
          <span>🌐</span> API Integration
        </div>

        <div 
          style={nodeStyle} 
          onDragStart={(e) => onDragStart(e, 'custom', 'Reasoning Agent')} 
          draggable
          onMouseOver={(e) => { e.target.style.borderColor = '#aa3bff'; e.target.style.color = '#aa3bff'; e.target.style.backgroundColor = 'rgba(170, 59, 255, 0.05)'; }}
          onMouseOut={(e) => { e.target.style.borderColor = '#d1d5db'; e.target.style.color = '#374151'; e.target.style.backgroundColor = '#f9fafb'; }}
        >
          <span>🧠</span> Reasoning Agent
        </div>

        <div 
          style={nodeStyle} 
          onDragStart={(e) => onDragStart(e, 'custom', 'Notification Engine')} 
          draggable
          onMouseOver={(e) => { e.target.style.borderColor = '#aa3bff'; e.target.style.color = '#aa3bff'; e.target.style.backgroundColor = 'rgba(170, 59, 255, 0.05)'; }}
          onMouseOut={(e) => { e.target.style.borderColor = '#d1d5db'; e.target.style.color = '#374151'; e.target.style.backgroundColor = '#f9fafb'; }}
        >
          <span>🔔</span> Notification Engine
        </div>
      </div>

      {/* --- BOTTOM SECTION (ACTIONS) --- */}
      <div style={bottomSectionStyle}>
        <button 
          onClick={onSave}
          style={{ ...buttonStyle, backgroundColor: '#aa3bff', color: '#ffffff' }}
          onMouseOver={(e) => e.target.style.opacity = 0.9}
          onMouseOut={(e) => e.target.style.opacity = 1}
        >
          ▶ Execute Canvas
        </button>

        <button 
          onClick={onClear}
          style={{ ...buttonStyle, backgroundColor: '#fff', color: '#ef4444', border: '1px solid #fca5a5' }}
          onMouseOver={(e) => { e.target.style.backgroundColor = '#fef2f2'; e.target.style.borderColor = '#ef4444'; }}
          onMouseOut={(e) => { e.target.style.backgroundColor = '#fff'; e.target.style.borderColor = '#fca5a5'; }}
        >
          🗑 Clear Canvas
        </button>
      </div>
    </aside>
  );
}