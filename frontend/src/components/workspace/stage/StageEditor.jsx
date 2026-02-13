import React, { useState, useRef, useEffect } from 'react';
import environment from '../../../config/environment';
import '../../../styles/StageEditor.css';

function StageEditor({ stage, onSave, onCancel }) {
  const [editedLogic, setEditedLogic] = useState(stage.edited_logic || stage.original_logic);
  const [saving, setSaving] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const textareaRef = useRef(null);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(editedLogic);
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadVersionHistory = async () => {
    setDownloading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${environment.API_BASE_URL}/api/stage/${stage.id}/version-history-pdf`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        const error = await response.json();
        
        // Handle no history case with friendly message
        if (response.status === 404) {
          alert('No version history available yet. Version history is created when you edit stage logic or generate code.');
          return;
        }
        
        throw new Error(error.detail || 'Failed to download version history');
      }

      // Download the PDF
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `version_history_${stage.stage_name}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading version history:', error);
      alert(error.message || 'Failed to download version history');
    } finally {
      setDownloading(false);
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [editedLogic]);

  const handleChange = (e) => {
    setEditedLogic(e.target.value);
  };

  return (
    <div className="stage-editor">
      <div className="editor-header">
        <div>
          <h3>Edit Stage Logic</h3>
          <div className="editor-info">
            Stage {stage.stage_number}: {stage.stage_name}
          </div>
        </div>
        <button 
          onClick={handleDownloadVersionHistory}
          disabled={downloading}
          className="btn-version-history"
          title="Download version history as PDF"
        >
          {downloading ? 'Downloading...' : 'Version History'}
        </button>
      </div>

      <div className="editor-body">
        <textarea
          ref={textareaRef}
          value={editedLogic}
          onChange={handleChange}
          className="logic-editor auto-resize"
          placeholder="Edit stage logic..."
        />
        <div className="word-count">
          {editedLogic.split(/\s+/).filter(w => w).length} words
        </div>
      </div>

      <div className="editor-actions">
        <button onClick={onCancel} className="btn-cancel">
          Cancel
        </button>
        <button 
          onClick={handleSave} 
          disabled={saving || !editedLogic.trim()}
          className="btn-save"
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
}

export default StageEditor;