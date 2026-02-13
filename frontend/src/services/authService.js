import api from './api';

const authService = {
  async login(username, password) {
    const response = await api.post('/api/auth/login', {
      username,
      password
    });
    
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    
    return response.data;
  },

  async register(username, email, password, fullName) {
    const response = await api.post('/api/auth/register', {
      username,
      email,
      password,
      full_name: fullName
    });
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  getToken() {
    return localStorage.getItem('access_token');
  },

  logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/home';
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
};

export default authService;