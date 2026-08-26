import Link from 'next/link';
import AssessmentWizard from '../../components/AssessmentWizard';

export const metadata = {
  title: 'Health Assessment | HealthSense AI',
  description: 'Start your HealthSense AI assessment with step one of the health risk predictor.',
};

export default function AssessmentPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100 sm:px-10 lg:px-16">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-cyan-300 transition"
          >
            ← Back to Home
          </Link>
        </div>

        <header className="rounded-[2rem] border border-white/10 bg-slate-950/80 px-6 py-8 shadow-2xl shadow-slate-950/40 sm:px-10">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Health Assessment</p>
          <h1 className="mt-4 text-4xl font-semibold text-white sm:text-5xl">Health Assessment</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300 sm:text-lg">
            Complete the following assessment to receive your AI-powered health risk analysis.
          </p>
        </header>

        <AssessmentWizard />
      </div>
    </main>
  );
}

