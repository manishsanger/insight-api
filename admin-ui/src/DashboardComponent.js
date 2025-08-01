import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, Title } from 'react-admin';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer
} from 'recharts';
import dataProvider from './dataProvider';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_requests: 0,
    successful_requests: 0,
    error_requests: 0,
    success_rate: 0
  });
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadDashboardData();
  }, [dateRange]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dataProvider.getDashboard(dateRange);
      setStats(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (field, value) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const chartData = [
    {
      name: 'Successful',
      value: stats.successful_requests,
      color: '#4CAF50'
    },
    {
      name: 'Errors',
      value: stats.error_requests,
      color: '#f44336'
    }
  ];

  const barData = [
    {
      name: 'Total Requests',
      count: stats.total_requests
    },
    {
      name: 'Successful',
      count: stats.successful_requests
    },
    {
      name: 'Errors',
      count: stats.error_requests
    }
  ];

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div style={{ margin: '20px' }}>
      <Title title="Dashboard" />
      
      {/* Date Range Filters */}
      <Card style={{ marginBottom: '20px' }}>
        <CardHeader title="Date Range Filter" />
        <CardContent>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <div>
              <label>Start Date: </label>
              <input
                type="date"
                value={dateRange.start_date}
                onChange={(e) => handleDateChange('start_date', e.target.value)}
                style={{ marginLeft: '10px', padding: '5px' }}
              />
            </div>
            <div>
              <label>End Date: </label>
              <input
                type="date"
                value={dateRange.end_date}
                onChange={(e) => handleDateChange('end_date', e.target.value)}
                style={{ marginLeft: '10px', padding: '5px' }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
        <Card>
          <CardHeader title="Total Requests" />
          <CardContent>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2196F3' }}>
              {stats.total_requests}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader title="Successful Requests" />
          <CardContent>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4CAF50' }}>
              {stats.successful_requests}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader title="Error Requests" />
          <CardContent>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f44336' }}>
              {stats.error_requests}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader title="Success Rate" />
          <CardContent>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#FF9800' }}>
              {stats.success_rate.toFixed(1)}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        
        {/* Bar Chart */}
        <Card>
          <CardHeader title="Request Statistics" />
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#2196F3" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Pie Chart */}
        <Card>
          <CardHeader title="Success vs Error Distribution" />
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity Summary */}
      <Card style={{ marginTop: '20px' }}>
        <CardHeader title="System Overview" />
        <CardContent>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            <div>
              <h4>Performance Metrics</h4>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                <li>Average Success Rate: {stats.success_rate.toFixed(1)}%</li>
                <li>Total Processed: {stats.total_requests}</li>
                <li>Error Rate: {((stats.error_requests / stats.total_requests) * 100 || 0).toFixed(1)}%</li>
              </ul>
            </div>
            <div>
              <h4>System Health</h4>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                <li style={{ color: stats.success_rate > 90 ? '#4CAF50' : '#f44336' }}>
                  Status: {stats.success_rate > 90 ? 'Healthy' : 'Needs Attention'}
                </li>
                <li>Services: Online</li>
                <li>Database: Connected</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
