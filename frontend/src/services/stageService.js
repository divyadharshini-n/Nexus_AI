import api from './api';

const stageService = {
  async updateStageLogic(stageId, editedLogic) {
    const response = await api.put('/api/stage/update-logic', {
      stage_id: stageId,
      edited_logic: editedLogic
    });
    return response.data;
  },

  async validateStage(stageId) {
    const response = await api.post('/api/stage/validate', {
      stage_id: stageId
    });
    return response.data;
  },

  async finalizeStage(stageId) {
    const response = await api.post('/api/stage/finalize', {
      stage_id: stageId
    });
    return response.data;
  },

  async getStageDetail(stageId) {
    const response = await api.get(`/api/stage/${stageId}`);
    return response.data;
  },

  async getVersionHistory(stageId) {
    const response = await api.get(`/api/stage/${stageId}/version-history`);
    return response.data;
  }
};

export default stageService;