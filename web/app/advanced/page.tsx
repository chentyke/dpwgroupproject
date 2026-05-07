import { ClusterPlot } from "@/components/cluster-plot";
import { DataTable } from "@/components/data-table";
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
import { Progress } from "@/components/ui/progress";
import { fetchApi, postApi } from "@/lib/api";
import {
  fallbackCluster,
  fallbackFutureRisk,
  fallbackPrediction,
} from "@/lib/fallback-data";
import { formatCurrency } from "@/lib/format";
import type { FutureModelSummary, FutureTimeline } from "@/lib/types";
import { RefreshCwIcon } from "lucide-react";

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

const formatPercent = (value?: number | null) =>
  value == null ? "n/a" : `${(value * 100).toFixed(1)}%`;

const formatMetric = (value?: number | null) =>
  value == null ? "n/a" : value.toFixed(3);

function FutureModelCard({ model }: { model: FutureModelSummary }) {
  const examples = model.examples ?? [];
  const metrics = model.metrics ?? {};
  const topFeatures = model.top_features ?? [];
  const maxImportance = Math.max(
    ...topFeatures.map((item) => item.importance),
    1,
  );

  return (
    <Card className="rounded-lg">
      <CardHeader>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle>{model.label}</CardTitle>
            <CardDescription>{model.target}</CardDescription>
          </div>
          <Badge variant="secondary">
            {formatPercent(model.high_risk_positive_rate)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-border p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
              Baseline
            </p>
            <p className="mt-1 text-lg font-semibold">
              {formatPercent(model.baseline_positive_rate)}
            </p>
          </div>
          <div className="rounded-lg border border-border p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
              Recall
            </p>
            <p className="mt-1 text-lg font-semibold">
              {formatMetric(metrics.recall)}
            </p>
          </div>
          <div className="rounded-lg border border-border p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
              Holdout
            </p>
            <p className="mt-1 text-lg font-semibold">
              {model.test_players}
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-3">
          {topFeatures.slice(0, 5).map((item) => (
            <div key={item.feature} className="flex flex-col gap-2">
              <div className="flex items-center justify-between gap-3">
                <p className="font-medium">{item.feature}</p>
                <Badge variant="outline">{item.importance.toFixed(3)}</Badge>
              </div>
              <Progress value={(item.importance / maxImportance) * 100} />
            </div>
          ))}
        </div>

        <div className="mt-5">
          <DataTable
            columns={[
              {
                key: "player",
                label: "Player",
                render: (row) => row.short_name,
              },
              {
                key: "season",
                label: "Season",
                render: (row) => row.season,
              },
              {
                key: "overall",
                label: "OVR",
                render: (row) => row.overall ?? "n/a",
              },
              {
                key: "probability",
                label: "Prob",
                render: (row) => (
                  <Badge variant="secondary">
                    {formatPercent(row.probability)}
                  </Badge>
                ),
              },
            ]}
            rows={examples.slice(0, 5)}
            getRowKey={(row) => `${model.target}-${row.sofifa_id}-${row.season}`}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function TimelineTable({ timelines }: { timelines: FutureTimeline[] }) {
  const rows = timelines.flatMap((timeline) =>
    timeline.points.map((point) => ({
      ...point,
      player: timeline.short_name,
      sofifa_id: timeline.sofifa_id,
    })),
  );

  return (
    <DataTable
      columns={[
        { key: "player", label: "Player", render: (row) => row.player },
        { key: "season", label: "Season", render: (row) => row.season },
        {
          key: "status",
          label: "Status",
          render: (row) => (
            <Badge variant={row.injury_status === -1 ? "outline" : "secondary"}>
              {row.injury_status}
            </Badge>
          ),
        },
        {
          key: "injury",
          label: "Injury",
          render: (row) => formatPercent(row.injury_probability),
        },
        {
          key: "solid",
          label: "Solid",
          render: (row) => formatPercent(row.solid_probability),
        },
      ]}
      rows={rows}
      getRowKey={(row) => `${row.sofifa_id}-${row.season}`}
    />
  );
}

export default async function AdvancedPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const k = Number(Array.isArray(params.k) ? params.k[0] : params.k ?? "5");

  const [cluster, prediction, futureRisk] = await Promise.all([
    postApi(
      "/api/cluster",
      { k },
      fallbackCluster,
    ),
    postApi(
      "/api/predict",
      samplePredictionPayload,
      fallbackPrediction,
    ),
    fetchApi("/api/injury/future-risk", fallbackFutureRisk),
  ]);
  const maxWeight = Math.max(
    ...prediction.contributions.map((item) => Math.abs(item.weight)),
    1,
  );

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Usage Scenario 4"
        title="Advanced analysis"
        description="Group players into playing-style archetypes with K-Means and summarize the value prediction model for a candidate profile."
        aside="Cluster projection uses PCA coordinates; prediction output reports estimated value and feature contribution weights."
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Clusters" value={String(cluster.k || k)} />
        <StatCard label="Mapped players" value={String(cluster.points.length)} />
        <StatCard label="Estimated value" value={formatCurrency(prediction.estimated_value_eur)} />
        <StatCard
          label="Future records"
          value={String(futureRisk.modeling_records)}
          caption={`${futureRisk.feature_count} features`}
        />
      </section>

      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Cluster control</CardTitle>
          <CardDescription>Choose the number of playing-style groups</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 md:grid-cols-[1fr_160px]">
            <div className="flex flex-col gap-2">
              <label htmlFor="k" className="text-sm font-medium">
                Cluster count (k)
              </label>
              <Input
                id="k"
                name="k"
                type="number"
                min={2}
                max={6}
                defaultValue={k}
              />
            </div>
            <Button type="submit" className="self-end">
              <RefreshCwIcon data-icon="inline-start" />
              Apply
            </Button>
          </form>
        </CardContent>
      </Card>

      <ClusterPlot points={cluster.points} summaries={cluster.summaries} />

      <section className="grid gap-5 xl:grid-cols-[minmax(340px,0.95fr)_minmax(0,1.05fr)]">
        <Card className="rounded-lg">
          <CardHeader>
            <CardTitle>{formatCurrency(prediction.estimated_value_eur)}</CardTitle>
            <CardDescription>Value prediction output</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border border-border bg-muted p-5">
              <p className="text-sm leading-6 text-muted-foreground">
                {prediction.notes.join(" ")}
              </p>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-border p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">R2</p>
                <p className="mt-1 text-lg font-semibold">
                  {prediction.r2_score?.toFixed(3) ?? "n/a"}
                </p>
              </div>
              <div className="rounded-lg border border-border p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">MAE</p>
                <p className="mt-1 text-lg font-semibold">
                  {prediction.mae_eur != null
                    ? formatCurrency(prediction.mae_eur)
                    : "n/a"}
                </p>
              </div>
              <div className="rounded-lg border border-border p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                  Test rows
                </p>
                <p className="mt-1 text-lg font-semibold">
                  {prediction.test_rows ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-lg">
          <CardHeader>
            <CardTitle>Feature weights</CardTitle>
            <CardDescription>Model contribution direction and magnitude</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-5 flex flex-col gap-3">
              {prediction.contributions.slice(0, 6).map((item) => (
                <div key={item.feature} className="flex flex-col gap-2">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium">{item.feature}</p>
                    <Badge variant={item.weight >= 0 ? "secondary" : "outline"}>
                      {item.weight.toFixed(2)}
                    </Badge>
                  </div>
                  <Progress value={(Math.abs(item.weight) / maxWeight) * 100} />
                </div>
              ))}
            </div>
            <DataTable
              columns={[
                { key: "feature", label: "Feature", render: (row) => row.feature },
                {
                  key: "weight",
                  label: "Weight",
                  render: (row) => <Badge variant="secondary">{row.weight.toFixed(2)}</Badge>,
                },
              ]}
              rows={prediction.contributions}
            />
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <FutureModelCard model={futureRisk.injury_model} />
        <FutureModelCard model={futureRisk.solid_model} />
      </section>

      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Validation timelines</CardTitle>
          <CardDescription>
            Held-out early seasons and later observed labels
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TimelineTable timelines={futureRisk.timelines ?? []} />
        </CardContent>
      </Card>
    </div>
  );
}
