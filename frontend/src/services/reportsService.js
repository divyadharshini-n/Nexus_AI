import environment from '../config/environment';

const reportsService = {
  async generateDOCXReport(projectId) {
    const token = localStorage.getItem('access_token');
    const url = `${environment.API_BASE_URL}/api/reports/docx/${projectId}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Report generation failed');
      }
      
      // Get filename from headers
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'project_report.docx';
      if (contentDisposition) {
        const matches = /filename=(.+)/.exec(contentDisposition);
        if (matches && matches[1]) {
          filename = matches[1];
        }
      }
      
      // Download file
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
      
      return { success: true };
    } catch (error) {
      console.error('DOCX report error:', error);
      return { success: false, error: error.message };
    }
  },

  async generateAuditTrailReport(projectId) {
    const token = localStorage.getItem('access_token');
    const url = `${environment.API_BASE_URL}/api/reports/audit-trail/${projectId}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        let errorMessage = 'Audit trail report generation failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If JSON parsing fails, use status text
          errorMessage = `${errorMessage} (${response.status} ${response.statusText})`;
        }
        throw new Error(errorMessage);
      }
      
      // Get filename from headers
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'audit_trail_report.pdf';
      if (contentDisposition) {
        const matches = /filename=(.+)/.exec(contentDisposition);
        if (matches && matches[1]) {
          filename = matches[1];
        }
      }
      
      // Download file
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
      
      return { success: true };
    } catch (error) {
      console.error('Audit trail report error:', error);
      return { success: false, error: error.message };
    }
  },

  async generatePDFReport(projectId) {
    const token = localStorage.getItem('access_token');
    const url = `${environment.API_BASE_URL}/api/reports/pdf/${projectId}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Report generation failed');
      }
      
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'project_report.pdf';
      if (contentDisposition) {
        const matches = /filename=(.+)/.exec(contentDisposition);
        if (matches && matches[1]) {
          filename = matches[1];
        }
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
      
      return { success: true };
    } catch (error) {
      console.error('PDF report error:', error);
      return { success: false, error: error.message };
    }
  },

  async getReportSummary(projectId) {
    const token = localStorage.getItem('access_token');
    const url = `${environment.API_BASE_URL}/api/reports/summary/${projectId}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to get summary');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Summary error:', error);
      throw error;
    }
  }
};

export default reportsService;