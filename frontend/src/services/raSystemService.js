import api from './api';
import environment from '../config/environment';

const raSystemService = {
  async uploadSafetyManual(projectId, file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    const response = await api.post('/api/ra/upload-safety-manual', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  async performSafetyCheck(stageId) {
    const response = await api.post('/api/ra/safety-check', {
      stage_id: stageId
    });
    return response.data;
  },

  async getDefaultSafetyStatus() {
    const response = await api.get('/api/ra/default-safety-status');
    return response.data;
  },

  async processDefaultManuals() {
    const response = await api.post('/api/ra/process-default-manuals');
    return response.data;
  },

  async getSafetyManualStatus(projectId) {
    const response = await api.get(`/api/ra/safety-manual/${projectId}`);
    return response.data;
  },

  async interrogateCode(stageId) {
    const response = await api.post('/api/ra/interrogate', {
      stage_id: stageId
    });
    return response.data;
  }
};

export default raSystemService;