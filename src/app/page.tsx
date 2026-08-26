import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'HealthSense AI',
  description: 'Predict your health risk using Artificial Intelligence.',
};

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.18),_transparent_25%),radial-gradient(circle_at_bottom_right,_rgba(139,92,246,0.16),_transparent_20%)] px-6 py-16 sm:px-10 lg:px-20">
        <div className="mx-auto flex max-w-7xl flex-col gap-16 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <p className="mb-4 inline-flex rounded-full bg-cyan-500/15 px-4 py-1.5 text-sm font-medium text-cyan-200 ring-1 ring-cyan-200/20">
              Premium AI Health Risk Predictor
            </p>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
              HealthSense AI
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-200 sm:text-xl">
              Predict your health risk using Artificial Intelligence.
            </p>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Link
                href="/assessment"
                className="inline-flex items-center justify-center rounded-full bg-cyan-500 px-6 py-3 text-base font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-400"
              >
                Get Started
              </Link>
              <a
                href="#features"
                className="inline-flex items-center justify-center rounded-full border border-slate-700 bg-slate-900/80 px-6 py-3 text-base font-semibold text-slate-100 transition hover:border-slate-500 hover:bg-slate-800/90"
              >
                Learn More
              </a>
            </div>
          </div>

          <div className="rounded-4xl border border-white/10 bg-slate-900/70 p-8 shadow-2xl shadow-slate-950/40 backdrop-blur-md sm:p-10 lg:max-w-lg">
            <div className="mb-6 rounded-3xl bg-gradient-to-r from-cyan-500/20 to-violet-500/20 p-6">
              <p className="text-sm font-medium uppercase tracking-[0.24em] text-cyan-200">Trusted by modern care teams</p>
              <h2 className="mt-4 text-3xl font-semibold text-white">Real-time intelligence for healthier outcomes</h2>
              <p className="mt-4 text-slate-300">
                Access predictive analytics in seconds and make confident choices with data tailored to your health profile.
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300 ring-1 ring-white/10">
                <p className="font-semibold text-white">Cutting-edge AI</p>
                <p className="mt-2">Advanced models trained for clinical relevance.</p>
              </div>
              <div className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300 ring-1 ring-white/10">
                <p className="font-semibold text-white">Secure data</p>
                <p className="mt-2">Built with privacy-first protections.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-slate-950 px-6 py-20 sm:px-10 lg:px-20">
        <div className="mx-auto max-w-7xl">
          <div className="mb-12 text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Capabilities</p>
            <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">
              Designed for precise health risk discovery.
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-slate-300">
              Four powerful features that bring clarity, speed, and confidentiality to your health journey.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            <article className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-8 shadow-xl shadow-slate-950/20 transition hover:-translate-y-1 hover:bg-slate-900/90">
              <h3 className="text-xl font-semibold text-white">AI Health Prediction</h3>
              <p className="mt-4 text-slate-300">Accurate risk scores powered by intelligent analysis.</p>
            </article>

            <article className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-8 shadow-xl shadow-slate-950/20 transition hover:-translate-y-1 hover:bg-slate-900/90">
              <h3 className="text-xl font-semibold text-white">Secure & Private</h3>
              <p className="mt-4 text-slate-300">Your health data remains encrypted and confidential.</p>
            </article>

            <article className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-8 shadow-xl shadow-slate-950/20 transition hover:-translate-y-1 hover:bg-slate-900/90">
              <h3 className="text-xl font-semibold text-white">Personalized Insights</h3>
              <p className="mt-4 text-slate-300">Tailored recommendations that reflect your individual profile.</p>
            </article>

            <article className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-8 shadow-xl shadow-slate-950/20 transition hover:-translate-y-1 hover:bg-slate-900/90">
              <h3 className="text-xl font-semibold text-white">Fast Analysis</h3>
              <p className="mt-4 text-slate-300">Receive results quickly with optimized performance.</p>
            </article>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="bg-slate-950 px-6 pb-20 sm:px-10 lg:px-20">
        <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">About HealthSense AI</p>
            <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">
              Smart healthcare guidance with a premium, human-centered experience.
            </h2>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300">
              HealthSense AI combines modern machine learning with secure health analytics to offer a clear path toward better wellbeing. Crafted for professionals and individuals who want confident decisions supported by intelligent risk predictions.
            </p>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-gradient-to-tr from-cyan-500/10 via-slate-900/70 to-violet-500/10 p-8 shadow-2xl shadow-slate-950/40">
            <div className="rounded-[1.75rem] bg-slate-950/90 p-8">
              <p className="text-lg font-semibold text-white">Why it matters</p>
              <p className="mt-4 text-slate-300 leading-7">
                In a world where personalized health insight matters more than ever, HealthSense AI gives meaningful predictions without compromising trust or design clarity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="bg-slate-950 px-6 py-8 text-center text-slate-500 sm:px-10 lg:px-20">
        <p>© 2026 HealthSense AI</p>
      </footer>
    </main>
  );
}
