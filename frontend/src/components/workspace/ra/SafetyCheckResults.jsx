import React from 'react';
import '../../../styles/SafetyCheckResults.css';

function SafetyCheckResults({ checkResult }) {
  const getStatusColor = (status) => {
    switch(status) {
      case 'PASS': return '#28a745';
      case 'WARNING': return '#ffc107';
      case 'FAIL': return '#dc3545';
      default: return '#666';
    }
  };

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'LOW': return '#28a745';
      case 'MEDIUM': return '#ffc107';
      case 'HIGH': return '#ff6b6b';
      case 'CRITICAL': return '#dc3545';
      default: return '#666';
    }
  };

  return (
    <div className="safety-check-results">
      <div className="check-header">
        <h3>✅ Independent Safety Check</h3>
        <div className="status-badges">
          <span 
            className="status-badge"
            style={{ backgroundColor: getStatusColor(checkResult.status) }}
          >
            {checkResult.status}
          </span>
          <span 
            className="risk-badge"
            style={{ backgroundColor: getRiskColor(checkResult.risk_level) }}
          >
            Risk: {checkResult.risk_level}
          </span>
        </div>
      </div>

      {checkResult.manuals_used && checkResult.manuals_used.length > 0 && (
        <div className="manuals-info">
          <h4>📚 Safety Manuals Used ({checkResult.total_manuals})</h4>
          <ul>
            {checkResult.manuals_used.map((manual, index) => (
              <li key={index}>{manual}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="check-section">
        <h4>Compliance Analysis</h4>
        <p>{checkResult.compliance_analysis || 'No analysis available'}</p>
      </div>

      {checkResult.missing_checks && checkResult.missing_checks.length > 0 && (
        <div className="check-section missing">
          <h4>⚠️ Missing Safety Checks</h4>
          <ul>
            {checkResult.missing_checks.map((check, index) => (
              <li key={index}>{check}</li>
            ))}
          </ul>
        </div>
      )}

      {checkResult.violations && checkResult.violations.length > 0 && (
        <div className="check-section violations">
          <h4>🚨 Safety Violations</h4>
          <ul>
            {checkResult.violations.map((violation, index) => (
              <li key={index}>{violation}</li>
            ))}
          </ul>
        </div>
      )}

      {checkResult.hazards && checkResult.hazards.length > 0 && (
        <div className="check-section hazards">
          <h4>⚠️ Potential Hazards</h4>
          <ul>
            {checkResult.hazards.map((hazard, index) => (
              <li key={index}>{hazard}</li>
            ))}
          </ul>
        </div>
      )}

      {checkResult.required_corrections && checkResult.required_corrections.length > 0 && (
        <div className="check-section corrections">
          <h4>🔧 Required Corrections</h4>
          <ul>
            {checkResult.required_corrections.map((correction, index) => (
              <li key={index}>{correction}</li>
            ))}
          </ul>
        </div>
      )}

      {checkResult.recommendations && checkResult.recommendations.length > 0 && (
        <div className="check-section recommendations">
          <h4>💡 Recommendations</h4>
          <ul>
            {checkResult.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default SafetyCheckResults;