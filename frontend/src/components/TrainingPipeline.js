import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-gateway-url.amazonaws.com/prod';

function TrainingPipeline() {
  const [formData, setFormData] = useState({
    datasetUri: 's3://mlops-data-bucket/diabetic_data.csv',
    modelName: 'medication-adherence-model',
    algorithm: 'RandomForest',
    instanceType: 'ml.m5.xlarge',
    maxRuntime: 3600,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/training/start`, formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to start training job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Training Pipeline
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Train a medication adherence prediction model using diabetic patient data
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="Dataset S3 URI"
              name="datasetUri"
              value={formData.datasetUri}
              onChange={handleChange}
              fullWidth
              required
              helperText="S3 path to the training dataset (CSV format)"
            />

            <TextField
              label="Model Name"
              name="modelName"
              value={formData.modelName}
              onChange={handleChange}
              fullWidth
              required
            />

            <FormControl fullWidth>
              <InputLabel>Algorithm</InputLabel>
              <Select
                name="algorithm"
                value={formData.algorithm}
                onChange={handleChange}
                label="Algorithm"
              >
                <MenuItem value="RandomForest">Random Forest</MenuItem>
                <MenuItem value="XGBoost">XGBoost</MenuItem>
                <MenuItem value="LogisticRegression">Logistic Regression</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Instance Type</InputLabel>
              <Select
                name="instanceType"
                value={formData.instanceType}
                onChange={handleChange}
                label="Instance Type"
              >
                <MenuItem value="ml.m5.large">ml.m5.large</MenuItem>
                <MenuItem value="ml.m5.xlarge">ml.m5.xlarge</MenuItem>
                <MenuItem value="ml.m5.2xlarge">ml.m5.2xlarge</MenuItem>
                <MenuItem value="ml.c5.xlarge">ml.c5.xlarge</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Max Runtime (seconds)"
              name="maxRuntime"
              type="number"
              value={formData.maxRuntime}
              onChange={handleChange}
              fullWidth
            />

            <Button
              type="submit"
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
              disabled={loading}
            >
              {loading ? 'Starting Training...' : 'Start Training'}
            </Button>
          </Box>
        </form>

        {error && (
          <Alert severity="error" sx={{ mt: 3 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Alert severity="success" sx={{ mt: 3 }}>
            Training job started successfully!
            <br />
            Job ID: {result.trainingJobId}
            <br />
            Status: {result.status}
          </Alert>
        )}
      </Paper>
    </Container>
  );
}

export default TrainingPipeline;
