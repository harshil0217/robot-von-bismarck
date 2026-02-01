// Type definitions for backend server

export interface CountryResponse {
  country: 'USA' | 'China' | 'Russia' | 'EU';
  message: string;
  timestamp: Date;
  iteration: number;
}

export interface AnalystResponse {
  iteration: number;
  analysis: string;
  norm_updates: CountryNorms;
  reasoning: {
    [key: string]: string;
  };
}

export interface NormValues {
  multilateral_cooperation: number;
  sovereignty_as_responsibility: number;
  human_rights_universalism: number;
  diplomatic_engagement: number;
  norm_entrepreneurship: number;
  peaceful_dispute_resolution: number;
  diffuse_reciprocity: number;
  collective_identity_formation: number;
  legitimacy_through_consensus: number;
  transparency_accountability: number;
}

export interface CountryNorms {
  [key: string]: NormValues;
}

export interface WebSocketMessage {
  type: 'start' | 'stop' | 'country_response' | 'analyst_response' | 'error' | 'complete' | 'status';
  data?: any;
  error?: string;
}

export interface StartSimulationRequest {
  type: 'start';
  event: string;
  initialNorms: CountryNorms;
}
