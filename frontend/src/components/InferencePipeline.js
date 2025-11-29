import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-gateway-url.amazonaws.com/prod';

function InferencePipeline() {
  const [formData, setFormData] = useState({
    inputDataUri: 's3://mlops-data-bucket/inference_data.csv',
    modelVersion: 'latest',
  });
  const [loading, setLoading] = useState(false);
  const [predictions, setPredictions] = useState(null);
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
    setPredictions(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/inference/predict`, formData);
      setPredictions(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to run inference');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Inference Pipeline
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Generate medication adherence predictions for patient data
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="Input Data S3 URI"
              name="inputDataUri"
              value={formData.inputDataUri}
              onChange={handleChange}
              fullWidth
              required
              helperText="S3 path to the input data for predictions"
            />

            <TextField
              label="Model Version"
              name="modelVersion"
              value={formData.modelVersion}
              onChange={handleChange}
              fullWidth
              helperText="Use 'latest' for the most recent approved model"
            />

            <Button
              type="submit"
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
              disabled={loading}
            >
              {loading ? 'Running Inference...' : 'Run Inference'}
            </Button>
          </Box>
        </form>

        {error && (
          <Alert severity="error" sx={{ mt: 3 }}>
            {error}
          </Alert>
        )}

        {predictions && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Prediction Results
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              Generated {predictions.predictionCount} predictions
              <br />
              Drift Score: {predictions.driftScore?.toFixed(4)}
              {predictions.driftScore > 0.1 && ' (Warning: High drift detected)'}
            </Alert>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Patient ID</TableCell>
                    <TableCell>Medication Brand</TableCell>
                    <TableCell>Non-Adherence Probability</TableCell>
                    <TableCell>Risk Level</TableCell>
                    <TableCell>Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {predictions.predictions?.slice(0, 10).map((pred, index) => (
                    <TableRow key={index}>
                      <TableCell>{pred.patientId}</TableCell>
                      <TableCell>{pred.medicationBrand}</TableCell>
                      <TableCell>{(pred.nonAdherenceProbability * 100).toFixed(1)}%</TableCell>
                      <TableCell>
                        <Chip
                          label={pred.nonAdherenceProbability > 0.7 ? 'High' : pred.nonAdherenceProbability > 0.4 ? 'Medium' : 'Low'}
                          color={pred.nonAdherenceProbability > 0.7 ? 'error' : pred.nonAdherenceProbability > 0.4 ? 'warning' : 'success'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{(pred.confidenceScore * 100).toFixed(1)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>
    </Container>
  );
}

export default InferencePipeline;
