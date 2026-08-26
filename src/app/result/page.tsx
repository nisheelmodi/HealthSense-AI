'use client';

import Link from 'next/link';
import { Suspense, useMemo, useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import DisclaimerCard from '../../components/DisclaimerCard';
import RecommendationCard from '../../components/RecommendationCard';
import ResultCard from '../../components/ResultCard';
import SummaryCard from '../../components/SummaryCard';
import { calculateRisk } from '../../lib/riskCalculator';
import type { AssessmentData, PredictionResult } from '../../types/assessment';

const iconDiet = `
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6">
    <path d="M12 2C8.134 2 5 5.134 5 9c0 5.418 7 13 7 13s7-7.582 7-13c0-3.866-3.134-7-7-7Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 11.5c1.77 0 3.204-1.45 3.204-3.237 0-1.786-1.435-3.237-3.204-3.237S8.796 6.477 8.796 8.263C8.796 10.05 10.23 11.5 12 11.5Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
`;

const iconExercise = `
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6">
    <path d="M7 19l-3-3c-.6-.6-.6-1.6 0-2.2L8 9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M17 5l3 3c.6.6.6 1.6 0 2.2L16 15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M5 19h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M9 9l6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  </svg>
`;

const iconSleep = `
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6">
    <path d="M20 15c0 3.866-3.582 7-8 7-1.615 0-3.127-.46-4.391-1.241" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M6.5 8.5a8 8 0 0 1 12.6 7.002" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M9 13.5c.452.817 1.345 1.5 2.5 1.5 1.1 0 2.08-.638 2.5-1.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  </svg>
`;

const iconHydration = `
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6">
    <path d="M12 2s5 5 5 10-2.686 7.146-5 10c-2.314-2.854-5-6-5-10s5-10 5-10Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 12.5c1.38 0 2.5-1.12 2.5-2.5S13.38 7.5 12 7.5 9.5 8.62 9.5 10s1.12 2.5 2.5 2.5Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
`;

function ResultPageContent() {
  const searchParams = useSearchParams();
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [hasLoaded, setHasLoaded] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedResult = sessionStorage.getItem('prediction_result');
      if (storedResult) {
        try {
          const parsed = JSON.parse(storedResult) as PredictionResult;
          setPredictionResult(parsed);
        } catch (e) {
          console.error('Failed to parse prediction result from sessionStorage', e);
        }
      }
      setHasLoaded(true);
    }
  }, []);

  const assessmentData = useMemo<AssessmentData | null>(() => {
    const encodedData = searchParams.get('assessment');

    if (!encodedData) {
      return null;
    }

    try {
      const decodedData = decodeURIComponent(encodedData);
      const parsedData = JSON.parse(decodedData) as Partial<AssessmentData>;

      if (
        parsedData.personalInfo &&
        parsedData.lifestyle &&
        parsedData.symptoms &&
        Array.isArray(parsedData.symptoms.selectedSymptoms)
      ) {
        return parsedData as AssessmentData;
      }

      return null;
    } catch {
      return null;
    }
  }, [searchParams]);

  const result = useMemo(() => {
    if (predictionResult) {
      return predictionResult;
    }
    return calculateRisk(assessmentData);
  }, [predictionResult, assessmentData]);

  const hasAssessment = Boolean(predictionResult || assessmentData);

  const getRecommendationDetails = (recommendation: string) => {
    const lower = recommendation.toLowerCase();
    if (lower.includes('smoking') || lower.includes('quit') || lower.includes('tobacco')) {
      return {
        title: 'Quit Smoking',
        description: recommendation,
        icon: iconDiet,
      };
    }
    if (lower.includes('sleep') || lower.includes('rest') || lower.includes('bedtime')) {
      return {
        title: 'Improve Sleep',
        description: recommendation,
        icon: iconSleep,
      };
    }
    if (lower.includes('weight') || lower.includes('exercise') || lower.includes('activity') || lower.includes('workout')) {
      return {
        title: 'Physical Activity',
        description: recommendation,
        icon: iconExercise,
      };
    }
    if (lower.includes('water') || lower.includes('hydration') || lower.includes('hydrate') || lower.includes('fluid')) {
      return {
        title: 'Hydration',
        description: recommendation,
        icon: iconHydration,
      };
    }
    if (lower.includes('doctor') || lower.includes('medical') || lower.includes('consult') || lower.includes('healthcare')) {
      return {
        title: 'Medical Consultation',
        description: recommendation,
        icon: iconSleep,
      };
    }
    return {
      title: 'Healthy Habits',
      description: recommendation,
      icon: iconDiet,
    };
  };

  if (!hasLoaded) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-cyan-400 border-t-transparent" />
      </div>
    );
  }


  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100 sm:px-10 lg:px-16">
      <div className="mx-auto flex max-w-6xl flex-col gap-10">
        <header className="rounded-[2rem] border border-white/10 bg-slate-950/80 px-6 py-8 shadow-2xl shadow-slate-950/40 sm:px-10">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">AI Health Risk Prediction</p>
          <h1 className="mt-4 text-4xl font-semibold text-white sm:text-5xl">AI Health Risk Prediction</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300 sm:text-lg">
            Your assessment has been analyzed. Below is your health risk overview.
          </p>
        </header>

        {!hasAssessment ? (
          <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-2xl shadow-slate-950/40 sm:p-10">
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-300">No assessment found</p>
            <h2 className="mt-4 text-3xl font-semibold text-white">No assessment data was found.</h2>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
              Start a new assessment to generate a fresh risk profile and personalized recommendations.
            </p>
            <div className="mt-8">
              <Link
                href="/assessment"
                className="inline-flex items-center justify-center rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-400"
              >
                Take Assessment Again
              </Link>
            </div>
          </section>
        ) : (
          <>
            <div className="grid gap-8 xl:grid-cols-[1.2fr_0.8fr]">
              <ResultCard score={result.score} level={result.riskLevel} />
              <SummaryCard summary={result.summary} />
            </div>

            {(result.factorsConsidered?.length || result.riskFactors?.length || result.protectiveFactors?.length) && (
              <section className="grid gap-6 lg:grid-cols-3">
                {result.factorsConsidered?.length ? (
                  <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/40 sm:p-8">
                    <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-300">Factors considered</p>
                    <h3 className="mt-4 text-2xl font-semibold text-white">Factors considered in this assessment</h3>
                    <ul className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
                      {result.factorsConsidered.map((factor) => (
                        <li key={factor} className="flex items-start gap-2">
                          <span className="mt-2 h-1.5 w-1.5 rounded-full bg-cyan-400" />
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {result.riskFactors?.length ? (
                  <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/40 sm:p-8">
                    <p className="text-sm font-semibold uppercase tracking-[0.28em] text-amber-300">Potential risk factors</p>
                    <h3 className="mt-4 text-2xl font-semibold text-white">Potential risk-related factors</h3>
                    <ul className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
                      {result.riskFactors.map((factor) => (
                        <li key={factor} className="flex items-start gap-2">
                          <span className="mt-2 h-1.5 w-1.5 rounded-full bg-amber-400" />
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {result.protectiveFactors?.length ? (
                  <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/40 sm:p-8">
                    <p className="text-sm font-semibold uppercase tracking-[0.28em] text-emerald-300">Protective factors</p>
                    <h3 className="mt-4 text-2xl font-semibold text-white">Protective factors</h3>
                    <ul className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
                      {result.protectiveFactors.map((factor) => (
                        <li key={factor} className="flex items-start gap-2">
                          <span className="mt-2 h-1.5 w-1.5 rounded-full bg-emerald-400" />
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </section>
            )}

            <section className="grid gap-6 lg:grid-cols-2">
              {result.recommendations.map((recommendation) => {
                const details = getRecommendationDetails(recommendation);

                return (
                  <RecommendationCard
                    key={recommendation}
                    title={details.title}
                    description={details.description}
                    icon={details.icon}
                  />
                );
              })}
            </section>
          </>
        )}

        <div className="grid gap-8 xl:grid-cols-[1.4fr_0.6fr]">
          <DisclaimerCard />
          <div className="flex flex-col gap-4 rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-2xl shadow-slate-950/40 sm:p-10">
            <div className="space-y-4">
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-300">Next steps</p>
              <h3 className="text-3xl font-semibold text-white">Explore your options</h3>
              <p className="text-sm leading-7 text-slate-300">
                You can retake the assessment with updated responses or return home to review other AI-powered features.
              </p>
            </div>

            <div className="mt-8 flex flex-col gap-4 sm:flex-row">
              <Link
                href="/assessment"
                className="inline-flex flex-1 items-center justify-center rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-400"
              >
                Take Assessment Again
              </Link>
              <Link
                href="/"
                className="inline-flex flex-1 items-center justify-center rounded-full border border-slate-800 bg-slate-900/90 px-6 py-3 text-sm font-semibold text-slate-200 transition hover:border-cyan-400 hover:text-white"
              >
                Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

export default function ResultPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100 sm:px-10 lg:px-16">
          <div className="mx-auto flex max-w-6xl flex-col gap-10">
            <header className="rounded-[2rem] border border-white/10 bg-slate-950/80 px-6 py-8 shadow-2xl shadow-slate-950/40 sm:px-10">
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-300">AI Health Risk Prediction</p>
              <h1 className="mt-4 text-4xl font-semibold text-white sm:text-5xl">AI Health Risk Prediction</h1>
              <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300 sm:text-lg">
                Loading your assessment results...
              </p>
            </header>
          </div>
        </main>
      }
    >
      <ResultPageContent />
    </Suspense>
  );
}
