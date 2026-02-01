import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress
} from '@mui/material';
import { Send as SendIcon, Stop as StopIcon } from '@mui/icons-material';

interface ChatInterfaceProps {
  onStartSimulation: (event: string) => Promise<void>;
  onStopSimulation: () => Promise<void>;
  isRunning: boolean;
  isLoading: boolean;
  connectionError?: string | null;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onStartSimulation,
  onStopSimulation,
  isRunning,
  isLoading,
  connectionError
}) => {
  const [geopoliticalEvent, setGeopoliticalEvent] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!geopoliticalEvent.trim()) {
      setError('Please enter a geopolitical event');
      return;
    }

    try {
      setError(null);
      await onStartSimulation(geopoliticalEvent.trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleStop = async () => {
    try {
      setError(null);
      await onStopSimulation();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while stopping simulation');
    }
  };

  return (
    <Paper elevation={0} sx={{ p: 2, m: 0, backgroundColor: '#1a1a1a', fontFamily: 'Verdana, sans-serif' }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ color: '#ffffff', fontFamily: 'Verdana, sans-serif', fontWeight: 'bold' }}>
        Geopolitical Simulation Interface
      </Typography>

      <Typography variant="body1" paragraph sx={{ color: '#cccccc', fontFamily: 'Verdana, sans-serif' }}>
        Enter a geopolitical event to simulate how different countries would respond and how their ideological norms might evolve through diplomatic interactions.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 1, backgroundColor: '#330000', color: '#ffffff', fontFamily: 'Verdana, sans-serif' }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
        <TextField
          fullWidth
          multiline
          rows={3}
          variant="outlined"
          label="Geopolitical Event"
          placeholder="e.g., A major cyber attack on critical infrastructure is attributed to a state actor..."
          value={geopoliticalEvent}
          onChange={(e) => setGeopoliticalEvent(e.target.value)}
          disabled={isRunning}
          sx={{
            mb: 1,
            '& .MuiInputBase-root': {
              color: '#ffffff',
              fontFamily: 'Verdana, sans-serif',
              backgroundColor: '#0a0a0a',
            },
            '& .MuiInputLabel-root': {
              color: '#cccccc',
              fontFamily: 'Verdana, sans-serif',
            },
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: '#333333',
            },
          }}
        />
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          {!isRunning ? (
            <Button
              type="submit"
              variant="contained"
              color="primary"
              startIcon={isLoading ? <CircularProgress size={20} /> : <SendIcon />}
              disabled={isLoading || !geopoliticalEvent.trim() || !!connectionError}
              title={connectionError ? 'Cannot start: ' + connectionError : ''}
            >
              {isLoading ? 'Starting...' : 'Start Simulation'}
            </Button>
          ) : (
            <Button
              variant="contained"
              color="error"
              startIcon={<StopIcon />}
              onClick={handleStop}
            >
              Stop Simulation
            </Button>
          )}
          
          {isRunning && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={16} sx={{ color: '#ffffff' }} />
              <Typography variant="body2" sx={{ color: '#cccccc', fontFamily: 'Verdana, sans-serif' }}>
                Simulation running...
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Paper>
  );
};