import { BoxPlot } from "@/components/box-plot";
import { Heatmap } from "@/components/heatmap";
import { PageHeader } from "@/components/page-header";
import { fetchApi } from "@/lib/api";
import { fallbackFairness, fallbackHeatmap } from "@/lib/fallback-data";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

export default async function FairnessPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const overallMin = Number(
    Array.isArray(params.overallMin)
      ? params.overallMin[0]
      : params.overallMin ?? "80",
  );
  const overallMax = Number(
    Array.isArray(params.overallMax)
      ? params.overallMax[0]
      : params.overallMax ?? "90",
  );

  const [fairness, heatmap] = await Promise.all([
    fetchApi(
      "/api/fairness/wages-by-league",
      fallbackFairness,
      {
        query: {
          overall_min: overallMin,
          overall_max: overallMax,
        },
      },
    ),
    fetchApi(
      "/api/fairness/nationality-heatmap",
      fallbackHeatmap,
    ),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Usage Scenario 3"
        title="Salary fairness analysis"
        description="This page prepares the league-distribution and nationality-comparison views described in the SDS. The endpoint shape is ready now, while the exact statistical test will be swapped in once the real analysis code lands."
        aside="The meeting note specifically calls out Kruskal-Wallis, Dunn post-hoc testing, and a nationality heatmap for this workstream."
      />

      <section className="surface rounded-[1.75rem] p-6">
        <form className="grid gap-4 md:grid-cols-[1fr_1fr_160px]">
          <label className="space-y-2">
            <span className="text-sm font-medium">Overall min</span>
            <input
              name="overallMin"
              type="number"
              min={1}
              max={99}
              defaultValue={overallMin}
              className="w-full rounded-2xl border border-[var(--line)] bg-white/70 px-4 py-3"
            />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium">Overall max</span>
            <input
              name="overallMax"
              type="number"
              min={1}
              max={99}
              defaultValue={overallMax}
              className="w-full rounded-2xl border border-[var(--line)] bg-white/70 px-4 py-3"
            />
          </label>
          <button
            type="submit"
            className="self-end rounded-2xl bg-[var(--accent)] px-5 py-3 font-medium text-white"
          >
            Refresh
          </button>
        </form>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <BoxPlot items={fairness.distributions} />

        <div className="surface rounded-[1.75rem] p-6">
          <div className="mb-4">
            <p className="text-sm uppercase tracking-[0.2em] muted">Statistical test</p>
            <p className="display-font text-2xl font-semibold">{fairness.test.method}</p>
          </div>
          <div className="rounded-[1.5rem] border border-[var(--line)] bg-white/60 p-5">
            <p className="text-sm muted">Statistic</p>
            <p className="display-font mt-2 text-3xl font-bold">
              {fairness.test.statistic ?? "Pending"}
            </p>
            <p className="mt-4 text-sm leading-6 muted">{fairness.test.note}</p>
          </div>
          <div className="mt-4 space-y-2">
            {fairness.notes.map((note) => (
              <p key={note} className="text-sm leading-6 muted">
                {note}
              </p>
            ))}
          </div>
        </div>
      </section>

      <Heatmap cells={heatmap.cells} />
    </div>
  );
}
