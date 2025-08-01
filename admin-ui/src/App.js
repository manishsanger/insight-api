import React from 'react';
import { Admin, Resource, ListGuesser, EditGuesser, ShowGuesser } from 'react-admin';
import { BrowserRouter } from 'react-router-dom';
import dataProvider from './dataProvider';
import authProvider from './authProvider';
import Dashboard from './DashboardComponent';
import { ParameterList, ParameterEdit, ParameterCreate } from './components/Parameters';
import { RequestList } from './components/Requests';
import { UserList, UserEdit, UserCreate } from './components/Users';

const App = () => (
  <BrowserRouter>
    <Admin
      dataProvider={dataProvider}
      authProvider={authProvider}
      dashboard={Dashboard}
      title="Insight Admin Panel"
    >
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
