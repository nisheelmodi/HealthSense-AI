'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import AssessmentProgress from './AssessmentProgress';
import AssessmentNavigation from './AssessmentNavigation';
import LifestyleStep from './LifestyleStep';
import LoadingScreen from './LoadingScreen';
import PersonalInfoStep from './PersonalInfoStep';
import SymptomsStep from './SymptomsStep';
import type { AssessmentData } from '../types/assessment';

type PersonalInfoState = {
  fullName: string;
  age: string;
  gender: 'Male' | 'Female' | 'Other' | '';
  height: string;
  weight: string;
};

type LifestyleState = {
  smoking: string;
  alcohol: string;
  exercise: string;
  sleep: string;
  water: string;
};

type StepErrors = {
  [key: string]: string;
};

const stepDetails = [
  {
    title: 'Personal Information',
    description: 'Enter your basic health details to begin the assessment.',
  },
  {
    title: 'Lifestyle',
    description: 'Tell us about your daily habits for a more informed review.',
  },
  {
    title: 'Symptoms',
    description: 'Select any symptoms you are currently experiencing.',
  },
];

export default function AssessmentWizard() {
  const [currentStep, setCurrentStep] = useState(1);
  const [personalInfo, setPersonalInfo] = useState<PersonalInfoState>({
    fullName: '',
    age: '',
    gender: '',
    height: '',
    weight: '',
  });

  const [lifestyle, setLifestyle] = useState<LifestyleState>({
    smoking: '',
    alcohol: '',
    exercise: '',
    sleep: '',
    water: '',
  });

  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [errors, setErrors] = useState<StepErrors>({});
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  const activeStep = stepDetails[currentStep - 1];

  const validateStep = (step: number) => {
    const nextErrors: StepErrors = {};

    if (step === 1) {
      if (!personalInfo.fullName.trim()) {
        nextErrors.fullName = 'Full name is required.';
      }
      const ageNum = Number(personalInfo.age);
      if (!personalInfo.age.trim() || isNaN(ageNum) || ageNum < 1 || ageNum > 120) {
        nextErrors.age = 'Please enter a valid age between 1 and 120.';
      }
      if (!personalInfo.gender) {
        nextErrors.gender = 'Please select your gender.';
      }
      const heightNum = Number(personalInfo.height);
      if (!personalInfo.height.trim() || isNaN(heightNum) || heightNum < 50 || heightNum > 300) {
        nextErrors.height = 'Please enter a valid height between 50 and 300 cm.';
      }
      const weightNum = Number(personalInfo.weight);
      if (!personalInfo.weight.trim() || isNaN(weightNum) || weightNum < 10 || weightNum > 500) {
        nextErrors.weight = 'Please enter a valid weight between 10 and 500 kg.';
      }
    }

    if (step === 2) {
      if (!lifestyle.smoking) {
        nextErrors.smoking = 'Please select your smoking habits.';
      }
      if (!lifestyle.alcohol) {
        nextErrors.alcohol = 'Please select your alcohol habits.';
      }
      if (!lifestyle.exercise) {
        nextErrors.exercise = 'Please select your exercise frequency.';
      }
      if (!lifestyle.sleep) {
        nextErrors.sleep = 'Please select your average sleep hours.';
      }
      if (!lifestyle.water) {
        nextErrors.water = 'Please select your daily water intake.';
      }
    }

    return nextErrors;
  };

  const handleNext = () => {
    const nextErrors = validateStep(currentStep);
    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    setErrors({});
    setCurrentStep((prev) => Math.min(prev + 1, stepDetails.length));
  };

  const handlePrevious = () => {
    setErrors({});
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async () => {
    // Prevent duplicate submissions
    if (isLoading) return;

    setErrors({});
    setSubmissionError(null);
    setIsLoading(true);

    const assessmentData: AssessmentData = {
      personalInfo,
      lifestyle,
      symptoms: { selectedSymptoms: symptoms },
    };

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assessmentData),
      });

      if (!response.ok) {
        // Attempt to read the error body for user-friendly messages
        let friendlyMessage = 'We couldn\'t complete your assessment. Please check your information and try again.';

        try {
          const errorBody = await response.json();

          if (response.status === 422) {
            // Backend validation_errors is { detail: { validation_errors: string[] } }
            // or { detail: string } for parse errors
            const detail = errorBody?.detail;
            if (detail && typeof detail === 'object' && Array.isArray(detail.validation_errors)) {
              friendlyMessage = detail.validation_errors.join(' ');
            } else if (typeof detail === 'string') {
              // Generic parse error from backend — show a safe message
              friendlyMessage = 'Some values you entered couldn\'t be processed. Please check your age, height, and weight.';
            }
          } else if (response.status === 503) {
            friendlyMessage = 'The prediction service is temporarily unavailable. Please try again in a moment.';
          }
        } catch {
          // JSON parse failed — keep the default friendly message
        }

        setIsLoading(false);
        setSubmissionError(friendlyMessage);
        return;
      }

      let resultData;
      try {
        resultData = await response.json();
      } catch {
        setIsLoading(false);
        setSubmissionError('The server returned an unexpected response. Please try again.');
        return;
      }

      // Store prediction result in sessionStorage
      sessionStorage.setItem('prediction_result', JSON.stringify(resultData));
      sessionStorage.setItem('assessment_data', JSON.stringify(assessmentData));

      // 1-second delay to keep the premium loading screen visible
      setTimeout(() => {
        router.push('/result');
      }, 1000);
    } catch {
      // Network failure or backend unreachable
      setIsLoading(false);
      setSubmissionError(
        'Unable to reach the assessment service. Please check your connection and try again.'
      );
    }
  };

  const updatePersonalInfo = (field: keyof PersonalInfoState, value: string) => {
    setPersonalInfo((prev) => ({ ...prev, [field]: value }));
  };

  const updateLifestyle = (field: keyof LifestyleState, value: string) => {
    setLifestyle((prev) => ({ ...prev, [field]: value }));
  };

  const toggleSymptom = (symptom: string) => {
    setSymptoms((prev) =>
      prev.includes(symptom) ? prev.filter((item) => item !== symptom) : [...prev, symptom]
    );
  };

  return (
    <>
      {isLoading && <LoadingScreen />}

      <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/40 sm:p-10">
        <div className="mb-8">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Health Assessment</p>
              <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">{activeStep.title}</h2>
            </div>
            <p className="text-sm font-medium text-slate-300">Step {currentStep} of {stepDetails.length}</p>
          </div>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300 sm:text-lg">
            {activeStep.description}
          </p>
        </div>

        <AssessmentProgress currentStep={currentStep} totalSteps={stepDetails.length} />

        {submissionError && (
          <div className="mt-8 rounded-3xl border border-rose-500/20 bg-rose-500/10 p-5 text-sm text-rose-400">
            <p className="font-semibold text-base text-rose-300">Prediction Service Error</p>
            <p className="mt-2 text-slate-300">{submissionError}</p>
            <button
              type="button"
              onClick={() => setSubmissionError(null)}
              className="mt-4 rounded-full border border-rose-500/30 bg-rose-500/10 px-4 py-2 text-xs font-semibold text-rose-300 hover:bg-rose-500/25 transition"
            >
              Dismiss Error
            </button>
          </div>
        )}

        <form className="mt-8 space-y-8" onSubmit={(event) => event.preventDefault()}>
          {currentStep === 1 && (
            <PersonalInfoStep

              values={personalInfo}
              errors={errors}
              onChange={updatePersonalInfo}
            />
          )}

          {currentStep === 2 && (
            <LifestyleStep values={lifestyle} errors={errors} onChange={updateLifestyle} />
          )}

          {currentStep === 3 && (
            <SymptomsStep selectedSymptoms={symptoms} onToggle={toggleSymptom} />
          )}

          <AssessmentNavigation
            isFirstStep={currentStep === 1}
            isLastStep={currentStep === stepDetails.length}
            isSubmitting={isLoading}
            onPrevious={handlePrevious}
            onNext={handleNext}
            onSubmit={handleSubmit}
          />
        </form>
      </section>
    </>
  );
}
