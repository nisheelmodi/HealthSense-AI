'use client';

type ResultCardProps = {
  score: number;
  level: string;
};

export default function ResultCard({ score, level }: ResultCardProps) {
  const progressDegree = Math.round((score / 100) * 360);
  const progressStyle = {
    background: `conic-gradient(rgba(34,211,238,0.95) 0deg ${progressDegree}deg, rgba(148,163,184,0.18) ${progressDegree}deg 360deg)`,
  };

  return (
    <article className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-2xl shadow-slate-950/40 sm:p-10">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-300">Risk Score</p>
          <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">AI Health Risk</h2>
          <p className="mt-3 max-w-xl text-sm leading-7 text-slate-300">
            Your assessment has been reviewed against clinical-style risk criteria to deliver a tailored health overview.
          </p>
        </div>
      </div>

      <div className="mt-10 flex flex-col items-center justify-center gap-6">
        <div className="relative flex items-center justify-center rounded-full bg-slate-900/95 p-6 shadow-[0_24px_80px_-40px_rgba(14,165,233,0.55)] sm:p-8" style={progressStyle}>
          <div className="flex h-64 w-64 items-center justify-center rounded-full bg-slate-950/90 shadow-inner shadow-slate-950/50 sm:h-72 sm:w-72">
            <div className="flex h-48 w-48 items-center justify-center rounded-full bg-slate-950 text-center sm:h-56 sm:w-56">
              <div>
                <p className="text-5xl font-semibold text-white sm:text-6xl">{score}%</p>
                <p className="mt-2 text-sm uppercase tracking-[0.35em] text-cyan-300">{level}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/90 px-6 py-5 text-slate-200 shadow-lg shadow-slate-950/10">
            <p className="text-sm text-slate-400">Overall risk</p>
            <p className="mt-3 text-xl font-semibold text-white">{level}</p>
          </div>
          <div className="rounded-3xl border border-slate-800 bg-slate-900/90 px-6 py-5 text-slate-200 shadow-lg shadow-slate-950/10">
            <p className="text-sm text-slate-400">Confidence</p>
            <p className="mt-3 text-xl font-semibold text-white">High</p>
          </div>
        </div>
      </div>
    </article>
  );
}
