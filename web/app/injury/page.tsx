import { FutureRiskPanel, formatPercent } from "@/components/future-risk-panel";
import { PageHeader } from "@/components/page-header";
import { StatCard } from "@/components/stat-card";
import { fetchApi } from "@/lib/api";
import { fallbackFutureRisk } from "@/lib/fallback-data";

export default async function InjuryPage() {
  const futureRisk = await fetchApi("/api/injury/future-risk", fallbackFutureRisk);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Future Trait Model"
        title="Injury & solid projection"
        description="Predict whether early unlabeled player seasons later convert into Injury Prone or Solid Player labels."
        aside="The models use player-group holdout validation, so each player's seasons stay on one side of the train/test split."
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Players" value={String(futureRisk.player_count)} />
        <StatCard label="Future records" value={String(futureRisk.modeling_records)} />
        <StatCard
          label="Injury lift"
          value={formatPercent(futureRisk.injury_model.high_risk_positive_rate)}
          caption={`Baseline ${formatPercent(futureRisk.injury_model.baseline_positive_rate)}`}
        />
        <StatCard
          label="Solid lift"
          value={formatPercent(futureRisk.solid_model.high_risk_positive_rate)}
          caption={`Baseline ${formatPercent(futureRisk.solid_model.baseline_positive_rate)}`}
        />
      </section>

      <FutureRiskPanel futureRisk={futureRisk} />
    </div>
  );
}
