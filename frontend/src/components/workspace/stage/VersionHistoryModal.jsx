import React, { useState, useEffect } from 'react';
import stageService from '../../../services/stageService';
import '../../../styles/VersionHistoryModal.css';

function VersionHistoryModal({ stage, onClose }) {
  const [versionHistory, setVersionHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    loadVersionHistory();
  }, [stage.id]);

  const loadVersionHistory = async () => {
    try {
      setLoading(true);
      const data = await stageService.getVersionHistory(stage.id);
      setVersionHistory(data);
    } catch (error) {
      console.error('Failed to load version history:', error);
      alert('Failed to load version history');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadVersion = async (versionNumber) => {
    try {
      setDownloading(true);
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/stage/${stage.id}/version/${versionNumber}/download`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${stage.stage_name}_v${versionNumber}_${new Date().toISOString().split('T')[0]}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download version report');
    } finally {
      setDownloading(false);
    }
  };

  const handleDownloadFullHistory = async () => {
    try {
      setDownloading(true);
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/stage/${stage.id}/version-history-pdf`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Version_History_${stage.stage_name}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download version history report');
    } finally {
      setDownloading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getActionBadgeClass = (action) => {
    const actionMap = {
      'edit_logic': 'action-edit',
      'validate': 'action-validate',
      'generate_code': 'action-code',
      'safety_check': 'action-safety'
    };
    return actionMap[action] || 'action-default';
  };

  const getActionLabel = (action) => {
    const labelMap = {
      'edit_logic': ' Edit Logic',
      'validate': '✅ Validate',
      'generate_code': '⚡ Generate Code',
      'safety_check': '🛡️ Safety Check'
    };
    return labelMap[action] || action;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="version-history-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Version History</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="loading-state">Loading version history...</div>
          ) : versionHistory ? (
            <>
              {/* Summary Section */}
              <div className="version-summary">
                <div className="summary-item">
                  <span className="summary-label">Stage:</span>
                  <span className="summary-value">{stage.stage_name}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Current Version:</span>
                  <span className="summary-value version-badge">{versionHistory.current_version}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total Versions:</span>
                  <span className="summary-value">{versionHistory.total_versions}</span>
                </div>
                {versionHistory.last_action && (
                  <div className="summary-item">
                    <span className="summary-label">Last Action:</span>
                    <span className="summary-value">{getActionLabel(versionHistory.last_action)}</span>
                  </div>
                )}
              </div>

              {/* Download Full History Button */}
              <div className="full-history-download">
                <button
                  className="btn-download-full"
                  onClick={handleDownloadFullHistory}
                  disabled={downloading}
                >
                  📥 Download Complete Version History Report
                </button>
              </div>

              {/* Version History List */}
              <div className="version-list">
                <h3>Version Timeline</h3>
                {versionHistory.history && versionHistory.history.length > 0 ? (
                  <div className="timeline">
                    {versionHistory.history.map((version, index) => (
                      <div key={index} className="timeline-item">
                        <div className="timeline-marker">
                          <span className="version-number">{version.version}</span>
                        </div>
                        <div className="timeline-content">
                          <div className="version-header">
                            <span className={`action-badge ${getActionBadgeClass(version.action)}`}>
                              {getActionLabel(version.action)}
                            </span>
                            <span className="version-date">{formatDate(version.timestamp)}</span>
                          </div>
                          
                          {version.metadata && (
                            <div className="version-metadata">
                              {version.metadata.description && (
                                <p className="metadata-description">{version.metadata.description}</p>
                              )}
                              {version.metadata.validation_status && (
                                <span className="metadata-tag">Status: {version.metadata.validation_status}</span>
                              )}
                              {version.metadata.passed !== undefined && (
                                <span className={`metadata-tag ${version.metadata.passed ? 'passed' : 'failed'}`}>
                                  {version.metadata.passed ? '✓ Passed' : '✗ Failed'}
                                </span>
                              )}
                              {version.metadata.risk_level && (
                                <span className="metadata-tag risk">Risk: {version.metadata.risk_level}</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-history">No version history available</p>
                )}
              </div>
            </>
          ) : (
            <div className="error-state">Failed to load version history</div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-close" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}

export default VersionHistoryModal;
