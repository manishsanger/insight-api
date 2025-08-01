import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8650';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const dataProvider = {
  getList: async (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;
    const query = new URLSearchParams({
      page: page,
      per_page: perPage,
      sort_field: field,
      sort_order: order,
      ...params.filter,
    });

    let url;
    switch (resource) {
      case 'parameters':
        url = '/admin/parameters';
        break;
      case 'requests':
        url = '/admin/requests';
        break;
      case 'users':
        url = '/admin/users';
        break;
      default:
        throw new Error(`Unknown resource: ${resource}`);
    }

    const { data } = await apiClient.get(`${url}?${query}`);
    
    return {
      data: data[resource] || data.data || [],
      total: data.total || 0,
    };
  },

  getOne: async (resource, params) => {
    let url;
    switch (resource) {
      case 'parameters':
        url = `/admin/parameters/${params.id}`;
        break;
      case 'requests':
        url = `/admin/requests/${params.id}`;
        break;
      case 'users':
        url = `/admin/users/${params.id}`;
        break;
      default:
        throw new Error(`Unknown resource: ${resource}`);
    }

    const { data } = await apiClient.get(url);
    return { data };
  },

  getMany: async (resource, params) => {
    const query = new URLSearchParams({
      ids: params.ids.join(','),
    });

    let url;
    switch (resource) {
      case 'parameters':
        url = '/admin/parameters';
        break;
      case 'requests':
        url = '/admin/requests';
        break;
      case 'users':
        url = '/admin/users';
        break;
      default:
        throw new Error(`Unknown resource: ${resource}`);
    }

    const { data } = await apiClient.get(`${url}?${query}`);
    return { data: data[resource] || data.data || [] };
  },

  getManyReference: async (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;
    const query = new URLSearchParams({
      page: page,
      per_page: perPage,
      sort_field: field,
      sort_order: order,
      [params.target]: params.id,
      ...params.filter,
    });

    let url;
    switch (resource) {
      case 'parameters':
        url = '/admin/parameters';
        break;
      case 'requests':
        url = '/admin/requests';
        break;
      case 'users':
        url = '/admin/users';
        break;
      default:
        throw new Error(`Unknown resource: ${resource}`);
    }

    const { data } = await apiClient.get(`${url}?${query}`);
    
    return {
      data: data[resource] || data.data || [],
      total: data.total || 0,
    };
  },

  create: async (resource, params) => {
    let url;
    switch (resource) {
      case 'parameters':
        url = '/admin/parameters';
        break;
      case 'users':
        url = '/admin/users';
        break;
      default:
        throw new Error(`Unknown resource: ${resource}`);
    }

    const { data } = await apiClient.post(url, params.data);
    return { data };
  },

  update: async (resource, params) => {
    let url;
    switch (resource) {
      case 'parameters':
        url = `/admin/parameters/${params.id}`;
        break;
      case 'users':
        url = `/admin/users/${params.id}`;
        break;
      default:
        throw new Error(`Unknown resource: ${resource}`);
    }

    const { data } = await apiClient.put(url, params.data);
    return { data };
  },

  updateMany: async (resource, params) => {
    const promises = params.ids.map(id =>
      dataProvider.update(resource, { id, data: params.data })
    );
    const results = await Promise.all(promises);
    return { data: results.map(result => result.data) };
  },

  delete: async (resource, params) => {
    let url;
    switch (resource) {
      case 'parameters':
        url = `/admin/parameters/${params.id}`;
        break;
      case 'users':
        url = `/admin/users/${params.id}`;
        break;
      default:
        throw new Error(`Unknown resource: ${resource}`);
    }

    await apiClient.delete(url);
    return { data: params.previousData };
  },

  deleteMany: async (resource, params) => {
    const promises = params.ids.map(id =>
      dataProvider.delete(resource, { id })
    );
    const results = await Promise.all(promises);
    return { data: results.map(result => result.data) };
  },

  // Custom method for dashboard data
  getDashboard: async (params = {}) => {
    const query = new URLSearchParams(params);
    const { data } = await apiClient.get(`/admin/dashboard?${query}`);
    return data;
  },
};

export default dataProvider;
