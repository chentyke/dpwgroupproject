import { ClusterPlot } from "@/components/cluster-plot";
import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { postApi } from "@/lib/api";
import { fallbackCluster, fallbackPrediction } from "@/lib/fallback-data";
import { formatCurrency } from "@/lib/format";
import { ClusterResponse, PredictionResponse } from "@/lib/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

const samplePredictionPayload = {
  overall: 87,
  potential: 92,
  age: 21,
  wage_eur: 85000,
  pace: 84,
  shooting: 78,
  dribbling: 91,
  passing: 82,
  defending: 57,
  physic: 64,
};

export default async function AdvancedPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const k = Number(Array.isArray(params.k) ? params.k[0] : params.k ?? "5");

  const [cluster, prediction] = await Promise.all([
    postApi<{ k: number }, ClusterResponse>(
      "/api/cluster",
      { k },
      fallbackCluster,
    ),
    postApi<typeof samplePredictionPayload, PredictionResponse>(
      "/api/predict",
      samplePredictionPayload,
      fallbackPrediction,
    ),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Usage Scenario 4"
        title="Advanced analysis"
        description="This page runs K-Means over latest-season outfield player ability profiles and projects the result to two dimensions with PCA."
        aside="The clustering uses pace, shooting, passing, dribbling, defending, and physic."
      />

      <section className="surface rounded-[1.75rem] p-6">
        <form className="grid gap-4 md:grid-cols-[1fr_160px]">
          <label className="space-y-2">
            <span className="text-sm font-medium">Cluster count (k)</span>
            <input
              name="k"
              type="number"
              min={2}
              max={6}
              defaultValue={k}
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

      <ClusterPlot points={cluster.points} summaries={cluster.summaries} />

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="surface rounded-[1.75rem] p-6">
          <div className="mb-4">
            <p className="text-sm uppercase tracking-[0.2em] muted">Prediction output</p>
            <p className="display-font text-2xl font-semibold">
              {formatCurrency(prediction.estimated_value_eur)}
            </p>
          </div>
          <div className="rounded-[1.5rem] border border-[var(--line)] bg-white/60 p-5">
            <p className="text-sm leading-6 muted">
              {prediction.notes.join(" ")}
            </p>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-[var(--line)] bg-white/60 p-4">
              <p className="text-xs uppercase tracking-[0.16em] muted">R2</p>
              <p className="mt-1 text-lg font-semibold">
                {prediction.r2_score?.toFixed(3) ?? "n/a"}
              </p>
            </div>
            <div className="rounded-2xl border border-[var(--line)] bg-white/60 p-4">
              <p className="text-xs uppercase tracking-[0.16em] muted">MAE</p>
              <p className="mt-1 text-lg font-semibold">
                {prediction.mae_eur != null
                  ? formatCurrency(prediction.mae_eur)
                  : "n/a"}
              </p>
            </div>
            <div className="rounded-2xl border border-[var(--line)] bg-white/60 p-4">
              <p className="text-xs uppercase tracking-[0.16em] muted">Test rows</p>
              <p className="mt-1 text-lg font-semibold">
                {prediction.test_rows ?? 0}
              </p>
            </div>
          </div>
        </div>

        <div className="surface rounded-[1.75rem] p-6">
          <div className="mb-5">
            <p className="text-sm uppercase tracking-[0.2em] muted">Feature weights</p>
            <p className="display-font text-2xl font-semibold">Ridge feature importance</p>
          </div>
          <DataTable
            columns={[
              { key: "feature", label: "Feature", render: (row) => row.feature },
              {
                key: "weight",
                label: "Weight",
                render: (row) => <span className="tag">{row.weight.toFixed(2)}</span>,
              },
            ]}
            rows={prediction.contributions}
          />
        </div>
      </section>
    </div>
  );
}
