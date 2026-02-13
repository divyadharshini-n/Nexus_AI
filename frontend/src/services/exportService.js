import environment from '../config/environment';

const exportService = {
  async exportProjectCSV(projectId) {
    const token = localStorage.getItem('access_token');
    const url = `${environment.API_BASE_URL}/api/export/csv/project/${projectId}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      
      // Get filename from headers
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'code_export.csv';
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
      console.error('Export error:', error);
      return { success: false, error: error.message };
    }
  },

  async exportStageCSV(stageId) {
    const token = localStorage.getItem('access_token');
    const url = `${environment.API_BASE_URL}/api/export/csv/stage/${stageId}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'stage_export.csv';
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
      console.error('Export error:', error);
      return { success: false, error: error.message };
    }
  }
};

export default exportService;