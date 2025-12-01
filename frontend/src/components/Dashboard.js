import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  CheckCircle,
  Warning,
  Speed,
  Storage,
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;

if (!API_BASE_URL) {
  console.error('REACT_APP_API_URL environment variable is not set');
}

function Dashboard() {
  const [stats, setStats] = useState({
    totalModels: 0,
    activeTrainingJobs: 0,
    recentPredictions: 0,
    driftAlerts: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardStats = useCallback(async () => {
    if (!API_BASE_URL) {
      setError('API URL not configured');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/dashboard/stats`, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.data && typeof response.data === 'object') {
        setStats({
          totalModels: Number(response.data.totalModels) || 0,
          activeTrainingJobs: Number(response.data.activeTrainingJobs) || 0,
          recentPredictions: Number(response.data.recentPredictions) || 0,
          driftAlerts: Number(response.data.driftAlerts) || 0,
        });
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      setError(error.response?.data?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  const StatCard = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color: color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        MLOps Platform Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Models"
            value={stats.totalModels}
            icon={<Storage fontSize="large" />}
            color="primary.main"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Training Jobs"
            value={stats.activeTrainingJobs}
            icon={<Speed fontSize="large" />}
            color="info.main"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Recent Predictions"
            value={stats.recentPredictions}
            icon={<CheckCircle fontSize="large" />}
            color="success.main"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Drift Alerts"
            value={stats.driftAlerts}
            icon={<Warning fontSize="large" />}
            color="warning.main"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography color="textSecondary">
              Training jobs, inference runs, and model deployments will appear here.
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Health
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary">
                All systems operational
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
