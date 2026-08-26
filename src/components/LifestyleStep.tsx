'use client';

type LifestyleState = {
  smoking: string;
  alcohol: string;
  exercise: string;
  sleep: string;
  water: string;
};

type LifestyleStepProps = {
  values: LifestyleState;
  errors: Record<string, string>;
  onChange: (field: keyof LifestyleState, value: string) => void;
};

const radioOptions = {
  smoking: ['Never', 'Occasionally', 'Regularly'],
  alcohol: ['None', 'Occasionally', 'Regularly'],
};

const selectOptions = {
  exercise: [
    'None',
    '1-2 times/week',
    '3-4 times/week',
    '5+ times/week',
  ],
  sleep: ['Less than 5', '5-6', '7-8', 'More than 8'],
  water: ['Less than 1L', '1-2L', '2-3L', 'More than 3L'],
};

export default function LifestyleStep({ values, errors, onChange }: LifestyleStepProps) {
  return (
    <div className="space-y-8">
      <div className="grid gap-6 lg:grid-cols-2">
        <fieldset className="space-y-4 rounded-[1.75rem] border border-slate-800 bg-slate-900/90 p-5">
          <legend className="text-sm font-medium text-slate-200">Smoking</legend>
          <div className="grid gap-3">
            {radioOptions.smoking.map((option) => (
              <label
                key={option}
                className={`flex cursor-pointer items-center gap-3 rounded-3xl border px-4 py-3 text-slate-100 transition hover:border-cyan-400 ${
                  values.smoking === option ? 'border-cyan-400 bg-cyan-500/10' : 'border-slate-800 bg-slate-900/90'
                }`}
              >
                <input
                  type="radio"
                  name="smoking"
                  value={option}
                  checked={values.smoking === option}
                  onChange={() => onChange('smoking', option)}
                  className="h-4 w-4 accent-cyan-400"
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
          {errors.smoking && <p className="text-sm text-rose-400">{errors.smoking}</p>}
        </fieldset>

        <fieldset className="space-y-4 rounded-[1.75rem] border border-slate-800 bg-slate-900/90 p-5">
          <legend className="text-sm font-medium text-slate-200">Alcohol</legend>
          <div className="grid gap-3">
            {radioOptions.alcohol.map((option) => (
              <label
                key={option}
                className={`flex cursor-pointer items-center gap-3 rounded-3xl border px-4 py-3 text-slate-100 transition hover:border-cyan-400 ${
                  values.alcohol === option ? 'border-cyan-400 bg-cyan-500/10' : 'border-slate-800 bg-slate-900/90'
                }`}
              >
                <input
                  type="radio"
                  name="alcohol"
                  value={option}
                  checked={values.alcohol === option}
                  onChange={() => onChange('alcohol', option)}
                  className="h-4 w-4 accent-cyan-400"
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
          {errors.alcohol && <p className="text-sm text-rose-400">{errors.alcohol}</p>}
        </fieldset>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-2">
          <label htmlFor="exercise" className="block text-sm font-medium text-slate-200">
            Exercise Frequency
          </label>
          <select
            id="exercise"
            value={values.exercise}
            onChange={(event) => onChange('exercise', event.target.value)}
            className="w-full rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
            aria-describedby={errors.exercise ? 'exercise-error' : undefined}
          >
            <option value="">Choose frequency</option>
            {selectOptions.exercise.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          {errors.exercise && (
            <p id="exercise-error" className="text-sm text-rose-400">
              {errors.exercise}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="sleep" className="block text-sm font-medium text-slate-200">
            Sleep Hours
          </label>
          <select
            id="sleep"
            value={values.sleep}
            onChange={(event) => onChange('sleep', event.target.value)}
            className="w-full rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
            aria-describedby={errors.sleep ? 'sleep-error' : undefined}
          >
            <option value="">Choose sleep hours</option>
            {selectOptions.sleep.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          {errors.sleep && (
            <p id="sleep-error" className="text-sm text-rose-400">
              {errors.sleep}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="water" className="block text-sm font-medium text-slate-200">
            Water Intake
          </label>
          <select
            id="water"
            value={values.water}
            onChange={(event) => onChange('water', event.target.value)}
            className="w-full rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
            aria-describedby={errors.water ? 'water-error' : undefined}
          >
            <option value="">Choose water intake</option>
            {selectOptions.water.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          {errors.water && (
            <p id="water-error" className="text-sm text-rose-400">
              {errors.water}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
