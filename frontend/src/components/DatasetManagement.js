import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { Upload, Refresh } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-gateway-url.amazonaws.com/prod';

function DatasetManagement() {
  const [datasets, setDatasets] = useState([]);
  const [openUpload, setOpenUpload] = useState(false);
  const [uploadData, setUploadData] = useState({
    name: '',
    s3Uri: '',
    description: '',
  });

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/datasets`);
      setDatasets(response.data.datasets || []);
    } catch (error) {
      console.error('Error fetching datasets:', error);
    }
  };

  const handleUpload = async () => {
    try {
      await axios.post(`${API_BASE_URL}/datasets/register`, uploadData);
      setOpenUpload(false);
      fetchDatasets();
    } catch (error) {
      console.error('Error uploading dataset:', error);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Dataset Management
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<Upload />}
            onClick={() => setOpenUpload(true)}
            sx={{ mr: 1 }}
          >
            Register Dataset
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchDatasets}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 3 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Rows</TableCell>
                <TableCell>Columns</TableCell>
                <TableCell>Size</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {datasets.map((dataset) => (
                <TableRow key={dataset.id}>
                  <TableCell>{dataset.name}</TableCell>
                  <TableCell>{dataset.version}</TableCell>
                  <TableCell>{dataset.rowCount?.toLocaleString()}</TableCell>
                  <TableCell>{dataset.columnCount}</TableCell>
                  <TableCell>{dataset.sizeInMB} MB</TableCell>
                  <TableCell>{new Date(dataset.createdAt).toLocaleDateString()}</TableCell>
                  <TableCell>{dataset.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={openUpload} onClose={() => setOpenUpload(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Register New Dataset</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Dataset Name"
              value={uploadData.name}
              onChange={(e) => setUploadData({ ...uploadData, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="S3 URI"
              value={uploadData.s3Uri}
              onChange={(e) => setUploadData({ ...uploadData, s3Uri: e.target.value })}
              fullWidth
              helperText="e.g., s3://bucket/path/to/data.csv"
            />
            <TextField
              label="Description"
              value={uploadData.description}
              onChange={(e) => setUploadData({ ...uploadData, description: e.target.value })}
              fullWidth
              multiline
              rows={3}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUpload(false)}>Cancel</Button>
          <Button onClick={handleUpload} variant="contained">Register</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default DatasetManagement;
