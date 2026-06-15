import React from 'react';
import { Handle, Position, useReactFlow } from 'reactflow';

export default function CustomNode({ id, data }) {
  const { setNodes } = useReactFlow();

  const handleInputChange = (field, value) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === id) {
          node.data = {
            ...node.data,
            [field]: value,
          };
        }
        return node;
      })
    );
  };

  // LIGHT THEME: Node container
  const containerStyle = {
    background: '#ffffff', 
    padding: '12px', 
    borderRadius: '8px', 
    border: '1px solid #d1d5db', 
    color: '#1f2937', 
    minWidth: '220px',
    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
  };

  // LIGHT THEME: Input fields
  const inputStyle = {
    width: '100%', 
    marginTop: '4px', 
    background: '#f9fafb', 
    color: '#111827', 
    border: '1px solid #d1d5db', 
    borderRadius: '4px', 
    padding: '8px', 
    boxSizing: 'border-box',
    fontSize: '12px',
    fontFamily: 'inherit'
  };

  const labelStyle = { fontSize: '11px', color: '#6b7280', fontWeight: '500' };

  return (
    <div style={containerStyle}>
      <Handle type="target" position={Position.Top} style={{ background: '#9ca3af', width: '8px', height: '8px' }} />
      
      <div style={{ fontWeight: '600', marginBottom: '12px', borderBottom: '1px solid #e5e7eb', paddingBottom: '8px', textAlign: 'center', fontSize: '14px' }}>
        {data.label}
      </div>
      
      {/* 1. API Integration Node */}
      {data.label === 'API Integration' ? (
        <div className="nodrag">
          <label style={labelStyle}>FDA Database Query:</label>
          <input
            type="text"
            onChange={(e) => handleInputChange('drugName', e.target.value)}
            defaultValue={data.drugName || ''}
            placeholder="Enter drug (e.g., Tylenol)"
            style={inputStyle}
          />
        </div>

      /* 2. Reasoning Agent Node */
      ) : data.label === 'Reasoning Agent' ? (
        <div className="nodrag">
          <label style={labelStyle}>Patient ID:</label>
          <input
            type="text"
            onChange={(e) => handleInputChange('patientId', e.target.value)}
            defaultValue={data.patientId || ''}
            placeholder="e.g., PAT-1042"
            style={{ ...inputStyle, marginBottom: '12px' }}
          />
          <label style={labelStyle}>Clinical Notes / Symptoms:</label>
          <textarea
            onChange={(e) => handleInputChange('prompt', e.target.value)}
            defaultValue={data.prompt || ''}
            placeholder="Enter patient symptoms..."
            style={{ ...inputStyle, height: '60px', resize: 'vertical' }}
          />
        </div>

      /* 3. Notification Engine Node */
      ) : (
        <div className="nodrag">
          <label style={labelStyle}>Task Instructions:</label>
          <textarea
            onChange={(e) => handleInputChange('prompt', e.target.value)}
            defaultValue={data.prompt || ''}
            placeholder="Enter task details here..."
            style={{ ...inputStyle, height: '70px', resize: 'vertical' }}
          />
        </div>
      )}

      <Handle type="source" position={Position.Bottom} style={{ background: '#9ca3af', width: '8px', height: '8px' }} />
    </div>
  );
}