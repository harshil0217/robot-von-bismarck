// Service for communicating with GCP Reasoning Engine via backend proxy

import { CountryNorms } from '../types/simulation';

export interface AdkServiceConfig {
  baseUrl?: string;
}

export class AdkService {
  private baseUrl: string;

  constructor(config: AdkServiceConfig = {}) {
    this.baseUrl = config.baseUrl || 'http://localhost:3001';
  }

  /**
   * Check backend and GCP health
   */
  async checkHealth(): Promise<{ healthy: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`);

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      return {
        healthy: false,
        message: error instanceof Error ? error.message : 'Backend not reachable'
      };
    }
  }

  /**
   * Start simulation
   * Makes HTTP POST to backend, which calls GCP Reasoning Engine
   */
  async startSimulation(event: string, initialNorms: CountryNorms): Promise<any> {
    console.log('Starting simulation:', event);

    const response = await fetch(`${this.baseUrl}/api/simulate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        event,
        initialNorms
      })
    });

    if (!response.ok) {
      let errorMessage = 'Failed to start simulation';

      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch (e) {
        errorMessage = await response.text();
      }

      throw new Error(errorMessage);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || 'Simulation failed');
    }

    console.log('Simulation complete:', result.responses);
    return result.responses;
  }

  /**
   * Legacy method - deprecated but kept for compatibility
   */
  async stopSimulation(): Promise<void> {
    console.warn('stopSimulation is not supported with GCP backend');
  }

  /**
   * Legacy method - deprecated but kept for compatibility
   */
  isSimulationRunning(): boolean {
    return false;
  }
}

// Export singleton instance
export const adkService = new AdkService();
