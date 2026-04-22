export type ApiEnvelope<T> = {
  code: string;
  message: string;
  data: T;
};

export type ColumnProfile = {
  name: string;
  dtype: string;
  null_count: number;
};

export type DatasetSummary = {
  source: string;
  total_rows: number;
  total_columns: number;
  seasons: number[];
  genders: string[];
  columns: ColumnProfile[];
  preview: Array<Record<string, string | number | null>>;
};

export type CleaningStep = {
  title: string;
  detail: string;
  status: string;
};

export type NullHotspot = {
  column: string;
  null_rate: number;
  note: string;
};

export type CleaningReport = {
  source: string;
  tidy_cache_path: string;
  position_columns: string[];
  steps: CleaningStep[];
  null_hotspots: NullHotspot[];
  notes: string[];
};

export type RadarMetric = {
  label: string;
  value: number;
};

export type VfmCandidate = {
  short_name: string;
  club_name: string;
  league_name: string;
  nationality_name: string;
  value_eur: number;
  wage_eur: number;
  overall: number;
  potential: number;
  player_positions: string;
  vfm_index: number;
  metrics: RadarMetric[];
};

export type ScatterPoint = {
  short_name: string;
  overall: number;
  value_eur: number;
  vfm_index: number;
  highlight: boolean;
};

export type VfmResponse = {
  position: string;
  max_value: number;
  benchmark_name: string;
  benchmark_metrics: RadarMetric[];
  candidates: VfmCandidate[];
  scatter_points: ScatterPoint[];
  notes: string[];
};

export type LeagueDistribution = {
  league_name: string;
  sample_size: number;
  min_wage: number;
  median_wage: number;
  average_wage: number;
  max_wage: number;
};

export type StatisticalTestSummary = {
  method: string;
  statistic: number | null;
  p_value: number | null;
  note: string;
};

export type FairnessByLeagueResponse = {
  overall_min: number;
  overall_max: number;
  distributions: LeagueDistribution[];
  test: StatisticalTestSummary;
  notes: string[];
};

export type HeatmapCell = {
  nationality_name: string;
  league_name: string;
  average_wage: number;
  sample_size: number;
};

export type NationalityHeatmapResponse = {
  cells: HeatmapCell[];
  notes: string[];
};

export type ClusterPoint = {
  short_name: string;
  label: string;
  x: number;
  y: number;
  season: number;
};

export type ClusterSummary = {
  label: string;
  count: number;
  description: string;
};

export type ClusterResponse = {
  k: number;
  points: ClusterPoint[];
  summaries: ClusterSummary[];
  notes: string[];
};

export type FeatureContribution = {
  feature: string;
  weight: number;
};

export type PredictionResponse = {
  estimated_value_eur: number;
  band: string;
  contributions: FeatureContribution[];
  notes: string[];
};

