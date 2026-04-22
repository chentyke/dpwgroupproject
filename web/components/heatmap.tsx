import { HeatmapCell } from "@/lib/types";
import { formatCompactNumber } from "@/lib/format";

type HeatmapProps = {
  cells: HeatmapCell[];
};

function colorFor(value: number, max: number) {
  const ratio = value / Math.max(max, 1);
  return `rgba(18, 107, 78, ${0.14 + ratio * 0.74})`;
}

export function Heatmap({ cells }: HeatmapProps) {
  if (cells.length === 0) {
    return (
      <div className="surface rounded-[1.5rem] p-5">
        <p className="display-font text-xl font-semibold">Nationality pay matrix</p>
        <p className="mt-3 text-sm muted">No heatmap cells are available yet.</p>
      </div>
    );
  }

  const nationalities = Array.from(new Set(cells.map((cell) => cell.nationality_name)));
  const leagues = Array.from(new Set(cells.map((cell) => cell.league_name)));
  const maxValue = Math.max(...cells.map((cell) => cell.average_wage), 1);

  return (
    <div className="surface rounded-[1.5rem] p-5">
      <div className="mb-4">
        <p className="text-sm uppercase tracking-[0.2em] muted">Heatmap</p>
        <p className="display-font text-xl font-semibold">Nationality pay matrix</p>
      </div>

      <div className="overflow-x-auto">
        <div
          className="grid min-w-[640px] gap-2"
          style={{
            gridTemplateColumns: `180px repeat(${leagues.length}, minmax(120px, 1fr))`,
          }}
        >
          <div />
          {leagues.map((league) => (
            <div
              key={league}
              className="px-3 py-2 text-xs font-medium uppercase tracking-[0.16em] muted"
            >
              {league}
            </div>
          ))}

          {nationalities.map((nationality) => (
            <div
              key={nationality}
              className="contents"
            >
              <div className="px-3 py-2 font-medium">{nationality}</div>
              {leagues.map((league) => {
                const cell = cells.find(
                  (item) =>
                    item.nationality_name === nationality && item.league_name === league,
                );
                return (
                  <div
                    key={`${nationality}-${league}`}
                    className="rounded-2xl border border-white/40 px-3 py-4 text-sm text-white"
                    style={{
                      background: cell
                        ? colorFor(cell.average_wage, maxValue)
                        : "rgba(24, 48, 39, 0.06)",
                    }}
                  >
                    {cell ? (
                      <>
                        <div className="font-semibold">
                          {formatCompactNumber(cell.average_wage)}
                        </div>
                        <div className="mt-1 text-xs text-white/85">
                          {cell.sample_size} players
                        </div>
                      </>
                    ) : (
                      <span className="text-xs text-[var(--muted)]">No sample</span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
