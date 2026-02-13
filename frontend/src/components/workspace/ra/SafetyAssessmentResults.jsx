import React from 'react';
import '../../../styles/SafetyAssessmentResults.css';

function SafetyAssessmentResults({ assessment }) {
  const getStatusColor = (status) => {
    switch(status) {
      case 'SAFE': return '#28a745';
      case 'WARNING': return '#ffc107';
      case 'UNSAFE': return '#dc3545';
      default: return '#666';
    }
  };

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'LOW': return '#28a745';
      case 'MEDIUM': return '#ffc107';
      case 'HIGH': return '#ff6b6b';
      case 'CRITICAL': return '#dc3545';
      default: return '#666';
    }
  };

  return (
    <div className="safety-assessment-results">
      <div className="safety-header">
        <h3>🛡️ Safety Assessment Results</h3>
        <div className="status-badges">
          <span 
            className="status-badge"
            style={{ backgroundColor: getStatusColor(assessment.status) }}
          >
            {assessment.status}
          </span>
          <span 
            className="severity-badge"
            style={{ backgroundColor: getSeverityColor(assessment.severity) }}
          >
            {assessment.severity}
          </span>
        </div>
      </div>

      <div className="safety-section">
        <h4>Compliance Analysis</h4>
        <p>{assessment.compliance_analysis || 'No analysis available'}</p>
      </div>

      {assessment.hazards && assessment.hazards.length > 0 && (
        <div className="safety-section hazards">
          <h4>⚠️ Potential Hazards</h4>
          <ul>
            {assessment.hazards.map((hazard, index) => (
              <li key={index}>{hazard}</li>
            ))}
          </ul>
        </div>
      )}

      {assessment.violations && assessment.violations.length > 0 && (
        <div className="safety-section violations">
          <h4>🚨 Safety Violations</h4>
          <ul>
            {assessment.violations.map((violation, index) => (
              <li key={index}>{violation}</li>
            ))}
          </ul>
        </div>
      )}

      {assessment.required_actions && assessment.required_actions.length > 0 && (
        <div className="safety-section actions">
          <h4>✋ Required Actions</h4>
          <ul>
            {assessment.required_actions.map((action, index) => (
              <li key={index}>{action}</li>
            ))}
          </ul>
        </div>
      )}

      {assessment.recommendations && assessment.recommendations.length > 0 && (
        <div className="safety-section recommendations">
          <h4>💡 Recommendations</h4>
          <ul>
            {assessment.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default SafetyAssessmentResults;