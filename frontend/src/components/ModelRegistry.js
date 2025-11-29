import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  IconButton,
} from '@mui/material';
import { CheckCircle, Cancel, Refresh } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-gateway-url.amazonaws.com/prod';

function ModelRegistry() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/models`);
      setModels(response.data.models || []);
    } catch (error) {
      console.error('Error fetching models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (modelVersion) => {
    try {
      await axios.post(`${API_BASE_URL}/models/${modelVersion}/approve`);
      fetchModels();
    } catch (error) {
      console.error('Error approving model:', error);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Model Registry
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchModels}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Model Group</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Algorithm</TableCell>
                <TableCell>Accuracy</TableCell>
                <TableCell>F1 Score</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {models.map((model) => (
                <TableRow key={model.version}>
                  <TableCell>{model.modelGroup}</TableCell>
                  <TableCell>{model.version}</TableCell>
                  <TableCell>{model.algorithm}</TableCell>
                  <TableCell>{(model.metrics.accuracy * 100).toFixed(1)}%</TableCell>
                  <TableCell>{(model.metrics.f1Score * 100).toFixed(1)}%</TableCell>
                  <TableCell>
                    <Chip
                      label={model.approvalStatus}
                      color={model.approvalStatus === 'approved' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{new Date(model.createdAt).toLocaleDateString()}</TableCell>
                  <TableCell>
                    {model.approvalStatus === 'pending' && (
                      <IconButton
                        color="success"
                        onClick={() => handleApprove(model.version)}
                        size="small"
                      >
                        <CheckCircle />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
}

export default ModelRegistry;
