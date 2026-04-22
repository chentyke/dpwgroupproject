type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description: string;
  aside?: string;
};

export function PageHeader({
  eyebrow,
  title,
  description,
  aside,
}: PageHeaderProps) {
  return (
    <section className="surface-strong rounded-[2rem] p-6 md:p-8">
      <div className="grid gap-6 md:grid-cols-[1.35fr_0.65fr] md:items-end">
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--accent)]">
            {eyebrow}
          </p>
          <h1 className="display-font text-3xl font-bold tracking-tight md:text-5xl">
            {title}
          </h1>
          <p className="max-w-3xl text-base leading-7 muted">{description}</p>
        </div>
        {aside ? (
          <div className="rounded-[1.5rem] border border-[var(--line)] bg-white/60 p-4 text-sm leading-6 text-[var(--ink)]">
            {aside}
          </div>
        ) : null}
      </div>
    </section>
  );
}

