import api from './api';

const aiDudeService = {
  async query(projectId, question, codeContext = null) {
    const response = await api.post('/api/aidude/query', {
      project_id: projectId,
      question,
      code_context: codeContext
    });
    return response.data;
  }
};

export default aiDudeService;