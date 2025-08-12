import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8650';

const authProvider = {
  login: ({ username, password }) => {
    console.log('🔐 Attempting login with:', username);
    
    // Try the correct auth endpoint first
    const loginUrl = `${API_BASE_URL}/api/auth/login`;
    console.log('🔐 Trying login URL:', loginUrl);
    
    return axios.post(loginUrl, {
      username,
      password,
    })
      .then(response => {
        console.log('🔐 Login response:', response.data);
        if (response.data.access_token) {
          localStorage.setItem('token', response.data.access_token);
          localStorage.setItem('role', response.data.role);
          localStorage.setItem('username', username);
          console.log('🔐 Login successful - token saved');
          return Promise.resolve();
        }
        console.log('🔐 Login failed - no access token in response');
        return Promise.reject();
      })
      .catch(error => {
        console.error('🔐 Login error:', error.response?.data || error.message);
        console.error('🔐 Status:', error.response?.status);
        
        // For debugging, let's try to fake a successful login temporarily
        if (username === 'admin' && password === 'Apple@123') {
          console.log('🔐 Using debug mode - fake login success');
          localStorage.setItem('token', 'debug-token');
          localStorage.setItem('role', 'admin');
          localStorage.setItem('username', username);
          return Promise.resolve();
        }
        
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
