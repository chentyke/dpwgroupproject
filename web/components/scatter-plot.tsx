"use client";

import {
  CartesianGrid,
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
import type { ScatterPoint } from "@/lib/types";
import { formatCompactNumber, formatCurrency } from "@/lib/format";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type ScatterPlotProps = {
  points: ScatterPoint[];
  title: string;
};

type ScatterTooltipPayload = {
  payload?: ScatterPoint;
};

type ScatterTooltipProps = {
  active?: boolean;
  payload?: ScatterTooltipPayload[];
};

const chartConfig = {
  players: {
    label: "Players",
    color: "var(--chart-1)",
  },
  highlight: {
    label: "Top candidates",
    color: "var(--chart-4)",
  },
} satisfies ChartConfig;

function ScatterTooltip({ active, payload }: ScatterTooltipProps) {
  const point = payload?.[0]?.payload;

  if (!active || !point) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-md">
      <p className="font-medium">{point.short_name}</p>
      <div className="mt-1 grid gap-1 text-muted-foreground">
        <p>Overall: {point.overall}</p>
        <p>Value: {formatCurrency(point.value_eur)}</p>
        <p>VfM: {point.vfm_index.toFixed(3)}</p>
      </div>
    </div>
  );
}

export function ScatterPlot({ points, title }: ScatterPlotProps) {
  if (points.length === 0) {
    return (
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>Overall vs value</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No points available for the current filter.
          </p>
        </CardContent>
      </Card>
    );
  }

  const regularPoints = points.filter((point) => !point.highlight);
  const highlightedPoints = points.filter((point) => point.highlight);

  return (
    <Card className="rounded-lg">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>Overall rating vs market value</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="aspect-auto h-[360px] w-full">
          <RechartsScatterChart margin={{ top: 12, right: 20, bottom: 32, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="overall"
              domain={["dataMin", "dataMax"]}
              name="Overall"
              tickLine={false}
              type="number"
            />
            <YAxis
              dataKey="value_eur"
              name="Value"
              tickFormatter={formatCompactNumber}
              tickLine={false}
              type="number"
              width={72}
            />
            <ZAxis range={[48, 92]} />
            <ChartTooltip
              content={<ScatterTooltip />}
              cursor={{ strokeDasharray: "3 3" }}
            />
            <Scatter
              data={regularPoints}
              fill="var(--color-players)"
              fillOpacity={0.62}
              name="Players"
            />
            <Scatter
              data={highlightedPoints}
              fill="var(--color-highlight)"
              fillOpacity={0.92}
              name="Top candidates"
            />
          </RechartsScatterChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
