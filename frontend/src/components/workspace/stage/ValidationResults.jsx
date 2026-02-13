import React, { useState } from 'react';
import '../../../styles/ValidationResults.css';

function ValidationResults({ validation }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const getStatusColor = (status) => {
    switch(status) {
      case 'PASS': return '#28a745';
      case 'FAIL': return '#dc3545';
      default: return '#666';
    }
  };

  const getSeverityConfig = (severity) => {
    switch(severity) {
      case 'critical':
        return {
          color: '#000000',
          bgColor: '#d3d3d3',
          borderColor: '#000000',
          icon: '🔴',
          label: 'CRITICAL',
          description: 'Must be fixed for validation to pass'
        };
      case 'moderate':
        return {
          color: '#000000',
          bgColor: '#fff3e0',
          borderColor: '#000000',
          icon: '🟡',
          label: 'MODERATE',
          description: 'Good to implement but not mandatory'
        };
      case 'optional':
        return {
          color: '#000000',
          bgColor: '#e7f6f8',
          borderColor: '#000000',
          icon: '🔵',
          label: 'OPTIONAL',
          description: 'Suggestions that may improve the system'
        };
      default:
        return {
          color: '#666',
          bgColor: '#f5f5f5',
          borderColor: '#999',
          icon: '⚪',
          label: 'INFO',
          description: 'Information'
        };
    }
  };

  const handleCopyLogic = (logic, index) => {
    navigator.clipboard.writeText(logic);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const categorizedIssues = validation.categorized_issues || [];
  const criticalCount = categorizedIssues.filter(i => i.severity === 'critical').length || 0;
  const moderateCount = categorizedIssues.filter(i => i.severity === 'moderate').length || 0;
  const optionalCount = categorizedIssues.filter(i => i.severity === 'optional').length || 0;

  return (
    <div className="validation-results">
      <div className="validation-header">
        <h3>Validation Results</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span 
            className="validation-status"
            style={{ backgroundColor: getStatusColor(validation.status) }}
          >
            {validation.status}
          </span>
          {(criticalCount > 0 || moderateCount > 0 || optionalCount > 0) && (
            <span className="validation-summary">
              {criticalCount} Critical, {moderateCount} Moderate, {optionalCount} Optional
            </span>
          )}
        </div>
      </div>

      {/* Original Issues Section */}
      {validation.issues && validation.issues.length > 0 && (
        <div className="validation-section">
          <h4> Issues</h4>
          <ul className="simple-list">
            {validation.issues.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Original Recommendations Section */}
      {validation.recommendations && validation.recommendations.length > 0 && (
        <div className="validation-section">
          <h4> Recommendations</h4>
          <ul className="simple-list">
            {validation.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Categorized Issues Section (New) - Grouped by Severity */}
      {categorizedIssues.length > 0 && (
        <div className="issues-panel">
          <div className="issues-panel-header">
            <h4>Issues Found (Categorized by Severity)</h4>
            <div className="issue-counts">
              {criticalCount > 0 && (
                <span className="count-badge critical">{criticalCount} Critical</span>
              )}
              {moderateCount > 0 && (
                <span className="count-badge moderate">{moderateCount} Moderate</span>
              )}
              {optionalCount > 0 && (
                <span className="count-badge optional">{optionalCount} Optional</span>
              )}
            </div>
          </div>

          <div className="issues-list">
            {/* Critical Issues Box */}
            {criticalCount > 0 && (
              <div 
                className="issue-card"
                style={{ 
                  borderLeft: `4px solid ${getSeverityConfig('critical').borderColor}`,
                  backgroundColor: getSeverityConfig('critical').bgColor
                }}
              >
                <div className="issue-header">
                  <div className="issue-title-row">
                    <span className="issue-icon">{getSeverityConfig('critical').icon}</span>
                    <span 
                      className="issue-severity-label"
                      style={{ color: getSeverityConfig('critical').color }}
                    >
                      {getSeverityConfig('critical').label}
                    </span>
                  </div>
                  <span className="issue-severity-description">
                    {getSeverityConfig('critical').description}
                  </span>
                </div>

                {/* List all critical issues */}
                {categorizedIssues.filter(i => i.severity === 'critical').map((issue, index) => (
                  <div key={`critical-${index}`} className="issue-item">
                    <h5 className="issue-title">{index + 1}. {issue.title}</h5>
                    {issue.description && (
                      <div className="issue-description">
                        <strong>Problem:</strong> {issue.description}
                      </div>
                    )}
                  </div>
                ))}

                {/* Combined recommended logic for all critical issues */}
                {categorizedIssues.filter(i => i.severity === 'critical').some(i => i.recommended_logic) && (
                  <div className="recommended-logic">
                    <div className="recommended-logic-header">
                      <strong> Recommended Control Logic (Copy All):</strong>
                      <button
                        className="copy-logic-btn"
                        onClick={() => {
                          const allLogic = categorizedIssues
                            .filter(i => i.severity === 'critical' && i.recommended_logic)
                            .map((issue, idx) => `${idx + 1}. ${issue.title}:\n${issue.recommended_logic}`)
                            .join('\n\n');
                          handleCopyLogic(allLogic, 'critical-all');
                        }}
                        title="Copy to clipboard"
                      >
                        {copiedIndex === 'critical-all' ? '✓ Copied!' : ' Copy All'}
                      </button>
                    </div>
                    <div className="recommended-logic-content">
                      {categorizedIssues
                        .filter(i => i.severity === 'critical' && i.recommended_logic)
                        .map((issue, idx) => (
                          <div key={idx} className="logic-item">
                            <strong>{idx + 1}. {issue.title}:</strong>
                            <p>{issue.recommended_logic}</p>
                          </div>
                        ))
                      }
                    </div>
                    <div className="usage-hint">
                      Copy this recommendation and paste it into the Edit Logic section
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Moderate Issues Box */}
            {moderateCount > 0 && (
              <div 
                className="issue-card"
                style={{ 
                  borderLeft: `4px solid ${getSeverityConfig('moderate').borderColor}`,
                  backgroundColor: getSeverityConfig('moderate').bgColor
                }}
              >
                <div className="issue-header">
                  <div className="issue-title-row">
                    <span className="issue-icon">{getSeverityConfig('moderate').icon}</span>
                    <span 
                      className="issue-severity-label"
                      style={{ color: getSeverityConfig('moderate').color }}
                    >
                      {getSeverityConfig('moderate').label}
                    </span>
                  </div>
                  <span className="issue-severity-description">
                    {getSeverityConfig('moderate').description}
                  </span>
                </div>

                {/* List all moderate issues */}
                {categorizedIssues.filter(i => i.severity === 'moderate').map((issue, index) => (
                  <div key={`moderate-${index}`} className="issue-item">
                    <h5 className="issue-title">{index + 1}. {issue.title}</h5>
                    {issue.description && (
                      <div className="issue-description">
                        <strong>Problem:</strong> {issue.description}
                      </div>
                    )}
                  </div>
                ))}

                {/* Combined recommended logic for all moderate issues */}
                {categorizedIssues.filter(i => i.severity === 'moderate').some(i => i.recommended_logic) && (
                  <div className="recommended-logic">
                    <div className="recommended-logic-header">
                      <strong>Recommended Control Logic (Copy All):</strong>
                      <button
                        className="copy-logic-btn"
                        onClick={() => {
                          const allLogic = categorizedIssues
                            .filter(i => i.severity === 'moderate' && i.recommended_logic)
                            .map((issue, idx) => `${idx + 1}. ${issue.title}:\n${issue.recommended_logic}`)
                            .join('\n\n');
                          handleCopyLogic(allLogic, 'moderate-all');
                        }}
                        title="Copy to clipboard"
                      >
                        {copiedIndex === 'moderate-all' ? '✓ Copied!' : '📋 Copy All'}
                      </button>
                    </div>
                    <div className="recommended-logic-content">
                      {categorizedIssues
                        .filter(i => i.severity === 'moderate' && i.recommended_logic)
                        .map((issue, idx) => (
                          <div key={idx} className="logic-item">
                            <strong>{idx + 1}. {issue.title}:</strong>
                            <p>{issue.recommended_logic}</p>
                          </div>
                        ))
                      }
                    </div>
                    <div className="usage-hint">
                       Copy this recommendation and paste it into the Edit Logic section
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Optional Issues Box */}
            {optionalCount > 0 && (
              <div 
                className="issue-card"
                style={{ 
                  borderLeft: `4px solid ${getSeverityConfig('optional').borderColor}`,
                  backgroundColor: getSeverityConfig('optional').bgColor
                }}
              >
                <div className="issue-header">
                  <div className="issue-title-row">
                    <span className="issue-icon">{getSeverityConfig('optional').icon}</span>
                    <span 
                      className="issue-severity-label"
                      style={{ color: getSeverityConfig('optional').color }}
                    >
                      {getSeverityConfig('optional').label}
                    </span>
                  </div>
                  <span className="issue-severity-description">
                    {getSeverityConfig('optional').description}
                  </span>
                </div>

                {/* List all optional issues */}
                {categorizedIssues.filter(i => i.severity === 'optional').map((issue, index) => (
                  <div key={`optional-${index}`} className="issue-item">
                    <h5 className="issue-title">{index + 1}. {issue.title}</h5>
                    {issue.description && (
                      <div className="issue-description">
                        <strong>Problem:</strong> {issue.description}
                      </div>
                    )}
                  </div>
                ))}

                {/* Combined recommended logic for all optional issues */}
                {categorizedIssues.filter(i => i.severity === 'optional').some(i => i.recommended_logic) && (
                  <div className="recommended-logic">
                    <div className="recommended-logic-header">
                      <strong> Recommended Control Logic (Copy All):</strong>
                      <button
                        className="copy-logic-btn"
                        onClick={() => {
                          const allLogic = categorizedIssues
                            .filter(i => i.severity === 'optional' && i.recommended_logic)
                            .map((issue, idx) => `${idx + 1}. ${issue.title}:\n${issue.recommended_logic}`)
                            .join('\n\n');
                          handleCopyLogic(allLogic, 'optional-all');
                        }}
                        title="Copy to clipboard"
                      >
                        {copiedIndex === 'optional-all' ? '✓ Copied!' : '📋 Copy All'}
                      </button>
                    </div>
                    <div className="recommended-logic-content">
                      {categorizedIssues
                        .filter(i => i.severity === 'optional' && i.recommended_logic)
                        .map((issue, idx) => (
                          <div key={idx} className="logic-item">
                            <strong>{idx + 1}. {issue.title}:</strong>
                            <p>{issue.recommended_logic}</p>
                          </div>
                        ))
                      }
                    </div>
                    <div className="usage-hint">
                      Copy this recommendation and paste it into the Edit Logic section
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="validation-analysis">
        <h4> Analysis Summary</h4>
        
        {validation.semantic_analysis && (
          <div className="analysis-item">
            <strong>Semantic Analysis:</strong>
            <p>{validation.semantic_analysis}</p>
          </div>
        )}

        {validation.logical_consistency && (
          <div className="analysis-item">
            <strong>Logical Consistency:</strong>
            <p>{validation.logical_consistency}</p>
          </div>
        )}

        {validation.safety_compliance && (
          <div className="analysis-item">
            <strong>Safety Compliance:</strong>
            <p>{validation.safety_compliance}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ValidationResults;