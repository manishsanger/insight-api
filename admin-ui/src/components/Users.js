import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  DateField,
  Edit,
  Create,
  SimpleForm,
  TextInput,
  SelectInput,
  required,
  EditButton,
  DeleteButton,
} from 'react-admin';

export const UserList = (props) => (
  <List {...props} title="Users">
    <Datagrid rowClick="edit">
      <TextField source="username" />
      <TextField source="role" />
      <DateField source="created_at" showTime />
      <EditButton />
      <DeleteButton />
    </Datagrid>
  </List>
);

export const UserEdit = (props) => (
  <Edit {...props} title="Edit User">
    <SimpleForm>
      <TextInput source="username" validate={[required()]} />
      <SelectInput source="role" choices={[
        { id: 'admin', name: 'Admin' },
        { id: 'user', name: 'User' },
      ]} validate={[required()]} />
    </SimpleForm>
  </Edit>
);

export const UserCreate = (props) => (
  <Create {...props} title="Create User">
    <SimpleForm>
      <TextInput source="username" validate={[required()]} />
      <TextInput source="password" type="password" validate={[required()]} />
      <SelectInput source="role" choices={[
        { id: 'admin', name: 'Admin' },
        { id: 'user', name: 'User' },
      ]} validate={[required()]} defaultValue="user" />
    </SimpleForm>
  </Create>
);
