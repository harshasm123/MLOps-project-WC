import React from 'react';
import { Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ModelTraining,
  Psychology,
  Storage,
  Dataset,
  Analytics as Monitoring,
} from '@mui/icons-material';

function Navigation() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          MLOps Platform - Medication Adherence Prediction
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button color="inherit" component={Link} to="/" startIcon={<DashboardIcon />}>
            Dashboard
          </Button>
          <Button color="inherit" component={Link} to="/training" startIcon={<ModelTraining />}>
            Training
          </Button>
          <Button color="inherit" component={Link} to="/inference" startIcon={<Psychology />}>
            Inference
          </Button>
          <Button color="inherit" component={Link} to="/models" startIcon={<Storage />}>
            Models
          </Button>
          <Button color="inherit" component={Link} to="/datasets" startIcon={<Dataset />}>
            Datasets
          </Button>
          <Button color="inherit" component={Link} to="/monitoring" startIcon={<Monitoring />}>
            Monitoring
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navigation;
