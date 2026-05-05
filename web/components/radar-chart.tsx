"use client";

import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart as RechartsRadarChart,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  type ChartConfig,
} from "@/components/ui/chart";
import type { RadarMetric } from "@/lib/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type RadarChartProps = {
  metrics: RadarMetric[];
  label: string;
};

type TooltipPayload = {
  payload?: {
    metric?: string;
    value?: number;
  };
};

type RadarTooltipProps = {
  active?: boolean;
  payload?: TooltipPayload[];
};

const chartConfig = {
  value: {
    label: "Rating",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

function RadarTooltip({ active, payload }: RadarTooltipProps) {
  const item = payload?.[0]?.payload;

  if (!active || !item) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-md">
      <p className="font-medium">{item.metric}</p>
      <p className="text-muted-foreground">{item.value?.toFixed(0)} / 100</p>
    </div>
  );
}

export function RadarChart({ metrics, label }: RadarChartProps) {
  if (metrics.length === 0) {
    return (
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>{label}</CardTitle>
          <CardDescription>Radar profile</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-6 text-muted-foreground">
            No radar metrics are available for the current API response.
          </p>
        </CardContent>
      </Card>
    );
  }

  const chartData = metrics.map((metric) => ({
    metric: metric.label,
    value: metric.value,
  }));

  return (
    <Card className="rounded-lg">
      <CardHeader>
        <CardTitle>{label}</CardTitle>
        <CardDescription>Attribute radar</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square w-full max-w-[360px]"
        >
          <RechartsRadarChart
            data={chartData}
            margin={{ top: 22, right: 52, bottom: 22, left: 52 }}
          >
            <ChartTooltip cursor={false} content={<RadarTooltip />} />
            <PolarGrid gridType="polygon" />
            <PolarAngleAxis
              dataKey="metric"
              tick={{
                fill: "var(--muted-foreground)",
                fontSize: 12,
              }}
            />
            <PolarRadiusAxis
              angle={90}
              axisLine={false}
              domain={[0, 100]}
              tick={false}
            />
            <Radar
              dataKey="value"
              dot
              fill="var(--color-value)"
              fillOpacity={0.24}
              stroke="var(--color-value)"
              strokeWidth={2}
            />
          </RechartsRadarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
