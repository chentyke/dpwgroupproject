"use client";

import {
  CartesianGrid,
  Cell,
  Rectangle,
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
import type { HeatmapCell } from "@/lib/types";
import { formatCurrency } from "@/lib/format";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type HeatmapProps = {
  cells: HeatmapCell[];
};

type HeatmapPoint = HeatmapCell & {
  intensity: number;
};

type HeatmapTooltipPayload = {
  payload?: HeatmapPoint;
};

type HeatmapTooltipProps = {
  active?: boolean;
  payload?: HeatmapTooltipPayload[];
};

type HeatmapSquareProps = {
  cx?: number;
  cy?: number;
  fill?: string;
};

const chartConfig = {
  wage: {
    label: "Average wage",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

function compactLeagueName(name: string) {
  return name
    .replace("English Premier League", "Premier League")
    .replace("Spain Primera Division", "LaLiga")
    .replace("Italian Serie A", "Serie A")
    .replace("French Ligue 1", "Ligue 1")
    .replace("English League Championship", "Championship")
    .replace("Spanish Segunda División", "Segunda")
    .replace("USA Major League Soccer", "MLS");
}

function colorFor(value: number, max: number) {
  const ratio = value / Math.max(max, 1);
  return `oklch(0.56 0.16 185 / ${0.16 + ratio * 0.78})`;
}

function HeatmapTooltip({ active, payload }: HeatmapTooltipProps) {
  const point = payload?.[0]?.payload;

  if (!active || !point) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-md">
      <p className="font-medium">{point.nationality_name}</p>
      <div className="mt-1 grid gap-1 text-muted-foreground">
        <p>{point.league_name}</p>
        <p>Average wage: {formatCurrency(point.average_wage)}</p>
        <p>{point.sample_size} players</p>
      </div>
    </div>
  );
}

function HeatmapSquare({ cx = 0, cy = 0, fill }: HeatmapSquareProps) {
  return (
    <Rectangle
      fill={fill}
      height={22}
      radius={4}
      stroke="var(--background)"
      strokeWidth={1}
      width={34}
      x={cx - 17}
      y={cy - 11}
    />
  );
}

export function Heatmap({ cells }: HeatmapProps) {
  if (cells.length === 0) {
    return (
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Nationality pay matrix</CardTitle>
          <CardDescription>Average wage by nationality and league</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No heatmap cells are available yet.
          </p>
        </CardContent>
      </Card>
    );
  }

  const maxValue = Math.max(...cells.map((cell) => cell.average_wage), 1);
  const leagueScores = new Map<string, number>();
  const nationalityScores = new Map<string, number>();

  for (const cell of cells) {
    leagueScores.set(
      cell.league_name,
      (leagueScores.get(cell.league_name) ?? 0) + cell.average_wage,
    );
    nationalityScores.set(
      cell.nationality_name,
      (nationalityScores.get(cell.nationality_name) ?? 0) + cell.average_wage,
    );
  }

  const leagues = Array.from(leagueScores.entries()).sort((a, b) => b[1] - a[1]);
  const nationalities = Array.from(nationalityScores.entries()).sort(
    (a, b) => b[1] - a[1],
  );
  const leagueOrder = new Map(leagues.map(([league], index) => [league, index]));
  const nationalityOrder = new Map(
    nationalities.map(([nationality], index) => [nationality, index]),
  );
  const chartData: HeatmapPoint[] = cells
    .map((cell) => ({
      ...cell,
      intensity: cell.average_wage / maxValue,
    }))
    .sort((left, right) => {
      const nationDelta =
        (nationalityOrder.get(left.nationality_name) ?? 0) -
        (nationalityOrder.get(right.nationality_name) ?? 0);

      if (nationDelta !== 0) {
        return nationDelta;
      }

      return (
        (leagueOrder.get(left.league_name) ?? 0) -
        (leagueOrder.get(right.league_name) ?? 0)
      );
    });
  const chartHeight = Math.max(560, nationalities.length * 34 + 158);
  const topCell = cells.reduce((best, cell) =>
    cell.average_wage > best.average_wage ? cell : best,
  );

  return (
    <Card className="rounded-lg">
      <CardHeader>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle>Nationality pay matrix</CardTitle>
            <CardDescription>Average wage by nationality and league</CardDescription>
          </div>
          <div className="rounded-lg border border-border px-3 py-2 text-sm">
            <p className="font-medium">{formatCurrency(topCell.average_wage)}</p>
            <p className="text-xs text-muted-foreground">
              {topCell.nationality_name} in {compactLeagueName(topCell.league_name)}
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <ChartContainer
            config={chartConfig}
            className="aspect-auto min-w-[900px]"
            style={{ height: chartHeight }}
          >
            <RechartsScatterChart margin={{ top: 12, right: 12, bottom: 94, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                allowDuplicatedCategory={false}
                angle={-34}
                dataKey="league_name"
                domain={leagues.map(([league]) => league)}
                height={104}
                interval={0}
                name="League"
                textAnchor="end"
                tick={{
                  fill: "var(--muted-foreground)",
                  fontSize: 11,
                }}
                tickFormatter={compactLeagueName}
                tickLine={false}
                type="category"
              />
              <YAxis
                allowDuplicatedCategory={false}
                dataKey="nationality_name"
                domain={nationalities.map(([nationality]) => nationality)}
                interval={0}
                name="Nationality"
                tick={{
                  fill: "var(--muted-foreground)",
                  fontSize: 11,
                }}
                tickLine={false}
                type="category"
                width={142}
              />
              <ZAxis range={[1, 1]} />
              <ChartTooltip content={<HeatmapTooltip />} cursor={false} />
              <Scatter data={chartData} name="Average wage" shape={<HeatmapSquare />}>
                {chartData.map((cell) => (
                  <Cell
                    fill={colorFor(cell.average_wage, maxValue)}
                    key={`${cell.nationality_name}-${cell.league_name}`}
                  />
                ))}
              </Scatter>
            </RechartsScatterChart>
          </ChartContainer>
        </div>
      </CardContent>
    </Card>
  );
}
