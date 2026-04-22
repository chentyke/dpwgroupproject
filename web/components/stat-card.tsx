type StatCardProps = {
  label: string;
  value: string;
  caption?: string;
};

export function StatCard({ label, value, caption }: StatCardProps) {
  return (
    <article className="surface rounded-[1.5rem] p-5">
      <p className="text-sm uppercase tracking-[0.2em] muted">{label}</p>
      <p className="display-font mt-3 text-3xl font-bold">{value}</p>
      {caption ? <p className="mt-2 text-sm muted">{caption}</p> : null}
    </article>
  );
}

