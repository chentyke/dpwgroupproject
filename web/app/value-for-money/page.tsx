import { PageHeader } from "@/components/page-header";
import { ScatterPlot } from "@/components/scatter-plot";
import { StatCard } from "@/components/stat-card";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/components/ui/native-select";
import { VfmCandidatePanel } from "@/components/vfm-candidate-panel";
import { fetchApi } from "@/lib/api";
import { fallbackVfm } from "@/lib/fallback-data";
import { formatCurrency } from "@/lib/format";
import { SearchIcon } from "lucide-react";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

const positions = ["ST", "LW", "RW", "CAM", "CM", "CDM", "CB", "LB", "RB", "GK"];

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

  const data = await fetchApi(
    "/api/vfm",
    fallbackVfm,
    {
      query: {
        position,
        max_value: maxValue,
      },
    },
  );
  const topCandidate = data.candidates[0];

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Usage Scenario 2"
        title="Player value-for-money analysis"
        description="Find undervalued players by combining overall rating, position fit, market value, and benchmark attribute profiles."
        aside="VfM index: overall / log(value_eur + 1). Higher scores indicate stronger performance per Euro of market value."
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Position" value={data.position || position} />
        <StatCard label="Candidates" value={String(data.candidates.length)} />
        <StatCard
          label="Top VfM"
          value={topCandidate ? topCandidate.vfm_index.toFixed(3) : "0.000"}
          caption={topCandidate?.short_name}
        />
        <StatCard label="Budget cap" value={formatCurrency(maxValue)} />
      </section>

      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Shortlist filter</CardTitle>
          <CardDescription>Position and maximum player value</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 md:grid-cols-[180px_1fr_160px]">
            <div className="flex flex-col gap-2">
              <label htmlFor="position" className="text-sm font-medium">
                Position
              </label>
              <NativeSelect id="position" name="position" defaultValue={position}>
                {positions.map((item) => (
                  <NativeSelectOption key={item} value={item}>
                    {item}
                  </NativeSelectOption>
                ))}
              </NativeSelect>
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="maxValue" className="text-sm font-medium">
                Max value (EUR)
              </label>
              <Input
                id="maxValue"
                name="maxValue"
                type="number"
                defaultValue={maxValue}
              />
            </div>
            <Button type="submit" className="self-end">
              <SearchIcon data-icon="inline-start" />
              Apply
            </Button>
          </form>
        </CardContent>
      </Card>

      <VfmCandidatePanel
        benchmarkMetrics={data.benchmark_metrics}
        benchmarkName={data.benchmark_name}
        candidates={data.candidates}
        position={data.position}
      />

      <ScatterPlot
        points={data.scatter_points}
        title="Undervalued candidates relative to the filtered market"
      />
    </div>
  );
}
