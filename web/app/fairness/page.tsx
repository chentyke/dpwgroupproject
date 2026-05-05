import { BoxPlot } from "@/components/box-plot";
import { Heatmap } from "@/components/heatmap";
import { PageHeader } from "@/components/page-header";
import { StatCard } from "@/components/stat-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { fetchApi } from "@/lib/api";
import { fallbackFairness, fallbackHeatmap } from "@/lib/fallback-data";
import { SearchIcon } from "lucide-react";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function fairnessInterpretation(pValue: number | null) {
  if (pValue == null) {
    return "Statistical significance is not available for the current rating band.";
  }

  if (pValue < 0.05) {
    return "The selected band shows statistically meaningful wage differences across leagues.";
  }

  return "The selected band does not show a statistically meaningful cross-league wage difference.";
}

function significanceTone(pValue: number | null) {
  if (pValue == null) {
    return "border-border bg-muted";
  }

  return pValue < 0.05
    ? "border-chart-4/35 bg-chart-4/10"
    : "border-chart-3/35 bg-chart-3/10";
}

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
  const analysisNotes = fairness.notes.filter(
    (note) => !note.toLowerCase().includes("scipy"),
  );

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Usage Scenario 3"
        title="Salary fairness analysis"
        description="Compare wage distributions for similarly rated players across leagues and nationalities, then surface whether pay differences remain statistically meaningful."
        aside="Kruskal-Wallis H-test summarises cross-league wage differences for the selected overall-rating band."
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Rating band" value={`${overallMin}-${overallMax}`} />
        <StatCard label="Leagues" value={String(fairness.distributions.length)} />
        <StatCard
          label="P-value"
          value={fairness.test.p_value == null ? "n/a" : fairness.test.p_value.toFixed(4)}
        />
        <StatCard label="Heatmap cells" value={String(heatmap.cells.length)} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(300px,0.85fr)_minmax(0,1.15fr)]">
        <Card className="rounded-lg">
          <CardHeader>
            <CardTitle>Fairness filter</CardTitle>
            <CardDescription>Overall-rating band for wage comparison</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="grid gap-4 sm:grid-cols-[1fr_1fr_auto] xl:grid-cols-1">
              <div className="flex flex-col gap-2">
                <label htmlFor="overallMin" className="text-sm font-medium">
                  Overall min
                </label>
                <Input
                  id="overallMin"
                  name="overallMin"
                  type="number"
                  min={1}
                  max={99}
                  defaultValue={overallMin}
                />
              </div>
              <div className="flex flex-col gap-2">
                <label htmlFor="overallMax" className="text-sm font-medium">
                  Overall max
                </label>
                <Input
                  id="overallMax"
                  name="overallMax"
                  type="number"
                  min={1}
                  max={99}
                  defaultValue={overallMax}
                />
              </div>
              <Button type="submit" className="self-end xl:w-full">
                <SearchIcon data-icon="inline-start" />
                Apply
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card className="rounded-lg">
          <CardHeader>
            <CardTitle>{fairness.test.method}</CardTitle>
            <CardDescription>Statistical test summary</CardDescription>
          </CardHeader>
          <CardContent>
            <div className={`rounded-lg border p-5 ${significanceTone(fairness.test.p_value)}`}>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Statistic</p>
                  <p className="display-font mt-2 text-3xl font-bold">
                    {fairness.test.statistic ?? "Pending"}
                  </p>
                </div>
                <Badge variant={fairness.test.p_value != null && fairness.test.p_value < 0.05 ? "secondary" : "outline"}>
                  p = {fairness.test.p_value == null ? "n/a" : fairness.test.p_value.toFixed(4)}
                </Badge>
              </div>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-muted-foreground">
                {fairnessInterpretation(fairness.test.p_value)}
              </p>
            </div>
            {analysisNotes.length ? (
              <div className="mt-4 grid gap-2 md:grid-cols-2">
                {analysisNotes.map((note) => (
                  <div
                    key={note}
                    className="rounded-lg border border-border bg-muted px-3 py-2 text-sm leading-6 text-muted-foreground"
                  >
                    {note}
                  </div>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>
      </section>

      <BoxPlot items={fairness.distributions} />
      <Heatmap cells={heatmap.cells} />
    </div>
  );
}
