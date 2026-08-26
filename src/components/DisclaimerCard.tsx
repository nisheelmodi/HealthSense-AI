'use client';

export default function DisclaimerCard() {
  return (
    <article className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-2xl shadow-slate-950/40 sm:p-10">
      <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-300">Medical Disclaimer</p>
      <h3 className="mt-4 text-3xl font-semibold text-white">Important notice</h3>
      <p className="mt-4 text-sm leading-7 text-slate-300 sm:text-base">
        This prediction is generated for educational purposes only and is not a medical diagnosis.
        Always consult a qualified healthcare professional.
      </p>
    </article>
  );
}
