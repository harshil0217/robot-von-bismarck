// Type definitions for the geopolitical simulation

export interface Country {
  name: 'USA' | 'China' | 'Russia' | 'EU';
  flag: string;
  color: string;
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

export interface CountryResponse {
  country: Country['name'];
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

export interface SimulationState {
  isRunning: boolean;
  currentIteration: number;
  maxIterations: number;
  geopoliticalEvent: string;
  countryResponses: CountryResponse[];
  analystResponses: AnalystResponse[];
  currentNorms: CountryNorms;
  initialNorms: CountryNorms;
}

export interface SimulationMessage {
  type: 'user' | 'system' | 'country' | 'analyst';
  content: string;
  timestamp: Date;
  country?: Country['name'];
  iteration?: number;
}

export const COUNTRIES: Country[] = [
  { name: 'USA', flag: '🇺🇸', color: '#1976d2' },
  { name: 'China', flag: '🇨🇳', color: '#d32f2f' },
  { name: 'Russia', flag: '🇷🇺', color: '#388e3c' },
  { name: 'EU', flag: '🇪🇺', color: '#7b1fa2' }
];

export const NORM_DEFINITIONS: Record<keyof NormValues, string> = {
  multilateral_cooperation: "Multilateral Cooperation: -1 (Pure unilateralism) to +1 (Committed multilateralism)",
  sovereignty_as_responsibility: "Sovereignty as Responsibility: -1 (Absolute sovereignty) to +1 (R2P - duty to protect)",
  human_rights_universalism: "Human Rights Universalism: -1 (Rejection of standards) to +1 (Universal commitment)",
  diplomatic_engagement: "Diplomatic Engagement: -1 (Diplomatic isolation) to +1 (Sustained dialogue with rivals)",
  norm_entrepreneurship: "Norm Entrepreneurship: -1 (Resistance to norms) to +1 (Active promotion of norms)",
  peaceful_dispute_resolution: "Peaceful Dispute Resolution: -1 (Military solutions) to +1 (International law commitment)",
  diffuse_reciprocity: "Diffuse Reciprocity: -1 (Transactional only) to +1 (Long-term cooperation)",
  collective_identity_formation: "Collective Identity Formation: -1 (Competitive zero-sum) to +1 (Shared identity)",
  legitimacy_through_consensus: "Legitimacy Through Consensus: -1 (Power-based) to +1 (International consensus)",
  transparency_accountability: "Transparency and Accountability: -1 (Opacity/secrecy) to +1 (Commitment to transparency)"
};