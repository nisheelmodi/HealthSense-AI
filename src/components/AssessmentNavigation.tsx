'use client';

type AssessmentNavigationProps = {
  isFirstStep: boolean;
  isLastStep: boolean;
  isSubmitting?: boolean;
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
};

export default function AssessmentNavigation({
  isFirstStep,
  isLastStep,
  isSubmitting = false,
  onPrevious,
  onNext,
  onSubmit,
}: AssessmentNavigationProps) {
  return (
    <div className="flex flex-col gap-4 border-t border-white/10 pt-6 sm:flex-row sm:items-center sm:justify-between">
      <button
        type="button"
        onClick={onPrevious}
        disabled={isFirstStep}
        className="inline-flex justify-center rounded-full border border-slate-800 bg-slate-900/90 px-6 py-3 text-sm font-semibold text-slate-200 transition hover:border-cyan-400 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        Previous
      </button>

      {isLastStep ? (
        <button
          type="button"
          onClick={onSubmit}
          disabled={isSubmitting}
          className="inline-flex justify-center rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? 'Analyzing…' : 'Submit Assessment'}
        </button>
      ) : (
        <button
          type="button"
          onClick={onNext}
          className="inline-flex justify-center rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-400"
        >
          Next →
        </button>
      )}
    </div>
  );
}
