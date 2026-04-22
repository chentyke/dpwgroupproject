import { ScatterPoint } from "@/lib/types";
import { formatCompactNumber } from "@/lib/format";

type ScatterPlotProps = {
  points: ScatterPoint[];
  title: string;
};

export function ScatterPlot({ points, title }: ScatterPlotProps) {
  if (points.length === 0) {
    return (
      <div className="surface rounded-[1.5rem] p-5">
        <p className="display-font text-xl font-semibold">{title}</p>
        <p className="mt-3 text-sm muted">No points available for the current filter.</p>
      </div>
    );
  }

  const width = 620;
  const height = 280;
  const padding = 38;
  const minOverall = Math.min(...points.map((point) => point.overall));
  const maxOverall = Math.max(...points.map((point) => point.overall));
  const minValue = Math.min(...points.map((point) => point.value_eur));
  const maxValue = Math.max(...points.map((point) => point.value_eur));

  const scaleX = (value: number) =>
    padding +
    ((value - minOverall) / Math.max(maxOverall - minOverall, 1)) * (width - padding * 2);
  const scaleY = (value: number) =>
    height -
    padding -
    ((value - minValue) / Math.max(maxValue - minValue, 1)) * (height - padding * 2);

  return (
    <div className="surface rounded-[1.5rem] p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] muted">Scatter</p>
          <p className="display-font text-xl font-semibold">{title}</p>
        </div>
        <span className="tag">Overall vs value</span>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="w-full">
        <line
          x1={padding}
          y1={height - padding}
          x2={width - padding}
          y2={height - padding}
          stroke="rgba(24, 48, 39, 0.25)"
        />
        <line
          x1={padding}
          y1={padding}
          x2={padding}
          y2={height - padding}
          stroke="rgba(24, 48, 39, 0.25)"
        />

        {points.map((point) => {
          const x = scaleX(point.overall);
          const y = scaleY(point.value_eur);
          return (
            <g key={point.short_name}>
              <circle
                cx={x}
                cy={y}
                r={point.highlight ? 6 : 4}
                fill={point.highlight ? "var(--warning)" : "rgba(18, 107, 78, 0.75)"}
              />
              {point.highlight ? (
                <text x={x + 8} y={y - 8} className="fill-[var(--ink)] text-[11px]">
                  {point.short_name}
                </text>
              ) : null}
            </g>
          );
        })}

        <text
          x={width - padding}
          y={height - 12}
          textAnchor="end"
          className="fill-[var(--muted)] text-[11px]"
        >
          Overall rating
        </text>
        <text x={padding} y={18} className="fill-[var(--muted)] text-[11px]">
          {formatCompactNumber(maxValue)} EUR
        </text>
      </svg>
    </div>
  );
}
