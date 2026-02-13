import React from 'react';
import '../../styles/PDFViewer.css';

function PDFViewer({ manual, onClose }) {
  if (!manual) return null;

  const pdfUrl = `http://localhost:8000/manuals/${encodeURIComponent(manual.file)}`;

  return (
    <div className="pdf-viewer-overlay" onClick={onClose}>
      <div className="pdf-viewer-container" onClick={(e) => e.stopPropagation()}>
        <div className="pdf-viewer-header">
          <h2 className="pdf-viewer-title">{manual.name}</h2>
          <button className="btn-close-pdf" onClick={onClose}>✕</button>
        </div>
        <div className="pdf-viewer-content">
          <iframe
            src={pdfUrl}
            title={manual.name}
            className="pdf-iframe"
          />
        </div>
      </div>
    </div>
  );
}

export default PDFViewer;
