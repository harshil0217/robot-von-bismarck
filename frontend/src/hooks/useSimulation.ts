import { useState, useCallback, useEffect } from 'react';
import {
  SimulationState,
  CountryNorms
} from '../types/simulation';
import { adkService } from '../services/adkService';

const INITIAL_STATE: SimulationState = {
  isRunning: false,
  currentIteration: 0,
  maxIterations: 5,
  geopoliticalEvent: '',
  countryResponses: [],
  analystResponses: [],
  currentNorms: {},
  initialNorms: {}
};

export const useSimulation = (initialNorms: CountryNorms) => {
  const [state, setState] = useState<SimulationState>({
    ...INITIAL_STATE,
    initialNorms,
    currentNorms: { ...initialNorms }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Check backend health on mount
  useEffect(() => {
    let mounted = true;

    const checkHealth = async () => {
      try {
        const health = await adkService.checkHealth();
        if (mounted) {
          if (!health.healthy) {
            setConnectionError(health.message);
          } else {
            setConnectionError(null);
          }
        }
      } catch (error) {
        if (mounted) {
          setConnectionError('Cannot connect to backend server');
        }
      }
    };

    checkHealth();

    return () => {
      mounted = false;
    };
  }, []);

  const startSimulation = useCallback(async (geopoliticalEvent: string) => {
    if (state.isRunning) {
      throw new Error('Simulation is already running');
    }

    setIsLoading(true);
    setConnectionError(null);

    try {
      // Reset state
      setState(prevState => ({
        ...prevState,
        isRunning: true,
        currentIteration: 0,
        geopoliticalEvent,
        countryResponses: [],
        analystResponses: [],
        currentNorms: { ...initialNorms }
      }));

      console.log('Calling backend API...');

      // Call backend API (this will block until simulation completes)
      const responses = await adkService.startSimulation(geopoliticalEvent, initialNorms);

      console.log('Received responses:', responses);

      // Get the latest norms from the last analyst response
      const latestNorms = responses.analystResponses.length > 0
        ? responses.analystResponses[responses.analystResponses.length - 1].norm_updates
        : initialNorms;

      // Get max iteration from responses
      const maxIteration = Math.max(
        ...responses.analystResponses.map((r: any) => r.iteration),
        0
      );

      // Update state with all responses
      setState(prevState => ({
        ...prevState,
        isRunning: false,
        countryResponses: responses.countryResponses || [],
        analystResponses: responses.analystResponses || [],
        currentNorms: latestNorms,
        currentIteration: maxIteration
      }));

    } catch (error) {
      console.error('Simulation error:', error);
      setState(prevState => ({
        ...prevState,
        isRunning: false
      }));
      setConnectionError(error instanceof Error ? error.message : 'Simulation failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [state.isRunning, initialNorms]);

  const stopSimulation = useCallback(async () => {
    // Not supported with GCP backend
    setState(prevState => ({
      ...prevState,
      isRunning: false
    }));
    setIsLoading(false);
  }, []);

  const resetSimulation = useCallback(() => {
    setState({
      ...INITIAL_STATE,
      initialNorms,
      currentNorms: { ...initialNorms }
    });
    setConnectionError(null);
  }, [initialNorms]);

  return {
    ...state,
    isLoading,
    connectionError,
    startSimulation,
    stopSimulation,
    resetSimulation
  };
};
