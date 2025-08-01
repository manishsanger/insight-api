import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8650';

const authProvider = {
  login: async ({ username, password }) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        username,
        password,
      });

      const { access_token, role } = response.data;
      
      if (role !== 'admin') {
        throw new Error('Access denied. Admin role required.');
      }

      localStorage.setItem('token', access_token);
      localStorage.setItem('role', role);
      localStorage.setItem('username', username);
      
      return Promise.resolve();
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'Login failed';
      return Promise.reject(new Error(message));
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    return Promise.resolve();
  },

  checkError: ({ status }) => {
    if (status === 401 || status === 403) {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('username');
      return Promise.reject();
    }
    return Promise.resolve();
  },

  checkAuth: () => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    
    if (token && role === 'admin') {
      return Promise.resolve();
    }
    
    return Promise.reject();
  },

  getPermissions: () => {
    const role = localStorage.getItem('role');
    return Promise.resolve(role);
  },

  getIdentity: () => {
    const username = localStorage.getItem('username');
    const role = localStorage.getItem('role');
    
    if (username && role) {
      return Promise.resolve({
        id: username,
        fullName: username,
        role: role,
      });
    }
    
    return Promise.reject();
  },
};

export default authProvider;
