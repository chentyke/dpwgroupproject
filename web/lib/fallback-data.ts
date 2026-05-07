import {
  CleaningReport,
  ClusterResponse,
  DatasetSummary,
  FairnessByLeagueResponse,
  FutureRiskResponse,
  NationalityHeatmapResponse,
  PredictionResponse,
  VfmResponse,
} from "@/lib/types";

const fallbackNote =
  "Explicit API fallback mode is active; no analysis result was computed.";

export const fallbackSummary: DatasetSummary = {
  source: "api-fallback-unavailable",
  total_rows: 0,
  total_columns: 0,
  seasons: [],
  genders: [],
  columns: [],
  preview: [],
};

export const fallbackCleaningReport: CleaningReport = {
  source: "api-fallback-unavailable",
  tidy_cache_path: "",
  position_columns: [],
  steps: [],
  null_hotspots: [],
  notes: [fallbackNote],
};

export const fallbackVfm: VfmResponse = {
  position: "",
  max_value: 0,
  benchmark_name: "API unavailable",
  benchmark_metrics: [],
  candidates: [],
  scatter_points: [],
  notes: [fallbackNote],
};

export const fallbackFairness: FairnessByLeagueResponse = {
  overall_min: 0,
  overall_max: 0,
  distributions: [],
  test: {
    method: "unavailable",
    statistic: null,
    p_value: null,
    note: fallbackNote,
  },
  notes: [fallbackNote],
};

export const fallbackHeatmap: NationalityHeatmapResponse = {
  cells: [],
  notes: [fallbackNote],
};

export const fallbackCluster: ClusterResponse = {
  k: 0,
  points: [],
  summaries: [],
  notes: [fallbackNote],
};

export const fallbackPrediction: PredictionResponse = {
  estimated_value_eur: 0,
  band: "unavailable",
  contributions: [],
  r2_score: null,
  mae_eur: null,
  residuals: [],
  training_rows: 0,
  test_rows: 0,
  notes: [fallbackNote],
};

export const fallbackFutureRisk: FutureRiskResponse = {
  source: "api-fallback-unavailable",
  seasons: [],
  player_count: 0,
  total_records: 0,
  modeling_records: 0,
  feature_count: 0,
  features: [],
  status_counts: [],
  injury_model: {
    target: "future_injury",
    label: "Future Injury Model",
    positive_records: 0,
    negative_records: 0,
    baseline_positive_rate: 0,
    training_rows: 0,
    test_rows: 0,
    train_players: 0,
    test_players: 0,
    high_risk_threshold: null,
    high_risk_records: 0,
    high_risk_positive_rate: null,
    metrics: {},
    top_features: [],
    examples: [],
    notes: [fallbackNote],
  },
  solid_model: {
    target: "future_solid",
    label: "Future Solid Model",
    positive_records: 0,
    negative_records: 0,
    baseline_positive_rate: 0,
    training_rows: 0,
    test_rows: 0,
    train_players: 0,
    test_players: 0,
    high_risk_threshold: null,
    high_risk_records: 0,
    high_risk_positive_rate: null,
    metrics: {},
    top_features: [],
    examples: [],
    notes: [fallbackNote],
  },
  timelines: [],
  notes: [fallbackNote],
};
