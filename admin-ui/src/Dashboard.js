import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, Title } from 'react-admin';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import dataProvider from './dataProvider';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_requests: 0,
    successful_requests: 0,
    error_requests: 0,
    success_rate: 0,
  });
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    fetchDashboardData();
  }, [dateRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dataProvider.getDashboard(dateRange);
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (field, value) => {
    setDateRange(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  const chartData = [
    { name: 'Successful', value: stats.successful_requests, color: '#4CAF50' },
    { name: 'Failed', value: stats.error_requests, color: '#F44336' },
  ];

  return (
    <div style={{ padding: '20px' }}>
      <Title title="Dashboard" />
      
      {/* Date Range Selector */}
      <Card style={{ marginBottom: '20px' }}>
        <CardHeader title="Filter by Date Range" />
        <CardContent>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <div>
              <label>Start Date:</label>
              <input
                type="date"
                value={dateRange.start_date}
                onChange={(e) => handleDateChange('start_date', e.target.value)}
                style={{ marginLeft: '10px', padding: '5px' }}
              />
            </div>
            <div>
              <label>End Date:</label>
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

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <Card>
          <CardContent>
            <h3 style={{ margin: 0, color: '#1976d2' }}>Total Requests</h3>
            <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#1976d2' }}>
              {stats.total_requests}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <h3 style={{ margin: 0, color: '#4CAF50' }}>Successful Requests</h3>
            <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#4CAF50' }}>
              {stats.successful_requests}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <h3 style={{ margin: 0, color: '#F44336' }}>Failed Requests</h3>
            <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#F44336' }}>
              {stats.error_requests}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <h3 style={{ margin: 0, color: '#FF9800' }}>Success Rate</h3>
            <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#FF9800' }}>
              {stats.success_rate.toFixed(1)}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        <Card>
          <CardHeader title="Request Status Distribution" />
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader title="Success Rate Visualization" />
          <CardContent>
            <div style={{ textAlign: 'center', padding: '50px' }}>
              <div style={{
                width: '200px',
                height: '200px',
                borderRadius: '50%',
                background: `conic-gradient(#4CAF50 0deg ${stats.success_rate * 3.6}deg, #F44336 ${stats.success_rate * 3.6}deg 360deg)`,
                margin: '0 auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px',
                fontWeight: 'bold',
                color: 'white',
                textShadow: '1px 1px 2px rgba(0,0,0,0.7)'
              }}>
                {stats.success_rate.toFixed(1)}%
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
