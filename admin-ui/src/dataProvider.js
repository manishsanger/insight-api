import { fetchUtils } from 'react-admin';

// Get API base URL from environment or default to localhost
const apiUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8650';

// Custom HTTP client that includes JWT token
const httpClient = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        // Return a rejected Promise instead of throwing an error
        reject(new Error('No authentication token found'));
        return;
      }
      
      // Ensure headers are properly formatted
      const headers = new Headers();
      headers.set('Authorization', `Bearer ${token}`);
      headers.set('Content-Type', 'application/json');
      
      // Add any existing headers
      if (options.headers) {
        Object.keys(options.headers).forEach(key => {
          headers.set(key, options.headers[key]);
        });
      }
      
      const customOptions = {
        ...options,
        headers: headers,
      };
      
      fetchUtils.fetchJson(url, customOptions)
        .then(result => {
          resolve(result);
        })
        .catch(error => {
          console.error('HTTP Client Error:', error);
          // Always reject with a proper error
          reject(new Error(`HTTP request failed: ${error.message || error}`));
        });
    } catch (error) {
      console.error('HTTP Client Setup Error:', error);
      // Always reject with a proper error
      reject(new Error(`HTTP client setup failed: ${error.message || error}`));
    }
  });
};

// Helper function to get the correct URL for a resource
const getResourceUrl = (resource) => {
  switch (resource) {
    case 'parameters':
      return `${apiUrl}/api/admin/parameters`;
    case 'requests':
      return `${apiUrl}/api/admin/requests`;
    case 'users':
      return `${apiUrl}/api/admin/users`;
    default:
      return `${apiUrl}/api/admin/${resource}`;
  }
};

