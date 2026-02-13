import api from './api';

const plannerService = {
  async createPlan(projectId, controlLogic) {
    const response = await api.post('/api/planner/create-plan', {
      project_id: projectId,
      control_logic: controlLogic
    });
    return response.data;
  },

  async getProjectStages(projectId) {
    const response = await api.get(`/api/planner/stages/${projectId}`);
    return response.data;
  }
};

export default plannerService;