'use client';

type SymptomsStepProps = {
  selectedSymptoms: string[];
  onToggle: (symptom: string) => void;
};

const symptomsList = [
  'Fever',
  'Cough',
  'Headache',
  'Chest Pain',
  'Fatigue',
  'Shortness of Breath',
  'Dizziness',
  'Vomiting',
];

export default function SymptomsStep({ selectedSymptoms, onToggle }: SymptomsStepProps) {
  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-300">
        Choose any symptoms you are currently experiencing. Multiple selections are supported.
      </p>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {symptomsList.map((symptom) => (
          <label
            key={symptom}
            className={`flex cursor-pointer items-center gap-3 rounded-3xl border px-4 py-4 text-slate-100 transition hover:border-cyan-400 ${
              selectedSymptoms.includes(symptom) ? 'border-cyan-400 bg-cyan-500/10' : 'border-slate-800 bg-slate-900/90'
            }`}
          >
            <input
              type="checkbox"
              checked={selectedSymptoms.includes(symptom)}
              onChange={() => onToggle(symptom)}
              className="h-4 w-4 accent-cyan-400"
            />
            <span>{symptom}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
