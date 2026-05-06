import React from 'react';

const Disclaimer = () => {
  return (
    <div style={{
      backgroundColor: '#FEF2F2', // Light red/warning background
      borderLeft: '4px solid #EF4444', // Red accent line
      padding: '12px 16px',
      margin: '10px 0',
      borderRadius: '4px',
      fontSize: '0.85rem',
      color: '#7F1D1D', // Dark red text for readability
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    }}>
      <span style={{ fontSize: '1.2rem' }}>⚠️</span>
      <p style={{ margin: 0, lineHeight: '1.4' }}>
        <strong>Note:</strong> This AI assistant provides general meal suggestions based on standard PCOS guidelines. It is not a substitute for professional medical advice. Always consult your doctor or nutritionist.
      </p>
    </div>
  );
};

export default Disclaimer;