"use client";

import {
  CartesianGrid,
  ErrorBar,
  Scatter,
  ScatterChart as RechartsScatterChart,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  type ChartConfig,
} from "@/components/ui/chart";
import type { LeagueDistribution } from "@/lib/types";
import { formatCompactNumber, formatCurrency } from "@/lib/format";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type BoxPlotProps = {
  items: LeagueDistribution[];
};

type WagePoint = LeagueDistribution & {
  value: number;
  errorRange?: [number, number];
  metric: "average" | "median";
};

type WageTooltipPayload = {
  payload?: WagePoint;
};

type WageTooltipProps = {
  active?: boolean;
  payload?: WageTooltipPayload[];
};

const chartConfig = {
  average: {
    label: "Average",
    color: "var(--chart-1)",
  },
  median: {
    label: "Median",
    color: "var(--chart-4)",
  },
} satisfies ChartConfig;

function compactLeagueName(name: string) {
  return name
    .replace("English Premier League", "Premier League")
    .replace("Spain Primera Division", "LaLiga")
    .replace("German 1. Bundesliga", "Bundesliga")
    .replace("Italian Serie A", "Serie A")
    .replace("French Ligue 1", "Ligue 1")
    .replace("English League Championship", "Championship")
    .replace("Campeonato Brasileiro Série A", "Brasileirão")
    .replace("Portuguese Liga ZON SAGRES", "Liga Portugal")
    .replace("Argentina Primera División", "Argentina Primera")
    .replace("Saudi Abdul L. Jameel League", "Saudi Pro League")
    .replace("USA Major League Soccer", "MLS");
}

function WageTooltip({ active, payload }: WageTooltipProps) {
  const point = payload?.[0]?.payload;

  if (!active || !point) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-md">
      <p className="font-medium">{point.league_name}</p>
      <div className="mt-1 grid gap-1 text-muted-foreground">
        <p>{point.sample_size} players</p>
        <p>Min: {formatCurrency(point.min_wage)}</p>
        <p>Median: {formatCurrency(point.median_wage)}</p>
        <p>Average: {formatCurrency(point.average_wage)}</p>
        <p>Max: {formatCurrency(point.max_wage)}</p>
      </div>
    </div>
  );
}

export function BoxPlot({ items }: BoxPlotProps) {
  if (items.length === 0) {
    return (
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>League wage spread</CardTitle>
          <CardDescription>Filtered wage distribution</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No league distribution is available for the current filter.
          </p>
        </CardContent>
      </Card>
    );
  }

  const averageData: WagePoint[] = items.map((item) => ({
    ...item,
    value: item.average_wage,
    errorRange: [
      item.average_wage - item.min_wage,
      item.max_wage - item.average_wage,
    ],
    metric: "average",
  }));
  const medianData: WagePoint[] = items.map((item) => ({
    ...item,
    value: item.median_wage,
    metric: "median",
  }));
  const chartHeight = Math.max(520, items.length * 34 + 118);
  const minSampleSize = Math.min(...items.map((item) => item.sample_size));
  const maxSampleSize = Math.max(...items.map((item) => item.sample_size));

  return (
    <Card className="rounded-lg">
      <CardHeader>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle>League wage spread</CardTitle>
            <CardDescription>
              Min-to-max range with average and median markers
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
            <span className="rounded-md border border-border px-2 py-1">
              Avg marker
            </span>
            <span className="rounded-md border border-border px-2 py-1">
              Median marker
            </span>
            <span className="rounded-md border border-border px-2 py-1">
              Samples {minSampleSize}-{maxSampleSize}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={chartConfig}
          className="aspect-auto w-full"
          style={{ height: chartHeight }}
        >
          <RechartsScatterChart
            layout="vertical"
            margin={{ top: 12, right: 42, bottom: 36, left: 4 }}
          >
            <CartesianGrid horizontal={false} strokeDasharray="3 3" />
            <XAxis
              domain={[0, "dataMax"]}
              dataKey="value"
              name="Wage"
              tickFormatter={formatCompactNumber}
              tickLine={false}
              type="number"
            />
            <YAxis
              allowDuplicatedCategory={false}
              dataKey="league_name"
              interval={0}
              name="League"
              tick={{
                fill: "var(--muted-foreground)",
                fontSize: 11,
              }}
              tickFormatter={compactLeagueName}
              tickLine={false}
              type="category"
              width={172}
            />
            <ZAxis range={[68, 68]} />
            <ChartTooltip
              content={<WageTooltip />}
              cursor={{ strokeDasharray: "3 3" }}
            />
            <Scatter data={averageData} fill="var(--color-average)" name="Average">
              <ErrorBar
                dataKey="errorRange"
                direction="x"
                stroke="var(--color-average)"
                strokeWidth={3}
                width={7}
              />
            </Scatter>
            <Scatter data={medianData} fill="var(--color-median)" name="Median" />
          </RechartsScatterChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
