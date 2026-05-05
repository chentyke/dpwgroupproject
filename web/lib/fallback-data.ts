import {
  CleaningReport,
  ClusterResponse,
  DatasetSummary,
  FairnessByLeagueResponse,
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
