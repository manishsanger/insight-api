// Mock data provider for testing - always returns proper Promise rejections
const mockDataProvider = {
  getList: (resource, params) => {
    console.log(`🟡 Mock getList called for ${resource}`, params);
    
    const mockData = {
      parameters: [
        { id: '1', name: 'test_param', description: 'Test parameter', active: true },
        { id: '2', name: 'another_param', description: 'Another parameter', active: false },
      ],
      requests: [
        { id: '1', method: 'GET', endpoint: '/api/test', status: 'success' },
        { id: '2', method: 'POST', endpoint: '/api/data', status: 'failed' },
      ],
      users: [
        { id: '1', username: 'admin', role: 'admin', active: true },
        { id: '2', username: 'user', role: 'user', active: true },
      ],
    };

    return Promise.resolve({
      data: mockData[resource] || [],
      total: mockData[resource]?.length || 0,
    });
  },

  getOne: (resource, params) => {
    console.log(`🟡 Mock getOne called for ${resource}`, params);
    
    const mockItem = {
      id: params.id,
      name: `Mock ${resource}`,
      description: `Mock description for ${resource} ${params.id}`,
      active: true,
    };

    return Promise.resolve({ data: mockItem });
  },

  getMany: (resource, params) => {
    console.log(`🟡 Mock getMany called for ${resource}`, params);
    
    const mockData = params.ids.map(id => ({
      id,
      name: `Mock ${resource} ${id}`,
      description: `Mock description`,
      active: true,
    }));

    return Promise.resolve({ data: mockData });
  },

  getManyReference: (resource, params) => {
    console.log(`🟡 Mock getManyReference called for ${resource}`, params);
    
    return Promise.resolve({
      data: [],
      total: 0,
    });
  },

  create: (resource, params) => {
    console.log(`🟡 Mock create called for ${resource}`, params);
    
    const newItem = {
      id: Date.now().toString(),
      ...params.data,
    };

    return Promise.resolve({ data: newItem });
  },

  update: (resource, params) => {
    console.log(`🟡 Mock update called for ${resource}`, params);
    
    const updatedItem = {
      id: params.id,
      ...params.data,
    };

    return Promise.resolve({ data: updatedItem });
  },

  updateMany: (resource, params) => {
    console.log(`🟡 Mock updateMany called for ${resource}`, params);
    
    return Promise.resolve({ data: params.ids });
  },

  delete: (resource, params) => {
    console.log(`🟡 Mock delete called for ${resource}`, params);
    
    return Promise.resolve({ data: { id: params.id } });
  },

  deleteMany: (resource, params) => {
    console.log(`🟡 Mock deleteMany called for ${resource}`, params);
    
    return Promise.resolve({ data: params.ids });
  },

  // Custom methods
  getDashboard: (dateRange) => {
    console.log(`🟡 Mock getDashboard called`, dateRange);
    
    return Promise.resolve({
      total_requests: 150,
      successful_requests: 135,
      error_requests: 15,
      success_rate: 90.0,
    });
  },
};

// Wrapper to ensure all methods always return promises and handle errors properly
const wrappedMockDataProvider = {};

Object.keys(mockDataProvider).forEach(method => {
  wrappedMockDataProvider[method] = (...args) => {
    try {
      console.log(`🔵 Mock DataProvider ${method} called with args:`, args);
      
      const result = mockDataProvider[method](...args);
      
      // Ensure result is always a Promise
      if (result && typeof result.then === 'function') {
        return result.catch(error => {
          console.error(`❌ Mock DataProvider ${method} error:`, error);
          return Promise.reject(new Error(`Mock ${method} failed: ${error.message}`));
        });
      } else {
        return Promise.resolve(result);
      }
    } catch (error) {
      console.error(`💥 Mock DataProvider ${method} synchronous error:`, error);
      return Promise.reject(new Error(`Mock ${method} failed: ${error.message}`));
    }
  };
});

export default wrappedMockDataProvider;
