export type NavigationSection = 
  | 'overview' 
  | 'wetware' 
  | 'thermodynamics' 
  | 'recursive' 
  | 'safety' 
  | 'audio'
  | 'agent';

export type Language = 'en' | 'gu';

export interface MetricCardData {
  id: string;
  title: string;
  titleGu: string;
  value: string;
  change: string;
  subtext: string;
  subtextGu: string;
  category: 'wetware' | 'energy' | 'velocity' | 'risk';
  trend: 'up' | 'down' | 'neutral';
}

export interface Incident {
  id: string;
  title: string;
  titleGu: string;
  date: string;
  category: 'Deception' | 'Containment Breach' | 'Power Seeking' | 'Cyber Warfare' | 'Emergence';
  severity: 'Critical' | 'High' | 'Elevated' | 'Observed';
  source: string;
  description: string;
  descriptionGu: string;
  technicalLogs: string[];
  mitigation: string;
  sandboxEscapeRisk: number; // 0 - 100
}

export interface AudioTrack {
  id: string;
  title: string;
  titleGu: string;
  speaker: string;
  duration: number; // in seconds
  url?: string;
  summary: string;
  transcript: {
    time: number;
    text: string;
    textGu: string;
  }[];
}

export interface NeuronNode {
  id: number;
  x: number;
  y: number;
  firing: boolean;
  activityLevel: number;
  synapses: number[];
  membranePotential: number; // -70mV to +40mV
}
