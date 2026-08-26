type AssessmentProgressProps = {
  currentStep: number;
  totalSteps: number;
};

export default function AssessmentProgress({ currentStep, totalSteps }: AssessmentProgressProps) {
  const progress = Math.round((currentStep / totalSteps) * 100);

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-6 shadow-xl shadow-slate-950/20 sm:p-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.26em] text-cyan-300">Step {currentStep} of {totalSteps}</p>
          <p className="mt-2 text-2xl font-semibold text-white">Progress</p>
        </div>
        <p className="text-sm font-medium text-slate-300">{progress}% complete</p>
      </div>

      <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-900">
        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-violet-500 transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
    </section>
  );
}
