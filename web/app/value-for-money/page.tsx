import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { RadarChart } from "@/components/radar-chart";
import { ScatterPlot } from "@/components/scatter-plot";
import { fetchApi } from "@/lib/api";
import { fallbackVfm } from "@/lib/fallback-data";
import { formatCurrency } from "@/lib/format";
import { VfmResponse } from "@/lib/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

export default async function ValueForMoneyPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const position = Array.isArray(params.position)
    ? params.position[0]
    : params.position ?? "CAM";
  const maxValue = Number(
    Array.isArray(params.maxValue) ? params.maxValue[0] : params.maxValue ?? "120000000",
  );

  const data = await fetchApi<VfmResponse>(
    `/api/vfm?position=${encodeURIComponent(position)}&max_value=${maxValue}`,
    fallbackVfm,
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Usage Scenario 2"
        title="Player value-for-money analysis"
        description="This page locks the API and UX shape for the Moneyball-style analysis proposed in the SDS: a shortlist table, a benchmark radar, and a scatter field that highlights undervalued candidates."
        aside="The current ranking uses the SDS formula overall / log(value_eur + 1)."
      />

      <section className="surface rounded-[1.75rem] p-6">
        <form className="grid gap-4 md:grid-cols-[160px_1fr_160px]">
          <label className="space-y-2">
            <span className="text-sm font-medium">Position</span>
            <input
              name="position"
              defaultValue={position}
              className="w-full rounded-2xl border border-[var(--line)] bg-white/70 px-4 py-3"
            />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium">Max value (EUR)</span>
            <input
              name="maxValue"
              type="number"
              defaultValue={maxValue}
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

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="surface rounded-[1.75rem] p-6">
          <div className="mb-5">
            <p className="text-sm uppercase tracking-[0.2em] muted">Shortlist</p>
            <p className="display-font text-2xl font-semibold">
              Top candidates for {data.position}
            </p>
          </div>
          <DataTable
            columns={[
              {
                key: "player",
                label: "Player",
                render: (row) => (
                  <div>
                    <p className="font-semibold">{row.short_name}</p>
                    <p className="text-xs muted">{row.club_name}</p>
                  </div>
                ),
              },
              { key: "positions", label: "Positions", render: (row) => row.player_positions },
              { key: "overall", label: "Overall", render: (row) => row.overall },
              { key: "value", label: "Value", render: (row) => formatCurrency(row.value_eur) },
              {
                key: "vfm",
                label: "VfM",
                render: (row) => (
                  <span className="tag">{row.vfm_index.toFixed(3)}</span>
                ),
              },
            ]}
            rows={data.candidates}
          />
        </div>

        <RadarChart metrics={data.benchmark_metrics} label={data.benchmark_name} />
      </section>

      <ScatterPlot
        points={data.scatter_points}
        title="Undervalued candidates relative to the filtered market"
      />
    </div>
  );
}
