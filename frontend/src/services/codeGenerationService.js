import api from './api';

const codeGenerationService = {
  async generateCode(stageId) {
    const response = await api.post('/api/code/generate', {
      stage_id: stageId
    });
    return response.data;
  },

  async getStageCode(stageId) {
    const response = await api.get(`/api/code/stage/${stageId}`);
    return response.data;
  },

  async getProjectCodes(projectId) {
    const response = await api.get(`/api/code/project/${projectId}`);
    return response.data;
  },

  async updateCode(stageId, programBody, globalLabels = null, localLabels = null) {
    const response = await api.put('/api/code/update', {
      stage_id: stageId,
      program_body: programBody,
      global_labels: globalLabels,
      local_labels: localLabels
    });
    return response.data;
  }
};

export default codeGenerationService;