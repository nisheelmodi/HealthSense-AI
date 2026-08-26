'use client';

export default function LoadingScreen() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/95 px-6 py-10 backdrop-blur-xl">
      <div className="w-full max-w-md rounded-[2rem] border border-white/10 bg-slate-900/95 p-10 text-center shadow-2xl shadow-slate-950/40">
        <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full border border-cyan-500/20 bg-slate-950 shadow-xl shadow-cyan-500/15">
          <div className="h-16 w-16 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin" />
        </div>

        <p className="mt-8 text-sm font-semibold uppercase tracking-[0.35em] text-cyan-300">Analyzing your health data...</p>
        <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">Analyzing your health data...</h2>
        <p className="mt-4 text-sm leading-7 text-slate-300">
          Our AI is preparing your health report.
        </p>
      </div>
    </div>
  );
}
