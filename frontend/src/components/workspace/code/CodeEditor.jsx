import React, { useState, useRef, useEffect } from 'react';
import { parseLabelsFromCode, formatLabelsToCode } from '../../../utils/labelParser';
import '../../../styles/CodeEditor.css';

function CodeEditor({ code, onSave, onCancel }) {
  // Reconstruct complete Structured Text code with VAR sections
  const reconstructCompleteCode = () => {
    let completeCode = '';
    
    // Add global labels section
    if (code.global_labels && code.global_labels.length > 0) {
      completeCode += 'VAR_GLOBAL\n';
      code.global_labels.forEach(label => {
        let line = `    ${label.name} : ${label.data_type}`;
        if (label.initial_value) {
          line += ` := ${label.initial_value}`;
        }
        line += ';';
        if (label.comment || label.device) {
          line += ' //';
          if (label.device) line += ` ${label.device}`;
          if (label.comment) line += ` ${label.comment}`;
        }
        completeCode += line + '\n';
      });
      completeCode += 'END_VAR\n\n';
    }
    
    // Add local labels section
    if (code.local_labels && code.local_labels.length > 0) {
      completeCode += 'VAR\n';
      code.local_labels.forEach(label => {
        let line = `    ${label.name} : ${label.data_type}`;
        if (label.initial_value) {
          line += ` := ${label.initial_value}`;
        }
        line += ';';
        if (label.comment) {
          line += ` // ${label.comment}`;
        }
        completeCode += line + '\n';
      });
      completeCode += 'END_VAR\n\n';
    }
    
    // Add program body
    completeCode += code.program_body || '';
    
    return completeCode;
  };
  
  const [editedCode, setEditedCode] = useState(reconstructCompleteCode());
  const [saving, setSaving] = useState(false);
  const textareaRef = useRef(null);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [editedCode]);

  const handleSave = async () => {
    setSaving(true);
    try {
      // Parse labels from edited code
      const { globalLabels, localLabels } = parseLabelsFromCode(editedCode);
      
      // Extract program body (code after VAR sections)
      let programBody = editedCode;
      const lines = editedCode.split('\n');
      let inVarSection = false;
      let bodyStartIndex = 0;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (line.startsWith('VAR_GLOBAL') || line.startsWith('VAR')) {
          inVarSection = true;
        } else if (line === 'END_VAR') {
          inVarSection = false;
          bodyStartIndex = i + 1;
        }
      }
      
      // Get code after all VAR sections
      if (bodyStartIndex > 0) {
        programBody = lines.slice(bodyStartIndex).join('\n').trim();
      }
      
      await onSave(programBody, globalLabels, localLabels);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e) => {
    setEditedCode(e.target.value);
  };

  return (
    <div className="code-editor">
      <div className="editor-header">
        <h3> Edit Generated Code</h3>
        <div className="editor-info">
          Modify the generated code. Label changes will be synchronized across the project.
        </div>
      </div>

      <div className="editor-actions-top">
        <button onClick={onCancel} className="btn-cancel">
          Cancel
        </button>
        <button 
          onClick={handleSave} 
          disabled={saving || !editedCode.trim()}
          className="btn-save"
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="editor-body">
        <textarea
          ref={textareaRef}
          value={editedCode}
          onChange={handleChange}
          className="code-textarea auto-resize"
          placeholder="Edit generated code..."
        />
        <div className="word-count">
          {editedCode.split('\n').length} lines
        </div>
      </div>
    </div>
  );
}

export default CodeEditor;
