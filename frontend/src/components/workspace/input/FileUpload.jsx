import React, { useState, useRef } from 'react';
import '../../../styles/FileUpload.css';

function FileUpload({ projectId, onTextExtracted }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const audioChunksRef = useRef([]);
  
  // Voice recording logic
  const handleStartRecording = async () => {
    audioChunksRef.current = [];
    setRecording(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new window.MediaRecorder(stream, { mimeType: 'audio/webm' });
      setMediaRecorder(recorder);
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };
      
      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
        setFile(audioFile);
        setRecording(false);
        setMediaRecorder(null);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        
        // Auto-upload the recorded audio
        await uploadAudioFile(audioFile);
      };
      
      recorder.start();
    } catch (err) {
      alert('Microphone access denied or not available.');
      setRecording(false);
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
  };

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
    // Check file type
    const allowedTypes = ['txt', 'pdf', 'docx', 'doc', 'wav', 'webm'];
    const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      alert('Unsupported file type. Allowed: TXT, PDF, DOCX, WAV, WEBM');
      return;
    }
    
    setFile(selectedFile);
  };

  // Upload audio file to voice-to-text API
  const uploadAudioFile = async (audioFile) => {
    setUploading(true);
    
    const formData = new FormData();
    formData.append('file', audioFile);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/voice/voice-to-text/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok && data.text) {
        // Insert recognized text into the input box
        onTextExtracted(data.text);
        setFile(null);
      } else {
        alert(`Voice recognition failed: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to process audio');
    } finally {
      setUploading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    try {
      const token = localStorage.getItem('access_token');
      
      // Check if it's an audio file
      const isAudio = file.type.startsWith('audio/') || 
                      ['wav', 'webm'].includes(file.name.split('.').pop().toLowerCase());
      
      if (isAudio) {
        // Use voice-to-text endpoint
        const response = await fetch('http://localhost:8000/api/voice/voice-to-text/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        const data = await response.json();

        if (response.ok && data.text) {
          onTextExtracted(data.text);
          setFile(null);
        } else {
          alert(`Voice recognition failed: ${data.detail || 'Unknown error'}`);
        }
      } else {
        // Use text extraction endpoint
        const response = await fetch('http://localhost:8000/api/input/upload', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        const data = await response.json();

        if (data.success) {
          alert(`File uploaded successfully! ${data.word_count} words extracted.`);
          onTextExtracted(data.extracted_text);
          setFile(null);
        } else {
          alert(`Upload failed: ${data.error}`);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <form
        className={`upload-form ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onSubmit={(e) => e.preventDefault()}
      >
        <input
          type="file"
          id="file-input"
          onChange={handleChange}
          accept=".txt,.pdf,.docx,.doc,.wav,.webm"
          style={{ display: 'none' }}
        />
        
        <div className="upload-area">
          {file ? (
            <div className="file-selected">
              <p> {file.name}</p>
              <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
              <button type="button" onClick={() => setFile(null)} className="btn-remove">
                Remove
              </button>
            </div>
          ) : (
            <div className="upload-prompt">
              <p> Drag & drop file here</p>
              <p className="or-text">or</p>
              <label htmlFor="file-input" className="btn-browse">
                Browse Files
              </label>
              <div style={{ margin: '16px 0' }}>
                {!recording && !uploading ? (
                  <button type="button" className="btn-record" onClick={handleStartRecording}>
                    🎤 Record Voice
                  </button>
                ) : recording ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                    <button type="button" className="btn-stop-record" onClick={handleStopRecording}>
                      ⏹️ Stop Recording
                    </button>
                    <span style={{ color: 'red', fontWeight: 'bold', animation: 'pulse 1.5s infinite' }}>
                      🔴 Recording in progress...
                    </span>
                  </div>
                ) : (
                  <span style={{ color: 'blue', fontWeight: 'bold' }}>Processing audio...</span>
                )}
              </div>
              <p className="supported-types">
                Supported: TXT, PDF, DOCX, WAV, Voice Recording
              </p>
            </div>
          )}
        </div>
      </form>

      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="btn-upload"
        >
          {uploading ? 'Uploading...' : 'Upload & Extract Text'}
        </button>
      )}
    </div>
  );
}

export default FileUpload;