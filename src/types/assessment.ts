export interface PersonalInfo {
  fullName: string;
  age: string;
  gender: 'Male' | 'Female' | 'Other' | '';
  height: string;
  weight: string;
}

export interface LifestyleInfo {
  smoking: string;
  alcohol: string;
  exercise: string;
  sleep: string;
  water: string;
}

export interface SymptomsInfo {
  selectedSymptoms: string[];
}

export interface AssessmentData {
  personalInfo: PersonalInfo;
  lifestyle: LifestyleInfo;
  symptoms: SymptomsInfo;
}

export type RiskLevel = 'Low Risk' | 'Moderate Risk' | 'High Risk';

export interface PredictionResult {
  score: number;
  riskLevel: RiskLevel;
  summary: string;
  recommendations: string[];
  /** Present when the result is a placeholder returned by the backend (not a real ML prediction). */
  isPlaceholder?: boolean;
  factorsConsidered?: string[];
  riskFactors?: string[];
  protectiveFactors?: string[];
}
