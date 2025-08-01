import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  BooleanField,
  DateField,
  Edit,
  Create,
  SimpleForm,
  TextInput,
  BooleanInput,
  required,
  EditButton,
  DeleteButton,
} from 'react-admin';

export const ParameterList = (props) => (
  <List {...props} title="Extraction Parameters">
    <Datagrid rowClick="edit">
      <TextField source="name" />
      <TextField source="description" />
      <BooleanField source="active" />
      <DateField source="created_at" showTime />
      <EditButton />
      <DeleteButton />
    </Datagrid>
  </List>
);

export const ParameterEdit = (props) => (
  <Edit {...props} title="Edit Parameter">
    <SimpleForm>
      <TextInput source="name" validate={[required()]} />
      <TextInput source="description" multiline rows={3} />
      <BooleanInput source="active" />
    </SimpleForm>
  </Edit>
);

export const ParameterCreate = (props) => (
  <Create {...props} title="Create Parameter">
    <SimpleForm>
      <TextInput source="name" validate={[required()]} />
      <TextInput source="description" multiline rows={3} />
      <BooleanInput source="active" defaultValue={true} />
    </SimpleForm>
  </Create>
);
