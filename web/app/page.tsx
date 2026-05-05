import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { StatCard } from "@/components/stat-card";
import { fetchApi } from "@/lib/api";
import { fallbackSummary } from "@/lib/fallback-data";
import { formatCompactNumber } from "@/lib/format";

const routes = [
  {
    href: "/explore",
    label: "Explore dataset",
    detail: "Summary, preview rows, cleaning steps, and null hotspots.",
  },
  {
    href: "/value-for-money",
    label: "Value for money",
    detail: "Candidate shortlist, radar profile, and scatter view.",
  },
  {
    href: "/fairness",
    label: "Fairness",
    detail: "League wage spread and nationality heatmap contract.",
  },
  {
    href: "/advanced",
    label: "Advanced analysis",
    detail: "Cluster projection and value prediction scaffold.",
  },
];

const milestones = [
  ["Week 1", "Scaffold + data cleaning", "FastAPI and Next.js both running"],
  ["Week 2", "VfM + fairness", "Real data returned from core analytics routes"],
  ["Week 3", "Advanced models + integration", "All 4 pages wired end to end"],
  ["Week 4", "Polish + report + PPT", "Final delivery materials prepared"],
];

export default async function HomePage() {
  const summary = await fetchApi("/api/dataset/summary", fallbackSummary);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Overview"
        title="An engineering baseline built around the SDS"
        description="This repo now matches the project structure described in the SDS and the April 22 team meeting: FastAPI backend, Next.js frontend, data folders, route contracts, and a usable front-end shell for all four required scenarios."
        aside={`Current data source: ${summary.source}. The backend prefers real CSVs in data/raw and falls back to a committed seed fixture if needed.`}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Rows"
          value={formatCompactNumber(summary.total_rows)}
          caption="Current unified player snapshots"
        />
        <StatCard
          label="Columns"
          value={String(summary.total_columns)}
          caption="Detected from the raw FIFA CSV schema"
        />
        <StatCard
          label="Seasons"
          value={summary.seasons.join(", ")}
          caption="Expected FIFA editions available to the API"
        />
        <StatCard
          label="Views"
          value="4"
          caption="Explore, value, fairness, advanced"
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="surface rounded-[1.75rem] p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] muted">Route map</p>
              <p className="display-font text-2xl font-semibold">Pages ready for the team</p>
            </div>
            <Link href="http://127.0.0.1:8000/docs" className="tag">
              Backend docs
            </Link>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {routes.map((route) => (
              <Link
                key={route.href}
                href={route.href}
                className="rounded-[1.5rem] border border-[var(--line)] bg-white/60 p-5 transition hover:-translate-y-0.5 hover:bg-white/80"
              >
                <p className="display-font text-xl font-semibold">{route.label}</p>
                <p className="mt-2 text-sm leading-6 muted">{route.detail}</p>
              </Link>
            ))}
          </div>
        </div>

        <div className="surface rounded-[1.75rem] p-6">
          <div className="mb-5">
            <p className="text-sm uppercase tracking-[0.2em] muted">Sprint framing</p>
            <p className="display-font text-2xl font-semibold">Milestones from the meeting note</p>
          </div>
          <div className="space-y-4">
            {milestones.map(([week, title, target]) => (
              <article
                key={week}
                className="rounded-[1.5rem] border border-[var(--line)] bg-white/60 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="display-font text-lg font-semibold">{week}</p>
                  <span className="tag">{title}</span>
                </div>
                <p className="mt-3 text-sm leading-6 muted">{target}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
