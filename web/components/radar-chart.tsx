import { RadarMetric } from "@/lib/types";

type RadarChartProps = {
  metrics: RadarMetric[];
  label: string;
};

export function RadarChart({ metrics, label }: RadarChartProps) {
  const size = 280;
  const center = size / 2;
  const radius = 88;
  const levels = [20, 40, 60, 80, 100];
  const angleStep = (Math.PI * 2) / metrics.length;

  const pointFor = (value: number, index: number) => {
    const angle = -Math.PI / 2 + angleStep * index;
    const scaled = (value / 100) * radius;
    return {
      x: center + Math.cos(angle) * scaled,
      y: center + Math.sin(angle) * scaled,
    };
  };

  const polygon = metrics
    .map((metric, index) => {
      const point = pointFor(metric.value, index);
      return `${point.x},${point.y}`;
    })
    .join(" ");

  return (
    <div className="surface rounded-[1.5rem] p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] muted">Radar profile</p>
          <p className="display-font text-xl font-semibold">{label}</p>
        </div>
        <span className="tag">6-metric snapshot</span>
      </div>

      <svg viewBox={`0 0 ${size} ${size}`} className="mx-auto h-[280px] w-full max-w-[280px]">
        {levels.map((level) => {
          const points = metrics
            .map((_, index) => {
              const point = pointFor(level, index);
              return `${point.x},${point.y}`;
            })
            .join(" ");
          return (
            <polygon
              key={level}
              points={points}
              fill="none"
              stroke="rgba(24, 48, 39, 0.14)"
              strokeWidth="1"
            />
          );
        })}

        {metrics.map((metric, index) => {
          const axisPoint = pointFor(100, index);
          return (
            <g key={metric.label}>
              <line
                x1={center}
                y1={center}
                x2={axisPoint.x}
                y2={axisPoint.y}
                stroke="rgba(24, 48, 39, 0.18)"
              />
              <text
                x={axisPoint.x}
                y={axisPoint.y}
                dx={axisPoint.x > center ? 8 : -8}
                dy={axisPoint.y > center ? 14 : -6}
                textAnchor={axisPoint.x > center ? "start" : "end"}
                className="fill-[var(--muted)] text-[11px]"
              >
                {metric.label}
              </text>
            </g>
          );
        })}

        <polygon
          points={polygon}
          fill="rgba(18, 107, 78, 0.24)"
          stroke="var(--accent)"
          strokeWidth="2"
        />
      </svg>
    </div>
  );
}

