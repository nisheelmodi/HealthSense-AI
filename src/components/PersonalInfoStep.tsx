'use client';

type PersonalInfoState = {
  fullName: string;
  age: string;
  gender: 'Male' | 'Female' | 'Other' | '';
  height: string;
  weight: string;
};

type PersonalInfoStepProps = {
  values: PersonalInfoState;
  errors: Record<string, string>;
  onChange: (field: keyof PersonalInfoState, value: string) => void;
};

export default function PersonalInfoStep({ values, errors, onChange }: PersonalInfoStepProps) {
  return (
    <div className="space-y-8">
      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="fullName" className="block text-sm font-medium text-slate-200">
            Full Name
          </label>
          <input
            id="fullName"
            type="text"
            value={values.fullName}
            onChange={(event) => onChange('fullName', event.target.value)}
            placeholder="Enter your full name"
            aria-describedby={errors.fullName ? 'fullName-error' : undefined}
            className="w-full rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
          />
          {errors.fullName && (
            <p id="fullName-error" className="text-sm text-rose-400">
              {errors.fullName}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="age" className="block text-sm font-medium text-slate-200">
            Age
          </label>
          <input
            id="age"
            type="number"
            min="1"
            max="120"
            value={values.age}
            onChange={(event) => onChange('age', event.target.value)}
            placeholder="Enter your age"
            aria-describedby={errors.age ? 'age-error' : undefined}
            className="w-full rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
          />
          {errors.age && (
            <p id="age-error" className="text-sm text-rose-400">
              {errors.age}
            </p>
          )}
        </div>
      </div>

      <fieldset className="space-y-3 rounded-[1.75rem] border border-slate-800 bg-slate-900/90 p-5">
        <legend className="text-sm font-medium text-slate-200">Gender</legend>
        <div className="grid gap-3 sm:grid-cols-3">
          {['Male', 'Female', 'Other'].map((option) => (
            <label
              key={option}
              className={`flex cursor-pointer items-center gap-3 rounded-3xl border px-4 py-3 text-slate-100 transition hover:border-cyan-400 ${
                values.gender === option ? 'border-cyan-400 bg-cyan-500/10' : 'border-slate-800 bg-slate-900/90'
              }`}
            >
              <input
                type="radio"
                name="gender"
                value={option}
                checked={values.gender === option}
                onChange={() => onChange('gender', option as PersonalInfoState['gender'])}
                className="h-4 w-4 accent-cyan-400"
              />
              <span>{option}</span>
            </label>
          ))}
        </div>
        {errors.gender && <p className="text-sm text-rose-400">{errors.gender}</p>}
      </fieldset>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="height" className="block text-sm font-medium text-slate-200">
            Height (cm)
          </label>
          <input
            id="height"
            type="number"
            min="50"
            max="300"
            value={values.height}
            onChange={(event) => onChange('height', event.target.value)}
            placeholder="e.g. 170"
            aria-describedby={errors.height ? 'height-error' : undefined}
            className="w-full rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
          />
          {errors.height && (
            <p id="height-error" className="text-sm text-rose-400">
              {errors.height}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="weight" className="block text-sm font-medium text-slate-200">
            Weight (kg)
          </label>
          <input
            id="weight"
            type="number"
            min="10"
            max="500"
            value={values.weight}
            onChange={(event) => onChange('weight', event.target.value)}
            placeholder="e.g. 68"
            aria-describedby={errors.weight ? 'weight-error' : undefined}
            className="w-full rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20"
          />
          {errors.weight && (
            <p id="weight-error" className="text-sm text-rose-400">
              {errors.weight}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
