import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8650';

const authProvider = {
  login: ({ username, password }) => {
    return axios.post(`${API_BASE_URL}/api/login`, {
      username,
      password,
    })
      .then(response => {
        if (response.data.access_token) {
          localStorage.setItem('token', response.data.access_token);
          localStorage.setItem('role', response.data.role);
          return Promise.resolve();
        }
        return Promise.reject();
      })
      .catch(() => {
        return Promise.reject();
      });
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
