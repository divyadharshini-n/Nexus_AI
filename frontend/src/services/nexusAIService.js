import api from './api';

const nexusAIService = {
  async chat(projectId, message) {
    const response = await api.post('/api/nexus/chat', {
      project_id: projectId,
      message
    });
    return response.data;
  }
};

export default nexusAIService;