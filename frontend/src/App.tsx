import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, Alert, CircularProgress } from '@mui/material';
import { Layout } from './components/Layout/Layout';
import { ChatInterface } from './components/ChatInterface/ChatInterface';
import { ChatConversation } from './components/ChatInterface/ChatConversation';
import { NormsVisualization } from './components/NormsPanel/NormsVisualization';
import { FinalAnalysis } from './components/Analysis/FinalAnalysis';
import { useSimulation } from './hooks/useSimulation';
import { CountryNorms } from './types/simulation';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#000000',
      paper: '#1a1a1a',
    },
    text: {
      primary: '#ffffff',
      secondary: '#cccccc',
    },
  },
  typography: {
    fontFamily: 'Verdana, sans-serif',
    allVariants: {
      color: '#ffffff',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1a1a1a',
        },
      },
    },
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#000000',
          margin: 0,
          padding: 0,
        },
        '#root': {
          minHeight: '100vh',
          backgroundColor: '#000000',
        },
      },
    },
  },
});

function App() {
  const [initialNorms, setInitialNorms] = useState<CountryNorms>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const simulation = useSimulation(initialNorms);

  useEffect(() => {
    const loadInitialNorms = async () => {
      try {
        const response = await fetch('/initial_norms.json');
        if (!response.ok) {
          throw new Error('Failed to load initial norms');
        }
        const norms = await response.json();
        setInitialNorms(norms);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load initial configuration');
      } finally {
        setLoading(false);
      }
    };

    loadInitialNorms();
  }, []);

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box 
          display="flex" 
          justifyContent="center" 
          alignItems="center" 
          minHeight="100vh"
          flexDirection="column"
          gap={2}
        >
          <CircularProgress size={60} />
          <Box>Loading application...</Box>
        </Box>
      </ThemeProvider>
    );
  }

  if (error) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Layout>
          <Alert severity="error">
            {error}
          </Alert>
        </Layout>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout onReset={simulation.resetSimulation}>
        {/* Connection Error Alert */}
        {simulation.connectionError && (
          <Alert severity="error" sx={{ m: 0, backgroundColor: '#330000', color: '#ffffff', fontFamily: 'Verdana, sans-serif' }}>
            Connection Error: {simulation.connectionError}
            <br />
            <small>Make sure the backend server is running on port 3001</small>
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 0, minHeight: 'calc(100vh - 64px)' }}>
          {/* Main Content Area */}
          <Box sx={{ flex: '1 1 70%' }}>
            {/* Chat Interface */}
            <ChatInterface
              onStartSimulation={simulation.startSimulation}
              onStopSimulation={simulation.stopSimulation}
              isRunning={simulation.isRunning}
              isLoading={simulation.isLoading}
              connectionError={simulation.connectionError}
            />

            {/* Chat Conversation */}
            <ChatConversation
              geopoliticalEvent={simulation.geopoliticalEvent}
              responses={simulation.countryResponses}
              currentIteration={simulation.currentIteration}
            />

            {/* Analysis Section */}
            {simulation.analystResponses.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <FinalAnalysis analystResponses={simulation.analystResponses} />
              </Box>
            )}
          </Box>

          {/* Norms Visualization Sidebar */}
          <Box sx={{ flex: '1 1 30%', minWidth: 350 }}>
            <NormsVisualization
              currentNorms={simulation.currentNorms}
              initialNorms={simulation.initialNorms}
              showComparison={true}
            />
          </Box>
        </Box>
      </Layout>
    </ThemeProvider>
  );
}

export default App;