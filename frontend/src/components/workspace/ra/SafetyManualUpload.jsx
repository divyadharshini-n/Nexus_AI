import React, { useState } from 'react';
import '../../../styles/SafetyManualUpload.css';

function SafetyManualUpload({ projectId, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile) => {
    const allowedTypes = ['pdf', 'docx', 'doc', 'txt'];
    const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      alert('Only PDF, DOCX, and TXT files are supported');
      return;
    }
    
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file || !onUploadSuccess) return;

    setUploading(true);
    try {
      await onUploadSuccess(file);
      setFile(null);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="safety-manual-upload">
      <h4>🛡️ Upload Safety Manual</h4>
      <p className="upload-description">
        Upload your company's safety manual for code safety validation
      </p>
      
      <form
        className={`upload-form-sm ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onSubmit={(e) => e.preventDefault()}
      >
        <input
          type="file"
          id="safety-manual-input"
          onChange={handleChange}
          accept=".pdf,.docx,.doc,.txt"
          style={{ display: 'none' }}
        />
        
        <div className="upload-area-sm">
          {file ? (
            <div className="file-selected-sm">
              <p>📄 {file.name}</p>
              <p className="file-size-sm">{(file.size / 1024).toFixed(2)} KB</p>
              <button type="button" onClick={() => setFile(null)} className="btn-remove-sm">
                Remove
              </button>
            </div>
          ) : (
            <div className="upload-prompt-sm">
              <p>📁 Drop safety manual here</p>
              <p className="or-text-sm">or</p>
              <label htmlFor="safety-manual-input" className="btn-browse-sm">
                Browse Files
              </label>
              <p className="supported-types-sm">
                PDF, DOCX, TXT
              </p>
            </div>
          )}
        </div>
      </form>

      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="btn-upload-sm"
        >
          {uploading ? 'Uploading...' : 'Upload Safety Manual'}
        </button>
      )}
    </div>
  );
}

export default SafetyManualUpload;