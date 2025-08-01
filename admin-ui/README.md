# Admin UI

A responsive React-based admin panel for managing the Insight API system.

## Features

- **Dashboard**: Overview of system statistics and performance metrics
- **Parameter Management**: Create, edit, and manage information extraction parameters
- **Request Monitoring**: View and filter all API requests and responses
- **User Management**: Manage system users and their roles
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Date Range Filtering**: Filter data by custom date ranges
- **Real-time Charts**: Visual representation of system metrics
- **JWT Authentication**: Secure admin access
- **Health Monitoring**: Service health status

## Dashboard Features

### Statistics Cards
- Total API requests
- Successful requests
- Failed requests
- Success rate percentage

### Interactive Charts
- Request status distribution (bar chart)
- Success rate visualization (pie chart)
- Date range filtering

### Date Range Filtering
- Custom start and end date selection
- Real-time data updates
- Historical data analysis

## Parameter Management

### Features
- View all extraction parameters
- Create new parameters
- Edit existing parameters
- Enable/disable parameters
- Delete parameters

### Parameter Fields
- **Name**: Unique parameter identifier
- **Description**: Human-readable description
- **Active**: Enable/disable status
- **Created At**: Creation timestamp

## Request Monitoring

### Features
- View all API requests
- Filter by status (success/error)
- Filter by date range
- Search functionality
- Pagination support

### Request Information
- Endpoint accessed
- Request status
- Timestamp
- Extraction ID (for successful requests)
- Error details (for failed requests)

## User Management

### Features
- View all system users
- Create new users
- Edit user details
- Manage user roles
- Delete users

### User Roles
- **Admin**: Full system access
- **User**: Limited API access

## Authentication

### Login Credentials
- **Username**: admin
- **Password**: Apple@123

### Security Features
- JWT token-based authentication
- Automatic token refresh
- Session timeout handling
- Role-based access control

## Technology Stack

### Frontend
- React 18.2.0
- React Admin 4.12.0
- Recharts 2.7.2 (for charts)
- Axios 1.4.0 (for API calls)
- React Router DOM 6.14.1

### Backend (Node.js Server)
- Express 4.18.2
- CORS 2.8.5
- Static file serving

## API Integration

### Base URL Configuration
The admin UI connects to the Officer Insight API using the base URL configured in environment variables:
- **Development**: http://localhost:8650
- **Production**: Configurable via REACT_APP_API_BASE_URL

### Endpoints Used
- `POST /auth/login` - Authentication
- `GET /admin/parameters` - Parameter management
- `POST /admin/parameters` - Create parameters
- `PUT /admin/parameters/{id}` - Update parameters
- `DELETE /admin/parameters/{id}` - Delete parameters
- `GET /admin/requests` - Request monitoring
- `GET /admin/dashboard` - Dashboard data
- `GET /admin/users` - User management

## Running Locally

### Development Mode
1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
export REACT_APP_API_BASE_URL="http://localhost:8650"
```

3. Start development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

### Production Mode
1. Build the application:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

The application will be available at http://localhost:8651

## Docker Usage

### Build Image
```bash
docker build -t admin-ui .
```

### Run Container
```bash
docker run -d \
  -p 8651:8651 \
  -e REACT_APP_API_BASE_URL="http://localhost:8650" \
  admin-ui
```

## Environment Variables

- `REACT_APP_API_BASE_URL`: Base URL for Officer Insight API
- `NODE_ENV`: Environment mode (development/production)
- `PORT`: Port number for the server (default: 8651)

## Component Structure

```
src/
├── App.js                 # Main application component
├── index.js              # Application entry point
├── Dashboard.js          # Dashboard component
├── dataProvider.js       # API data provider
├── authProvider.js       # Authentication provider
└── components/
    ├── Parameters.js     # Parameter management
    ├── Requests.js       # Request monitoring
    └── Users.js          # User management
```

## Data Provider

The data provider handles all API communications:
- CRUD operations for all resources
- Authentication token management
- Error handling and retries
- Response data normalization

## Auth Provider

The auth provider manages authentication:
- Login/logout functionality
- Token storage and retrieval
- Role-based access control
- Session management

## Responsive Design

The UI is designed to work on all device sizes:
- **Desktop**: Full feature set with side navigation
- **Tablet**: Responsive layout with touch-friendly controls
- **Mobile**: Optimized for small screens with collapsible navigation

## Error Handling

### Authentication Errors
- Automatic redirect to login on 401 errors
- Token refresh handling
- Session timeout notifications

### API Errors
- User-friendly error messages
- Retry mechanisms for failed requests
- Network connectivity detection

### Validation
- Client-side form validation
- Required field enforcement
- Data type validation

## Performance Optimization

### Features
- Lazy loading of components
- API response caching
- Optimized bundle size
- Image optimization

### Build Optimization
- Code splitting
- Tree shaking
- Minification
- Gzip compression

## Health Check

The application provides a health check endpoint at `/health`:

```json
{
  "status": "healthy",
  "timestamp": "2024-07-25T10:30:00Z",
  "service": "admin-ui"
}
```

## Testing

### Run Tests
```bash
npm test
```

### Test Coverage
- Component rendering tests
- Authentication flow tests
- API integration tests
- User interaction tests

## Deployment

### Production Build
```bash
npm run build
```

### Static File Serving
The production build serves static files through Express.js with:
- Gzip compression
- Browser caching
- SPA routing support

## Monitoring

### Available Metrics
- User login activities
- Page view analytics
- API response times
- Error tracking

### Health Monitoring
- Service availability
- API connectivity
- Authentication status

## Customization

### Themes
The application supports custom themes through React Admin's theming system:
- Color schemes
- Typography
- Component styling
- Layout customization

### Branding
- Custom logo integration
- Application title
- Favicon
- Color branding

## Security Features

### Authentication
- JWT token validation
- Role-based access control
- Session management
- Automatic logout on inactivity

### Data Protection
- HTTPS enforcement (in production)
- XSS protection
- CSRF protection
- Input sanitization

## Browser Support

### Supported Browsers
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Mobile Browsers
- iOS Safari
- Chrome Mobile
- Firefox Mobile

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check API connectivity
   - Verify credentials
   - Check token expiration

2. **Data Loading Issues**
   - Verify API endpoints
   - Check network connectivity
   - Review CORS configuration

3. **UI Display Issues**
   - Clear browser cache
   - Check console for errors
   - Verify responsive breakpoints
