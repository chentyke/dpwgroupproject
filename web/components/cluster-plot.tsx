import { ClusterPoint, ClusterSummary } from "@/lib/types";

type ClusterPlotProps = {
  points: ClusterPoint[];
  summaries: ClusterSummary[];
};

const COLORS: Record<string, string> = {
  "Creative Link": "#126b4e",
  "Direct Threat": "#c06128",
  "Control Anchor": "#2456a3",
  "Balanced Engine": "#7e6a2f",
};

export function ClusterPlot({ points, summaries }: ClusterPlotProps) {
  if (points.length === 0) {
    return (
      <div className="surface rounded-[1.5rem] p-5">
        <p className="display-font text-xl font-semibold">Heuristic 2-D map</p>
        <p className="mt-3 text-sm muted">
          No cluster points are available for the current input.
        </p>
      </div>
    );
  }

  const width = 620;
  const height = 280;
  const padding = 36;
  const xValues = points.map((point) => point.x);
  const yValues = points.map((point) => point.y);

  const scaleX = (value: number) =>
    padding +
    ((value - Math.min(...xValues)) / Math.max(Math.max(...xValues) - Math.min(...xValues), 1)) *
      (width - padding * 2);
  const scaleY = (value: number) =>
    height -
    padding -
    ((value - Math.min(...yValues)) / Math.max(Math.max(...yValues) - Math.min(...yValues), 1)) *
      (height - padding * 2);

  return (
    <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
      <div className="surface rounded-[1.5rem] p-5">
        <div className="mb-4">
          <p className="text-sm uppercase tracking-[0.2em] muted">Cluster projection</p>
          <p className="display-font text-xl font-semibold">Heuristic 2-D map</p>
        </div>
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full">
          <line
            x1={padding}
            y1={height - padding}
            x2={width - padding}
            y2={height - padding}
            stroke="rgba(24, 48, 39, 0.2)"
          />
          <line
            x1={padding}
            y1={padding}
            x2={padding}
            y2={height - padding}
            stroke="rgba(24, 48, 39, 0.2)"
          />
          {points.map((point) => (
            <g key={point.short_name}>
              <circle
                cx={scaleX(point.x)}
                cy={scaleY(point.y)}
                r={5}
                fill={COLORS[point.label] ?? "#126b4e"}
              />
            </g>
          ))}
        </svg>
      </div>

      <div className="surface rounded-[1.5rem] p-5">
        <div className="mb-4">
          <p className="text-sm uppercase tracking-[0.2em] muted">Cluster labels</p>
          <p className="display-font text-xl font-semibold">Current summary</p>
        </div>
        <div className="space-y-3">
          {summaries.map((summary) => (
            <article
              key={summary.label}
              className="rounded-[1.25rem] border border-[var(--line)] bg-white/60 p-4"
            >
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold">{summary.label}</p>
                <span className="tag">{summary.count} players</span>
              </div>
              <p className="mt-2 text-sm leading-6 muted">{summary.description}</p>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
