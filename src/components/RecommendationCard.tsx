'use client';

type RecommendationCardProps = {
  title: string;
  description: string;
  icon: string;
};

export default function RecommendationCard({ title, description, icon }: RecommendationCardProps) {
  return (
    <article className="group rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/30 transition-all duration-300 hover:-translate-y-1 hover:border-cyan-400/30 hover:bg-slate-900/90 sm:p-8">
      <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-slate-900/90 text-cyan-400 shadow-lg shadow-cyan-500/10">
        <span className="inline-block" dangerouslySetInnerHTML={{ __html: icon }} />
      </div>
      <h4 className="mt-5 text-xl font-semibold text-white">{title}</h4>
      <p className="mt-3 text-sm leading-7 text-slate-300">{description}</p>
    </article>
  );
}
