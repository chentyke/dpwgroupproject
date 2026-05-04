import {
  CleaningReport,
  ClusterResponse,
  DatasetSummary,
  FairnessByLeagueResponse,
  NationalityHeatmapResponse,
  PredictionResponse,
  VfmResponse,
} from "@/lib/types";

export const fallbackSummary: DatasetSummary = {
  source: "sample-fixture",
  total_rows: 12,
  total_columns: 17,
  seasons: [22],
  genders: ["female", "male"],
  columns: [
    { name: "sofifa_id", dtype: "int", null_count: 0 },
    { name: "short_name", dtype: "str", null_count: 0 },
    { name: "player_positions", dtype: "str", null_count: 0 },
    { name: "overall", dtype: "int", null_count: 0 },
    { name: "value_eur", dtype: "int", null_count: 0 },
    { name: "wage_eur", dtype: "int", null_count: 0 },
  ],
  preview: [
    {
      sofifa_id: 158023,
      short_name: "L. Messi",
      player_positions: "RW, ST, CF",
      overall: 93,
      potential: 93,
      value_eur: 78000000,
      wage_eur: 320000,
      league_name: "Ligue 1",
      nationality_name: "Argentina",
    },
  ],
};

export const fallbackCleaningReport: CleaningReport = {
  source: "sample-fixture",
  tidy_cache_path: "data/processed/players_tidy.parquet",
  position_columns: ["st", "cam", "cdm", "rw", "gk"],
  steps: [
    {
      title: "Load yearly snapshots",
      detail: "Read CSV fixtures into a unified player snapshot shape.",
      status: "ready",
    },
    {
      title: "Normalize market fields",
      detail: "Cast value_eur and wage_eur into integers.",
      status: "ready",
    },
  ],
  null_hotspots: [
    {
      column: "league_name",
      null_rate: 0.12,
      note: "Expected to spike in the female archive without club context.",
    },
  ],
  notes: ["Fallback mode is active because the backend is offline."],
};

export const fallbackVfm: VfmResponse = {
  position: "CAM",
  max_value: 120000000,
  benchmark_name: "Bernardo Silva",
  benchmark_metrics: [
    { label: "Pace", value: 77 },
    { label: "Shooting", value: 78 },
    { label: "Passing", value: 87 },
    { label: "Dribbling", value: 92 },
    { label: "Defending", value: 61 },
    { label: "Physic", value: 69 },
  ],
  candidates: [
    {
      short_name: "F. Wirtz",
      club_name: "Bayer 04 Leverkusen",
      league_name: "Bundesliga",
      nationality_name: "Germany",
      value_eur: 83000000,
      wage_eur: 54000,
      overall: 85,
      potential: 92,
      player_positions: "CAM, CM",
      vfm_index: 4.642,
      metrics: [
        { label: "Pace", value: 78 },
        { label: "Shooting", value: 74 },
        { label: "Passing", value: 84 },
        { label: "Dribbling", value: 87 },
        { label: "Defending", value: 52 },
        { label: "Physic", value: 65 },
      ],
    },
    {
      short_name: "J. Musiala",
      club_name: "FC Bayern Munich",
      league_name: "Bundesliga",
      nationality_name: "Germany",
      value_eur: 96000000,
      wage_eur: 85000,
      overall: 86,
      potential: 92,
      player_positions: "CAM, LM",
      vfm_index: 4.62,
      metrics: [
        { label: "Pace", value: 84 },
        { label: "Shooting", value: 78 },
        { label: "Passing", value: 82 },
        { label: "Dribbling", value: 91 },
        { label: "Defending", value: 57 },
        { label: "Physic", value: 64 },
      ],
    },
  ],
  scatter_points: [
    {
      short_name: "F. Wirtz",
      overall: 85,
      value_eur: 83000000,
      vfm_index: 4.642,
      highlight: true,
    },
    {
      short_name: "J. Musiala",
      overall: 86,
      value_eur: 96000000,
      vfm_index: 4.62,
      highlight: true,
    },
    {
      short_name: "Pedri",
      overall: 85,
      value_eur: 90000000,
      vfm_index: 4.601,
      highlight: false,
    },
  ],
  notes: ["Fallback mode is active."],
};

export const fallbackFairness: FairnessByLeagueResponse = {
  overall_min: 80,
  overall_max: 90,
  distributions: [
    {
      league_name: "Premier League",
      sample_size: 3,
      min_wage: 220000,
      median_wage: 230000,
      average_wage: 236666,
      max_wage: 260000,
    },
    {
      league_name: "Bundesliga",
      sample_size: 2,
      min_wage: 54000,
      median_wage: 69500,
      average_wage: 69500,
      max_wage: 85000,
    },
    {
      league_name: "Barclays WSL",
      sample_size: 2,
      min_wage: 7000,
      median_wage: 8500,
      average_wage: 8500,
      max_wage: 10000,
    },
  ],
  test: {
    method: "placeholder-kruskal",
    statistic: 7.24,
    p_value: null,
    note: "Replace the placeholder statistic with a real Kruskal-Wallis test.",
  },
  notes: ["Fallback mode is active."],
};

export const fallbackHeatmap: NationalityHeatmapResponse = {
  cells: [
    {
      nationality_name: "Norway",
      league_name: "Premier League",
      average_wage: 260000,
      sample_size: 1,
    },
    {
      nationality_name: "Norway",
      league_name: "Division 1 Feminine",
      average_wage: 9000,
      sample_size: 1,
    },
    {
      nationality_name: "Germany",
      league_name: "Bundesliga",
      average_wage: 69500,
      sample_size: 2,
    },
  ],
  notes: ["Fallback mode is active."],
};

export const fallbackCluster: ClusterResponse = {
  k: 5,
  points: [
    { short_name: "K. Mbappe", label: "Pacey Attackers", x: 2.44, y: 1.31, season: 22 },
    { short_name: "Ruben Dias", label: "Traditional Defenders", x: -1.92, y: 0.87, season: 22 },
    { short_name: "Pedri", label: "All-Rounders", x: 0.44, y: -0.38, season: 22 },
    { short_name: "F. Wirtz", label: "Lightweight Attackers", x: 1.38, y: -1.1, season: 22 },
  ],
  summaries: [
    {
      label: "Pacey Attackers",
      count: 1,
      description: "pace: 84.0, shooting: 76.0, passing: 70.0, dribbling: 79.0, defending: 38.0, physic: 68.0",
    },
    {
      label: "Traditional Defenders",
      count: 1,
      description: "pace: 62.0, shooting: 45.0, passing: 63.0, dribbling: 61.0, defending: 82.0, physic: 81.0",
    },
  ],
  notes: ["Fallback mode is active."],
};

export const fallbackPrediction: PredictionResponse = {
  estimated_value_eur: 98000000,
  band: "ridge-log-value",
  contributions: [
    { feature: "overall", weight: 0.64 },
    { feature: "potential", weight: 0.48 },
    { feature: "age", weight: 0.31 },
    { feature: "dribbling", weight: 0.18 },
  ],
  r2_score: 0.81,
  mae_eur: 3850000,
  residuals: [
    { predicted_log_value: 16.12, residual: 0.18 },
    { predicted_log_value: 15.88, residual: -0.11 },
  ],
  training_rows: 12800,
  test_rows: 3200,
  notes: ["Fallback mode is active."],
};
