import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { StatCard } from "@/components/stat-card";
import { fetchApi } from "@/lib/api";
import { fallbackCleaningReport, fallbackSummary } from "@/lib/fallback-data";
import { formatCompactNumber } from "@/lib/format";

export default async function ExplorePage() {
  const [summary, report] = await Promise.all([
    fetchApi("/api/dataset/summary", fallbackSummary),
    fetchApi(
      "/api/dataset/cleaning-report",
      fallbackCleaningReport,
    ),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Usage Scenario 1"
        title="Data loading and cleaning"
        description="This page is wired to the dataset summary and cleaning-report routes from the SDS. It is where the team can validate the archive, inspect schema shape, and confirm the first-stage ETL contract before deeper analysis begins."
        aside={`Source: ${summary.source}. Preview rows are generated directly from the unified raw-data view.`}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Rows" value={formatCompactNumber(summary.total_rows)} />
        <StatCard label="Columns" value={String(summary.total_columns)} />
        <StatCard label="Seasons" value={summary.seasons.join(", ")} />
        <StatCard label="Cache target" value="Parquet" caption={report.tidy_cache_path} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="surface rounded-[1.75rem] p-6">
          <div className="mb-5">
            <p className="text-sm uppercase tracking-[0.2em] muted">Preview</p>
            <p className="display-font text-2xl font-semibold">Seed rows from the archive</p>
          </div>
          <DataTable
            columns={Object.keys(summary.preview[0] ?? {}).map((key) => ({
              key,
              label: key,
              render: (row: Record<string, unknown>) =>
                String(row[key] ?? "null"),
            }))}
            rows={summary.preview}
          />
        </div>

        <div className="space-y-6">
          <div className="surface rounded-[1.75rem] p-6">
            <div className="mb-4">
              <p className="text-sm uppercase tracking-[0.2em] muted">Pipeline steps</p>
              <p className="display-font text-2xl font-semibold">Cleaning checklist</p>
            </div>
            <div className="space-y-3">
              {report.steps.map((step) => (
                <article
                  key={step.title}
                  className="rounded-[1.5rem] border border-[var(--line)] bg-white/60 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold">{step.title}</p>
                    <span className="tag">{step.status}</span>
                  </div>
                  <p className="mt-2 text-sm leading-6 muted">{step.detail}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="surface rounded-[1.75rem] p-6">
            <div className="mb-4">
              <p className="text-sm uppercase tracking-[0.2em] muted">Null hotspots</p>
              <p className="display-font text-2xl font-semibold">Columns to watch</p>
            </div>
            <div className="space-y-3">
              {report.null_hotspots.map((item) => (
                <article key={item.column} className="space-y-2">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium">{item.column}</p>
                    <p className="text-sm muted">{Math.round(item.null_rate * 100)}%</p>
                  </div>
                  <div className="metric-track h-2 overflow-hidden rounded-full">
                    <div
                      className="h-full rounded-full bg-[var(--warning)]"
                      style={{ width: `${Math.max(item.null_rate * 100, 4)}%` }}
                    />
                  </div>
                  <p className="text-sm leading-6 muted">{item.note}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
