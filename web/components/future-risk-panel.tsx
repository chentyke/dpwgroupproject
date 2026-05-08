import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type {
  FutureModelSummary,
  FutureRiskResponse,
  FutureTimeline,
} from "@/lib/types";

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

export function FutureRiskPanel({
  futureRisk,
}: {
  futureRisk: FutureRiskResponse;
}) {
  return (
    <>
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
    </>
  );
}

export { formatPercent };
