import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { StyledEngineProvider } from '@mui/material/styles';
import Dashboard from './components/Dashboard';
import TrainingPipeline from './components/TrainingPipeline';
import InferencePipeline from './components/InferencePipeline';
import ModelRegistry from './components/ModelRegistry';
import DatasetManagement from './components/DatasetManagement';
import Monitoring from './components/Monitoring';
import Navigation from './components/Navigation';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/training" element={<TrainingPipeline />} />
          <Route path="/inference" element={<InferencePipeline />} />
          <Route path="/models" element={<ModelRegistry />} />
          <Route path="/datasets" element={<DatasetManagement />} />
          <Route path="/monitoring" element={<Monitoring />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
