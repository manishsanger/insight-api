import React from 'react';
import { Admin, Resource } from 'react-admin';
import { BrowserRouter } from 'react-router-dom';
import dataProvider from './dataProvider';
import authProvider from './authProvider';
import Dashboard from './DashboardComponent';
import { ParameterList, ParameterEdit, ParameterCreate } from './components/Parameters';
import { RequestList } from './components/Requests';
import { UserList, UserEdit, UserCreate } from './components/Users';

console.log('🚀 App.js loading...');
console.error('🚨 About to import dataProvider...');
console.log('✅ DataProvider imported successfully:', dataProvider);
console.error('🚨 DataProvider imported:', typeof dataProvider);

// Use real data provider with Headers fix
const selectedDataProvider = dataProvider; // Change to mockDataProvider if needed for debugging

const App = () => (
  <BrowserRouter>
    <Admin
      dataProvider={selectedDataProvider}
      authProvider={authProvider}
      dashboard={Dashboard}
      title="Insight Admin Panel"
    >
      {/* Testing resources one by one to identify dataProvider errors */}
      <Resource
        name="parameters"
        list={ParameterList}
        edit={ParameterEdit}
        create={ParameterCreate}
      />
      <Resource
        name="requests"
        list={RequestList}
      />
      <Resource
        name="users"
        list={UserList}
        edit={UserEdit}
        create={UserCreate}
      />
    </Admin>
  </BrowserRouter>
);

export default App;
