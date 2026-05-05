"use client";

import {
  CartesianGrid,
  Scatter,
  ScatterChart as RechartsScatterChart,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  type ChartConfig,
} from "@/components/ui/chart";
import type { ClusterPoint, ClusterSummary } from "@/lib/types";

type ClusterPlotProps = {
  points: ClusterPoint[];
  summaries: ClusterSummary[];
};

type ClusterSeries = {
  key: string;
  label: string;
  color: string;
  data: ClusterPoint[];
};

type ClusterTooltipPayload = {
  payload?: ClusterPoint;
};

type ClusterTooltipProps = {
  active?: boolean;
  payload?: ClusterTooltipPayload[];
};

const PALETTE = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

function ClusterTooltip({ active, payload }: ClusterTooltipProps) {
  const point = payload?.[0]?.payload;

  if (!active || !point) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-md">
      <p className="font-medium">{point.short_name}</p>
      <div className="mt-1 grid gap-1 text-muted-foreground">
        <p>{point.label}</p>
        <p>
          PC1 {point.x.toFixed(2)}, PC2 {point.y.toFixed(2)}
        </p>
      </div>
    </div>
  );
}

function buildSeries(points: ClusterPoint[], summaries: ClusterSummary[]) {
  const sampleEvery = Math.max(Math.ceil(points.length / 1800), 1);
  const chartPoints = points.filter((_, index) => index % sampleEvery === 0);

  return summaries.map((summary, index) => ({
    key: `cluster${index + 1}`,
    label: summary.label,
    color: PALETTE[index % PALETTE.length],
    data: chartPoints.filter((point) => point.label === summary.label),
  }));
}

function buildChartConfig(series: ClusterSeries[]) {
  return Object.fromEntries(
    series.map((item) => [
      item.key,
      {
        label: item.label,
        color: item.color,
      },
    ]),
  ) satisfies ChartConfig;
}

export function ClusterPlot({ points, summaries }: ClusterPlotProps) {
  if (points.length === 0) {
    return (
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>K-Means PCA map</CardTitle>
          <CardDescription>Playing-style clusters</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No cluster points are available for the current input.
          </p>
        </CardContent>
      </Card>
    );
  }

  const series = buildSeries(points, summaries);
  const chartConfig = buildChartConfig(series);

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.75fr)]">
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>K-Means PCA map</CardTitle>
          <CardDescription>Playing-style clusters in two dimensions</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig} className="aspect-auto h-[420px] w-full">
            <RechartsScatterChart margin={{ top: 12, right: 20, bottom: 32, left: 12 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="x"
                name="PC1"
                tickLine={false}
                type="number"
              />
              <YAxis
                dataKey="y"
                name="PC2"
                tickLine={false}
                type="number"
                width={56}
              />
              <ZAxis range={[34, 34]} />
              <ChartTooltip
                content={<ClusterTooltip />}
                cursor={{ strokeDasharray: "3 3" }}
              />
              {series.map((item) => (
                <Scatter
                  data={item.data}
                  fill={`var(--color-${item.key})`}
                  fillOpacity={0.7}
                  key={item.key}
                  name={item.label}
                />
              ))}
            </RechartsScatterChart>
          </ChartContainer>
        </CardContent>
      </Card>

      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Cluster labels</CardTitle>
          <CardDescription>Centroid summaries</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3">
            {summaries.map((summary) => (
              <article
                key={summary.label}
                className="rounded-lg border border-border bg-background p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold">{summary.label}</p>
                  <Badge variant="secondary">{summary.count} players</Badge>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  {summary.description}
                </p>
              </article>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