// Data provider that maps to backend API structure - ALL methods return explicit Promises
const dataProvider = {
  getList: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        // Check authentication before proceeding
        const token = localStorage.getItem('token');
        if (!token) {
          reject(new Error('Authentication required'));
          return;
        }

        const { page, perPage } = params.pagination || { page: 1, perPage: 10 };
        const { field, order } = params.sort || { field: 'id', order: 'ASC' };
        
        const baseUrl = getResourceUrl(resource);
        const url = `${baseUrl}?page=${page}&per_page=${perPage}&sort_field=${field}&sort_order=${order}`;

        httpClient(url)
          .then(({ json }) => {
            const dataArray = json.data || [];
            resolve({
              data: dataArray,
              total: json.total || dataArray.length,
            });
          })
          .catch(error => {
            console.error('getList error:', error);
            reject(new Error(`Failed to fetch ${resource}: ${error.message}`));
          });
      } catch (error) {
        console.error('getList caught error:', error);
        reject(new Error(`Failed to process ${resource} request: ${error.message}`));
      }
    });
  },

  getOne: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        // Check authentication before proceeding
        const token = localStorage.getItem('token');
        if (!token) {
          reject(new Error('Authentication required'));
          return;
        }

        const baseUrl = getResourceUrl(resource);
        const url = `${baseUrl}/${params.id}`;

        httpClient(url)
          .then(({ json }) => {
            resolve({
              data: json,
            });
          })
          .catch(error => {
            console.error('getOne error:', error);
            reject(new Error(`Failed to fetch ${resource} ${params.id}: ${error.message}`));
          });
      } catch (error) {
        console.error('getOne caught error:', error);
        reject(new Error(`Failed to process ${resource} ${params.id} request: ${error.message}`));
      }
    });
  },

  getMany: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        const baseUrl = getResourceUrl(resource);
        const query = `ids=${JSON.stringify(params.ids)}`;
        const url = `${baseUrl}?${query}`;

        httpClient(url)
          .then(({ json }) => {
            resolve({
              data: json.data || [],
            });
          })
          .catch(error => {
            console.error('getMany error:', error);
            reject(new Error(`Failed to fetch multiple ${resource}: ${error.message}`));
          });
      } catch (error) {
        console.error('getMany caught error:', error);
        reject(new Error(`Failed to process ${resource} bulk request: ${error.message}`));
      }
    });
  },

  getManyReference: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        const { page, perPage } = params.pagination || { page: 1, perPage: 10 };
        const { field, order } = params.sort || { field: 'id', order: 'ASC' };
        
        const baseUrl = getResourceUrl(resource);
        const query = `${params.target}=${params.id}&page=${page}&per_page=${perPage}&sort_field=${field}&sort_order=${order}`;
        const url = `${baseUrl}?${query}`;

        httpClient(url)
          .then(({ json }) => {
            resolve({
              data: json.data || [],
              total: json.total || 0,
            });
          })
          .catch(error => {
            console.error('getManyReference error:', error);
            reject(new Error(`Failed to fetch ${resource} references: ${error.message}`));
          });
      } catch (error) {
        console.error('getManyReference caught error:', error);
        reject(new Error(`Failed to process ${resource} reference request: ${error.message}`));
      }
    });
  },

  create: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        // Check authentication before proceeding
        const token = localStorage.getItem('token');
        if (!token) {
          reject(new Error('Authentication required'));
          return;
        }

        const url = getResourceUrl(resource);

        httpClient(url, {
          method: 'POST',
          body: JSON.stringify(params.data),
        })
          .then(({ json }) => {
            resolve({
              data: { ...params.data, id: json.id || json.data?.id },
            });
          })
          .catch(error => {
            console.error('create error:', error);
            reject(new Error(`Failed to create ${resource}: ${error.message}`));
          });
      } catch (error) {
        console.error('create caught error:', error);
        reject(new Error(`Failed to process ${resource} creation: ${error.message}`));
      }
    });
  },

  update: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        const baseUrl = getResourceUrl(resource);
        const url = `${baseUrl}/${params.id}`;

        httpClient(url, {
          method: 'PUT',
          body: JSON.stringify(params.data),
        })
          .then(({ json }) => {
            resolve({
              data: json.data || json,
            });
          })
          .catch(error => {
            console.error('update error:', error);
            reject(new Error(`Failed to update ${resource} ${params.id}: ${error.message}`));
          });
      } catch (error) {
        console.error('update caught error:', error);
        reject(new Error(`Failed to process ${resource} ${params.id} update: ${error.message}`));
      }
    });
  },

  updateMany: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        const baseUrl = getResourceUrl(resource);
        const promises = params.ids.map(id => {
          const url = `${baseUrl}/${id}`;
          return httpClient(url, {
            method: 'PUT',
            body: JSON.stringify(params.data),
          }).catch(error => {
            console.error('updateMany individual error:', error);
            return Promise.reject(new Error(`Failed to update ${resource} ${id}: ${error.message}`));
          });
        });

        Promise.all(promises)
          .then(() => {
            resolve({ data: params.ids });
          })
          .catch(error => {
            console.error('updateMany error:', error);
            reject(new Error(`Failed to update multiple ${resource}: ${error.message}`));
          });
      } catch (error) {
        console.error('updateMany caught error:', error);
        reject(new Error(`Failed to process ${resource} bulk update: ${error.message}`));
      }
    });
  },

  delete: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        const baseUrl = getResourceUrl(resource);
        const url = `${baseUrl}/${params.id}`;

        httpClient(url, {
          method: 'DELETE',
        })
          .then(({ json }) => {
            resolve({
              data: json.data || json,
            });
          })
          .catch(error => {
            console.error('delete error:', error);
            reject(new Error(`Failed to delete ${resource} ${params.id}: ${error.message}`));
          });
      } catch (error) {
        console.error('delete caught error:', error);
        reject(new Error(`Failed to process ${resource} ${params.id} deletion: ${error.message}`));
      }
    });
  },

  deleteMany: (resource, params) => {
    return new Promise((resolve, reject) => {
      try {
        const baseUrl = getResourceUrl(resource);
        const promises = params.ids.map(id => {
          const url = `${baseUrl}/${id}`;
          return httpClient(url, {
            method: 'DELETE',
          }).catch(error => {
            console.error('deleteMany individual error:', error);
            return Promise.reject(new Error(`Failed to delete ${resource} ${id}: ${error.message}`));
          });
        });

        Promise.all(promises)
          .then(() => {
            resolve({ data: params.ids });
          })
          .catch(error => {
            console.error('deleteMany error:', error);
            reject(new Error(`Failed to delete multiple ${resource}: ${error.message}`));
          });
      } catch (error) {
        console.error('deleteMany caught error:', error);
        reject(new Error(`Failed to process ${resource} bulk deletion: ${error.message}`));
      }
    });
  },

  // Custom method for dashboard data
  getDashboard: (dateRange) => {
    return new Promise((resolve, reject) => {
      try {
        const { startDate, endDate } = dateRange || {};
        const url = `${apiUrl}/api/admin/dashboard?start_date=${startDate}&end_date=${endDate}`;
        
        httpClient(url)
          .then(({ json }) => {
            resolve(json);
          })
          .catch(error => {
            console.error('getDashboard error:', error);
            reject(new Error(`Failed to fetch dashboard data: ${error.message}`));
          });
      } catch (error) {
        console.error('getDashboard caught error:', error);
        reject(new Error(`Failed to process dashboard request: ${error.message}`));
      }
    });
  },
};

export default dataProvider;
