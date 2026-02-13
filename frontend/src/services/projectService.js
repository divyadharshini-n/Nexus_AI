import api from './api';

const projectService = {
  async createProject(name, description) {
    const response = await api.post('/api/projects/create', {
      name,
      description
    });
    return response.data;
  },

  async listProjects() {
    const response = await api.get('/api/projects/list');
    return response.data;
  },

  async getProject(projectId) {
    const response = await api.get(`/api/projects/${projectId}`);
    return response.data;
  },

  async deleteProject(projectId) {
    await api.delete(`/api/projects/${projectId}`);
  }
};

export default projectService;