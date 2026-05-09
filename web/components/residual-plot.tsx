"use client";

import {
  CartesianGrid,
  ReferenceLine,
  Scatter,
  ScatterChart as RechartsScatterChart,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
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
import type { ResidualPoint } from "@/lib/types";

type ResidualPlotProps = {
  residuals: ResidualPoint[];
};

type ResidualTooltipPayload = {
  payload?: ResidualPoint;
};

type ResidualTooltipProps = {
  active?: boolean;
  payload?: ResidualTooltipPayload[];
};

const chartConfig = {
  residuals: {
    label: "Residuals",
    color: "var(--chart-2)",
  },
  baseline: {
    label: "Zero residual",
    color: "var(--chart-6)",
  },
} satisfies ChartConfig;

function ResidualTooltip({ active, payload }: ResidualTooltipProps) {
  const point = payload?.[0]?.payload;

  if (!active || !point) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-md">
      <p className="font-medium">Residual point</p>
      <div className="mt-1 grid gap-1 text-muted-foreground">
        <p>Predicted log value: {point.predicted_log_value.toFixed(2)}</p>
        <p>Residual: {point.residual.toFixed(2)}</p>
      </div>
    </div>
  );
}

export function ResidualPlot({ residuals }: ResidualPlotProps) {
  if (residuals.length === 0) {
    return (
      <Card className="gap-4 rounded-lg py-5">
        <CardHeader className="px-5">
          <CardTitle>Residual plot</CardTitle>
          <CardDescription>Actual minus predicted log value</CardDescription>
        </CardHeader>
        <CardContent className="px-5">
          <p className="text-sm text-muted-foreground">
            No residual points are available for the current prediction model.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="gap-4 rounded-lg py-5">
      <CardHeader className="px-5">
        <CardTitle>Residual plot</CardTitle>
        <CardDescription>Actual minus predicted log market value</CardDescription>
      </CardHeader>
      <CardContent className="px-5">
        <ChartContainer config={chartConfig} className="aspect-auto h-[330px] w-full">
          <RechartsScatterChart margin={{ top: 12, right: 20, bottom: 32, left: 12 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="predicted_log_value"
              domain={["dataMin", "dataMax"]}
              name="Predicted log value"
              tickFormatter={(value) => Number(value).toFixed(1)}
              tickLine={false}
              type="number"
            />
            <YAxis
              dataKey="residual"
              name="Residual"
              tickFormatter={(value) => Number(value).toFixed(1)}
              tickLine={false}
              type="number"
              width={56}
            />
            <ZAxis range={[36, 64]} />
            <ReferenceLine
              y={0}
              stroke="var(--color-baseline)"
              strokeDasharray="4 4"
            />
            <ChartTooltip
              content={<ResidualTooltip />}
              cursor={{ strokeDasharray: "3 3" }}
            />
            <Scatter
              data={residuals}
              fill="var(--color-residuals)"
              fillOpacity={0.64}
              isAnimationActive={false}
              name="Residuals"
            />
          </RechartsScatterChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
