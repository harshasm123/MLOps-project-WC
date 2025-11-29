import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Alert,
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-gateway-url.amazonaws.com/prod';

function Monitoring() {
  const [driftData, setDriftData] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchMonitoringData();
  }, []);

  const fetchMonitoringData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/monitoring/drift`);
      setDriftData(response.data.driftHistory || []);
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Error fetching monitoring data:', error);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Model Monitoring
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Data Drift Over Time
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={driftData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="driftScore" stroke="#8884d8" name="Drift Score" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Active Alerts
            </Typography>
            {alerts.length === 0 ? (
              <Typography color="textSecondary">No active alerts</Typography>
            ) : (
              alerts.map((alert, index) => (
                <Alert key={index} severity={alert.severity} sx={{ mb: 1 }}>
                  {alert.message}
                </Alert>
              ))
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Monitoring;
