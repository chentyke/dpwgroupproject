import { LeagueDistribution } from "@/lib/types";
import { formatCompactNumber } from "@/lib/format";

type BoxPlotProps = {
  items: LeagueDistribution[];
};

export function BoxPlot({ items }: BoxPlotProps) {
  if (items.length === 0) {
    return (
      <div className="surface rounded-[1.5rem] p-5">
        <p className="display-font text-xl font-semibold">Box-plot scaffold</p>
        <p className="mt-3 text-sm muted">
          No league distribution is available for the current filter.
        </p>
      </div>
    );
  }

  const maxValue = Math.max(...items.map((item) => item.max_wage), 1);
  const scale = (value: number) => `${(value / maxValue) * 100}%`;

  return (
    <div className="surface rounded-[1.5rem] p-5">
      <div className="mb-4">
        <p className="text-sm uppercase tracking-[0.2em] muted">League wage spread</p>
        <p className="display-font text-xl font-semibold">Box-plot scaffold</p>
      </div>

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.league_name} className="space-y-2">
            <div className="flex items-baseline justify-between gap-3">
              <p className="font-medium">{item.league_name}</p>
              <p className="text-xs muted">{item.sample_size} players</p>
            </div>
            <div className="metric-track relative h-3 rounded-full">
              <div
                className="absolute top-0 h-3 rounded-full bg-[var(--accent)]/25"
                style={{
                  left: scale(item.min_wage),
                  width: `calc(${scale(item.max_wage)} - ${scale(item.min_wage)})`,
                }}
              />
              <span
                className="absolute top-1/2 h-5 w-[2px] -translate-y-1/2 bg-[var(--accent)]"
                style={{ left: scale(item.median_wage) }}
              />
              <span
                className="absolute top-1/2 h-5 w-[2px] -translate-y-1/2 bg-[var(--warning)]"
                style={{ left: scale(item.average_wage) }}
              />
            </div>
            <div className="flex justify-between text-xs muted">
              <span>{formatCompactNumber(item.min_wage)}</span>
              <span>median {formatCompactNumber(item.median_wage)}</span>
              <span>avg {formatCompactNumber(item.average_wage)}</span>
              <span>{formatCompactNumber(item.max_wage)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
