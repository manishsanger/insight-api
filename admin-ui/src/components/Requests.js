import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  DateField,
  Show,
  SimpleShowLayout,
  RichTextField,
  Filter,
  TextInput,
  DateInput,
  SelectInput,
} from 'react-admin';

const RequestFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search" source="q" alwaysOn />
    <SelectInput source="status" choices={[
      { id: 'success', name: 'Success' },
      { id: 'error', name: 'Error' },
    ]} />
    <DateInput source="start_date" />
    <DateInput source="end_date" />
  </Filter>
);

export const RequestList = (props) => (
  <List {...props} title="API Requests" filters={<RequestFilter />}>
    <Datagrid rowClick="show">
      <TextField source="endpoint" />
      <TextField source="status" />
      <DateField source="created_at" showTime />
      <TextField source="extraction_id" />
      <TextField source="error" />
    </Datagrid>
  </List>
);

export const RequestShow = (props) => (
  <Show {...props} title="Request Details">
    <SimpleShowLayout>
      <TextField source="endpoint" />
      <TextField source="status" />
      <DateField source="created_at" showTime />
      <TextField source="extraction_id" />
      <RichTextField source="error" />
    </SimpleShowLayout>
  </Show>
);
