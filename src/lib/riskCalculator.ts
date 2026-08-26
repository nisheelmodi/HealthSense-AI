import type { AssessmentData, PredictionResult, RiskLevel } from '../types/assessment';

const clampScore = (value: number): number => Math.min(100, Math.max(0, Math.round(value)));

const parseNumber = (value: string): number => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const parseHeight = (value: string): number => parseNumber(value);
const parseWeight = (value: string): number => parseNumber(value);

const getBmi = (height: string, weight: string): number => {
  const heightInMeters = parseHeight(height) / 100;
  const weightInKg = parseWeight(weight);

  if (heightInMeters <= 0 || weightInKg <= 0) {
    return 0;
  }

  return weightInKg / (heightInMeters * heightInMeters);
};

const getSleepHours = (value: string): number => {
  if (value === 'Less than 5') return 4;
  if (value === '5-6') return 5.5;
  if (value === '7-8') return 7.5;
  if (value === 'More than 8') return 9;
  return 0;
};

const getWaterLevel = (value: string): number => {
  if (value === 'Less than 1L') return 0.8;
  if (value === '1-2L') return 1.5;
  if (value === '2-3L') return 2.5;
  if (value === 'More than 3L') return 3.5;
  return 0;
};

const getExerciseLevel = (value: string): number => {
  if (value === 'None') return 0;
  if (value === '1-2 times/week') return 1.5;
  if (value === '3-4 times/week') return 3.5;
  if (value === '5+ times/week') return 5;
  return 0;
};

const getRiskLevel = (score: number): RiskLevel => {
  if (score >= 70) return 'High Risk';
  if (score >= 40) return 'Moderate Risk';
  return 'Low Risk';
};

export function calculateRisk(data: AssessmentData | null | undefined): PredictionResult {
  if (!data) {
    return {
      score: 0,
      riskLevel: 'Low Risk',
      summary: 'No assessment found. Complete the assessment to view a personal risk analysis.',
      recommendations: ['Take Assessment Again'],
    };
  }

  const { personalInfo, lifestyle, symptoms } = data;
  const age = parseNumber(personalInfo.age);
  const bmi = getBmi(personalInfo.height, personalInfo.weight);
  const sleep = getSleepHours(lifestyle.sleep);
  const water = getWaterLevel(lifestyle.water);
  const exercise = getExerciseLevel(lifestyle.exercise);
  const symptomCount = symptoms.selectedSymptoms.length;

  let score = 0;

  if (age > 50) score += 15;
  else if (age > 35) score += 8;

  if (bmi >= 30) score += 18;
  else if (bmi >= 25) score += 10;

  if (lifestyle.smoking === 'Regularly') score += 16;
  else if (lifestyle.smoking === 'Occasionally') score += 8;

  if (lifestyle.alcohol === 'Regularly') score += 10;
  else if (lifestyle.alcohol === 'Occasionally') score += 5;

  if (sleep < 6) score += 12;
  else if (sleep < 7) score += 6;

  if (water < 2) score += 8;

  if (exercise < 2) score += 10;

  if (symptomCount >= 3) score += 18;
  else if (symptomCount >= 1) score += 8;

  if (personalInfo.gender === 'Other') score += 2;

  score = clampScore(score);
  const riskLevel = getRiskLevel(score);

  const recommendations: string[] = [];

  if (lifestyle.smoking !== 'Never') {
    recommendations.push('Quit Smoking');
  }

  if (sleep < 6) {
    recommendations.push('Improve sleep');
  }

  if (bmi >= 25) {
    recommendations.push('Weight management');
  }

  if (water < 2) {
    recommendations.push('Hydrate regularly');
  }

  if (exercise < 2) {
    recommendations.push('Increase physical activity');
  }

  if (symptomCount >= 1) {
    recommendations.push('Medical consultation');
  }

  if (recommendations.length === 0) {
    recommendations.push('Maintain healthy habits');
  }

  const summary = riskLevel === 'High Risk'
    ? `Based on your age, habits, and symptoms, your current profile suggests ${riskLevel.toLowerCase()} and should be reviewed carefully.`
    : riskLevel === 'Moderate Risk'
      ? `Your health profile suggests ${riskLevel.toLowerCase()} with several areas that may benefit from improvement.`
      : 'Your health profile appears mostly stable, with healthy habits helping maintain a low overall risk.';

  return {
    score,
    riskLevel,
    summary,
    recommendations,
  };
}
