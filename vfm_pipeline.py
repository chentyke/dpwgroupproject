from pathlib import Path
import re, json, math, zipfile, textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'services' / 'data_analysis' / 'vfm'
FIG = OUT / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

CSV_FILES = sorted(ROOT.glob('players_*.csv')) + sorted(ROOT.glob('female_players_*.csv'))

NUMERIC_COLS = [
    'overall','potential','value_eur','wage_eur','age','league_level',
    'pace','shooting','passing','dribbling','defending','physic',
    'goalkeeping_diving','goalkeeping_handling','goalkeeping_kicking',
    'goalkeeping_positioning','goalkeeping_reflexes','goalkeeping_speed'
]
META_COLS = [
    'sofifa_id','short_name','long_name','player_positions','club_name','league_name',
    'nationality_name','preferred_foot','work_rate','player_url'
]

DEF_POS = {'CB','LCB','RCB','LB','RB','LWB','RWB'}
MID_POS = {'CDM','CM','CAM','LM','RM','LDM','RDM','LCM','RCM','LAM','RAM'}
ATT_POS = {'ST','CF','LW','RW','LF','RF','LS','RS'}
GK_POS = {'GK'}


def parse_version(path: Path) -> int:
    m = re.search(r'_(\d{2})\.csv$', path.name)
    if not m:
        raise ValueError(f'Cannot parse FIFA version from {path.name}')
    return int(m.group(1))


def load_all():
    frames = []
    quality = []
    for p in CSV_FILES:
        df = pd.read_csv(p, low_memory=False)
        version = parse_version(p)
        gender = 'female' if p.name.startswith('female_') else 'male'
        df['source_file'] = p.name
        df['fifa_version'] = version
        df['season_label'] = f'FIFA {version:02d}'
        df['dataset_gender'] = gender
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                df[col] = np.nan
        n = len(df)
        value_valid = df['value_eur'].gt(0).sum()
        wage_valid = df['wage_eur'].notna().sum()
        cost_valid = (df['value_eur'].gt(0) & df['wage_eur'].ge(0)).sum()
        quality.append({
            'source_file': p.name,
            'dataset_gender': gender,
            'fifa_version': version,
            'rows': int(n),
            'value_eur_non_missing': int(df['value_eur'].notna().sum()),
            'value_eur_positive': int(value_valid),
            'wage_eur_non_missing': int(wage_valid),
            'wage_eur_positive': int(df['wage_eur'].gt(0).sum()),
            'cost_eligible_rows': int(cost_valid),
            'cost_eligible_pct': round(cost_valid / n * 100, 2) if n else 0,
        })
        frames.append(df)
    return pd.concat(frames, ignore_index=True), pd.DataFrame(quality)


def primary_position(s):
    if pd.isna(s):
        return ''
    return str(s).split(',')[0].strip().upper()


def position_group(pos):
    if pos in GK_POS: return 'GK'
    if pos in DEF_POS: return 'DEF'
    if pos in MID_POS: return 'MID'
    if pos in ATT_POS: return 'ATT'
    return 'OTHER'


def row_position_skill(row):
    pg = row.get('position_group', 'OTHER')
    vals = row
    def nz(x):
        return np.nan if pd.isna(x) else float(x)
    if pg == 'GK':
        cols = ['goalkeeping_diving','goalkeeping_handling','goalkeeping_kicking','goalkeeping_positioning','goalkeeping_reflexes']
        arr = [nz(vals[c]) for c in cols]
        if np.isfinite(arr).sum() >= 3:
            return float(np.nanmean(arr))
        return nz(vals['overall'])
    # Weighted positional skill from broad attributes; fall back to overall if too many missing.
    attrs = {c: nz(vals[c]) for c in ['pace','shooting','passing','dribbling','defending','physic']}
    if sum(np.isfinite(list(attrs.values()))) < 4:
        return nz(vals['overall'])
    if pg == 'DEF':
        weights = {'defending':0.35,'physic':0.25,'pace':0.15,'passing':0.15,'dribbling':0.10}
    elif pg == 'MID':
        weights = {'passing':0.30,'dribbling':0.20,'defending':0.20,'physic':0.15,'pace':0.10,'shooting':0.05}
    elif pg == 'ATT':
        weights = {'shooting':0.30,'dribbling':0.25,'pace':0.20,'passing':0.15,'physic':0.10}
    else:
        weights = {'pace':1/6,'shooting':1/6,'passing':1/6,'dribbling':1/6,'defending':1/6,'physic':1/6}
    num = den = 0.0
    for k,w in weights.items():
        if np.isfinite(attrs.get(k, np.nan)):
            num += attrs[k] * w
            den += w
    return num / den if den else nz(vals['overall'])


def percentile_0_100(s: pd.Series, ascending=True):
    # Percentile rank, stable for small groups. High value is better when ascending=True.
    valid = s.notna()
    out = pd.Series(np.nan, index=s.index, dtype='float')
    if valid.sum() == 0:
        return out
    if valid.sum() == 1:
        out.loc[valid] = 100.0
        return out
    ranks = s.loc[valid].rank(method='average', pct=True, ascending=ascending)
    out.loc[valid] = ranks * 100
    return out


def minmax_0_100(s: pd.Series):
    valid = s.notna()
    out = pd.Series(np.nan, index=s.index, dtype='float')
    if valid.sum() == 0:
        return out
    lo, hi = s.loc[valid].min(), s.loc[valid].max()
    if abs(hi - lo) < 1e-12:
        out.loc[valid] = 50.0
    else:
        out.loc[valid] = (s.loc[valid] - lo) / (hi - lo) * 100
    return out


def zscore(s: pd.Series):
    valid = s.notna()
    out = pd.Series(np.nan, index=s.index, dtype='float')
    if valid.sum() < 2:
        out.loc[valid] = 0.0
        return out
    mu = s.loc[valid].mean()
    sd = s.loc[valid].std(ddof=0)
    if sd == 0 or pd.isna(sd):
        out.loc[valid] = 0.0
    else:
        out.loc[valid] = (s.loc[valid] - mu) / sd
    return out


def linreg(x, y):
    # Simple OLS y = intercept + slope*x; returns y_hat, summary.
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 3:
        yhat = np.full_like(y, np.nan, dtype='float')
        return yhat, {'n': n, 'intercept': np.nan, 'slope': np.nan, 'r2': np.nan, 'rmse': np.nan}
    X = np.column_stack([np.ones(n), x[mask]])
    beta = np.linalg.lstsq(X, y[mask], rcond=None)[0]
    pred = X @ beta
    residuals = y[mask] - pred
    sse = float(np.sum(residuals**2))
    sst = float(np.sum((y[mask] - y[mask].mean())**2))
    r2 = 1 - sse/sst if sst > 0 else np.nan
    rmse = math.sqrt(sse/n)
    yhat = np.full_like(y, np.nan, dtype='float')
    yhat[mask] = pred
    return yhat, {'n': n, 'intercept': float(beta[0]), 'slope': float(beta[1]), 'r2': float(r2), 'rmse': float(rmse)}


def make_analysis():
    df, quality = load_all()
    df['primary_position'] = df['player_positions'].apply(primary_position)
    df['position_group'] = df['primary_position'].apply(position_group)
    df['position_skill_score'] = df.apply(row_position_skill, axis=1)
    df['age_resale_score'] = np.clip(100 - np.maximum(df['age'] - 24, 0) * 4 - np.maximum(24 - df['age'], 0) * 1.5, 0, 100)
    df['performance_score'] = (
        0.50 * df['overall'] +
        0.25 * df['potential'] +
        0.15 * df['position_skill_score'] +
        0.10 * df['age_resale_score']
    )
    df['annual_wage_eur'] = df['wage_eur'] * 52
    df['total_cost_eur'] = df['value_eur'] + df['annual_wage_eur']
    df['cost_million_eur'] = df['total_cost_eur'] / 1_000_000
    df['cost_eligible'] = df['value_eur'].gt(0) & df['wage_eur'].ge(0) & df['total_cost_eur'].gt(0) & df['performance_score'].notna()
    df['log_total_cost'] = np.where(df['cost_eligible'], np.log1p(df['total_cost_eur']), np.nan)

    # Formula 1: pure performance per cost. Use log cost to avoid cost outliers making all results tiny.
    df['vfm_formula_1_raw'] = df['performance_score'] / df['log_total_cost']

    # Formula 3/default: balanced z-score: performance higher than cost level.
    # Compute within FIFA version to avoid cross-year inflation/scaling bias.
    df['performance_z_by_season'] = np.nan
    df['cost_z_by_season'] = np.nan
    for version, idx in df[df['cost_eligible']].groupby('fifa_version').groups.items():
        idx = list(idx)
        df.loc[idx, 'performance_z_by_season'] = zscore(df.loc[idx, 'performance_score']).values
        df.loc[idx, 'cost_z_by_season'] = zscore(df.loc[idx, 'log_total_cost']).values
    df['vfm_formula_3_raw'] = df['performance_z_by_season'] - df['cost_z_by_season']

    # Formula 2: regression residual performance above expected cost.
    df['expected_performance_from_cost'] = np.nan
    df['regression_residual'] = np.nan
    summaries = []
    for version, sub_idx in df[df['cost_eligible']].groupby('fifa_version').groups.items():
        idx = np.array(list(sub_idx))
        yhat, summ = linreg(df.loc[idx, 'log_total_cost'].to_numpy(float), df.loc[idx, 'performance_score'].to_numpy(float))
        df.loc[idx, 'expected_performance_from_cost'] = yhat
        df.loc[idx, 'regression_residual'] = df.loc[idx, 'performance_score'].to_numpy(float) - yhat
        summaries.append({'fifa_version': int(version), 'season_label': f'FIFA {int(version):02d}', **summ})
    # Overall regression, across all seasons, for chart context.
    eligible_idx = df[df['cost_eligible']].index.to_numpy()
    yhat, summ = linreg(df.loc[eligible_idx, 'log_total_cost'].to_numpy(float), df.loc[eligible_idx, 'performance_score'].to_numpy(float))
    summaries.append({'fifa_version': 'all', 'season_label': 'All eligible rows', **summ})
    regression_summary = pd.DataFrame(summaries)

    # Index normalization per season: 0-100 percentile. Higher is better.
    for col in ['vfm_formula_1_raw', 'regression_residual', 'vfm_formula_3_raw']:
        idx_col = {
            'vfm_formula_1_raw':'vfm_formula_1_index',
            'regression_residual':'vfm_formula_2_index',
            'vfm_formula_3_raw':'vfm_index'
        }[col]
        df[idx_col] = np.nan
        for version, sub_idx in df[df['cost_eligible']].groupby('fifa_version').groups.items():
            sub_idx = list(sub_idx)
            df.loc[sub_idx, idx_col] = percentile_0_100(df.loc[sub_idx, col], ascending=True).values

    # Additional interpretable dimensions for radar.
    df['performance_percentile'] = np.nan
    df['potential_percentile'] = np.nan
    df['position_skill_percentile'] = np.nan
    df['age_value_percentile'] = np.nan
    df['cost_efficiency_percentile'] = np.nan
    df['wage_efficiency_percentile'] = np.nan
    for version, sub_idx in df[df['cost_eligible']].groupby('fifa_version').groups.items():
        sub_idx = list(sub_idx)
        df.loc[sub_idx, 'performance_percentile'] = percentile_0_100(df.loc[sub_idx, 'performance_score'], ascending=True).values
        df.loc[sub_idx, 'potential_percentile'] = percentile_0_100(df.loc[sub_idx, 'potential'], ascending=True).values
        df.loc[sub_idx, 'position_skill_percentile'] = percentile_0_100(df.loc[sub_idx, 'position_skill_score'], ascending=True).values
        df.loc[sub_idx, 'age_value_percentile'] = percentile_0_100(df.loc[sub_idx, 'age_resale_score'], ascending=True).values
        # cost efficiency: lower cost and lower wage are better.
        df.loc[sub_idx, 'cost_efficiency_percentile'] = percentile_0_100(df.loc[sub_idx, 'log_total_cost'], ascending=False).values
        df.loc[sub_idx, 'wage_efficiency_percentile'] = percentile_0_100(df.loc[sub_idx, 'annual_wage_eur'], ascending=False).values

    # Segments for cost-performance analysis.
    df['cost_performance_segment'] = 'not_cost_eligible'
    elig = df['cost_eligible']
    high_perf = df['performance_percentile'] >= 75
    low_cost = df['cost_efficiency_percentile'] >= 75
    high_cost = df['cost_efficiency_percentile'] <= 25
    low_perf = df['performance_percentile'] <= 25
    df.loc[elig & high_perf & low_cost, 'cost_performance_segment'] = 'high_perf_low_cost__value_buy'
    df.loc[elig & high_perf & high_cost, 'cost_performance_segment'] = 'high_perf_high_cost__premium_star'
    df.loc[elig & low_perf & low_cost, 'cost_performance_segment'] = 'low_perf_low_cost__budget_depth'
    df.loc[elig & low_perf & high_cost, 'cost_performance_segment'] = 'low_perf_high_cost__overpriced_risk'
    df.loc[elig & (df['cost_performance_segment'] == 'not_cost_eligible'), 'cost_performance_segment'] = 'mid_market'

    # Rankings.
    rank_cols = [
        'rank_vfm','fifa_version','season_label','dataset_gender','sofifa_id','short_name','long_name',
        'age','primary_position','position_group','overall','potential','performance_score',
        'value_eur','wage_eur','annual_wage_eur','total_cost_eur','cost_million_eur',
        'vfm_index','vfm_formula_1_index','vfm_formula_2_index','vfm_formula_3_raw','regression_residual',
        'club_name','league_name','nationality_name','player_url','cost_performance_segment'
    ]
    eligible_df = df[df['cost_eligible']].copy()
    eligible_df['rank_vfm'] = eligible_df.groupby('fifa_version')['vfm_index'].rank(method='first', ascending=False).astype(int)
    rankings_all = eligible_df.sort_values(['fifa_version','rank_vfm'])[rank_cols]
    rankings_by_season_top20 = rankings_all[rankings_all['rank_vfm'] <= 20]
    latest_version = int(eligible_df['fifa_version'].max()) if len(eligible_df) else None
    latest_top100 = rankings_all[(rankings_all['fifa_version'] == latest_version) & (rankings_all['rank_vfm'] <= 100)] if latest_version else pd.DataFrame()
    overall_top100 = eligible_df.sort_values('vfm_index', ascending=False).head(100)[rank_cols]

    # Scatter regression data.
    scatter_cols = [
        'fifa_version','season_label','dataset_gender','sofifa_id','short_name','age','primary_position','position_group',
        'overall','potential','performance_score','total_cost_eur','cost_million_eur','log_total_cost',
        'expected_performance_from_cost','regression_residual','vfm_index','cost_performance_segment'
    ]
    scatter = eligible_df[scatter_cols].copy()

    # Radar data for latest top 8 with high enough overall to avoid pure low-cost weak players.
    radar_base = eligible_df[eligible_df['fifa_version'] == latest_version].copy()
    radar_base = radar_base[radar_base['overall'] >= 70].sort_values('vfm_index', ascending=False).head(8)
    radar_dims = [
        ('Performance', 'performance_percentile'),
        ('Potential', 'potential_percentile'),
        ('Position skill', 'position_skill_percentile'),
        ('Age/resale', 'age_value_percentile'),
        ('Cost efficiency', 'cost_efficiency_percentile'),
        ('Wage efficiency', 'wage_efficiency_percentile'),
    ]
    radar_rows = []
    for _, r in radar_base.iterrows():
        for dim, col in radar_dims:
            radar_rows.append({
                'fifa_version': int(r['fifa_version']), 'season_label': r['season_label'], 'rank_vfm': int(r['rank_vfm']),
                'sofifa_id': int(r['sofifa_id']), 'short_name': r['short_name'], 'overall': r['overall'],
                'position_group': r['position_group'], 'dimension': dim, 'value_0_100': round(float(r[col]), 4)
            })
    radar = pd.DataFrame(radar_rows)

    # Segment summary.
    segment_summary = (eligible_df.groupby(['fifa_version','season_label','cost_performance_segment'], dropna=False)
        .agg(players=('sofifa_id','count'), avg_overall=('overall','mean'), avg_potential=('potential','mean'),
             avg_cost_million_eur=('cost_million_eur','mean'), avg_vfm_index=('vfm_index','mean'))
        .reset_index())
    for c in ['avg_overall','avg_potential','avg_cost_million_eur','avg_vfm_index']:
        segment_summary[c] = segment_summary[c].round(4)

    # Data dictionary / formulas.
    formula_doc = f"""# VfM 指标设计候选公式（4/29 前准备版）

## 数据口径
- 数据文件：`players_16.csv` 至 `players_22.csv`，以及 `female_players_16.csv` 至 `female_players_22.csv`。
- 成本口径：`total_cost_eur = value_eur + 52 * wage_eur`，即球员市场价值加一年工资。`wage_eur` 按 FIFA/SoFIFA 常见口径视为周薪。
- 可计算 VfM 的样本：`value_eur > 0` 且 `wage_eur >= 0` 且综合表现分不为空。
- 标准化口径：VfM 排名和 0-100 分均在同一 FIFA 版本内计算，避免不同年份的价格水平不可比。

## 表现分 performance_score
`performance_score = 0.50*overall + 0.25*potential + 0.15*position_skill_score + 0.10*age_resale_score`

其中：
- `overall`：当前能力。
- `potential`：潜力。
- `position_skill_score`：按 GK/DEF/MID/ATT 加权后的岗位能力。
- `age_resale_score`：年龄/转售价值因子，24 岁附近最高，年纪越大逐步扣分，年轻球员轻微扣分。

---

## 候选公式 1：简单成本效率公式（易解释）
`vfm_formula_1_raw = performance_score / ln(1 + total_cost_eur)`

优点：最容易解释，就是“表现 / 成本”。对成本使用 log，防止高价球员成本极端放大。  
缺点：低价低能力球员可能被推高，所以正式排行榜需要配合 `overall >= 70` 或岗位/联赛筛选。

## 候选公式 2：回归残差公式（找被低估球员）
先按赛季拟合：
`performance_score = a + b * ln(1 + total_cost_eur) + error`

`vfm_formula_2_index` 来自 `regression_residual = actual_performance_score - expected_performance_from_cost` 的赛季内百分位。

优点：能识别“以这个价位来说表现明显高于预期”的球员。  
缺点：对线性假设敏感，业务解释不如公式 1 直观。

## 候选公式 3：默认公式，平衡型 VfM Index
`vfm_formula_3_raw = z(performance_score) - z(ln(1 + total_cost_eur))`

`vfm_index = percentile_rank(vfm_formula_3_raw within same FIFA version) * 100`

优点：兼顾能力和成本，跨赛季内可比，输出为 0-100 分；适合作为默认排行榜。  
缺点：它是相对指标，不是绝对欧元收益。

## 推荐
当前项目默认采用公式 3 作为 `vfm_index`；公式 1 用于快速解释，公式 2 用于散点回归和“低估/高估”分析。
"""

    # Report markdown.
    cost_eligible_total = int(df['cost_eligible'].sum())
    total_rows = int(len(df))
    latest_name = f'FIFA {latest_version:02d}' if latest_version else 'N/A'
    top5 = latest_top100.head(5)
    top5_lines = []
    for _, r in top5.iterrows():
        top5_lines.append(f"{int(r['rank_vfm'])}. {r['short_name']}（{r['primary_position']}，Overall {int(r['overall'])}，成本 €{r['cost_million_eur']:.2f}m，VfM {r['vfm_index']:.2f}）")
    top5_text = '\n'.join(top5_lines) if top5_lines else '无可计算样本。'
    report = f"""# VfM Index 计算与性价比分析报告

## 已完成内容
1. 合并并清洗 14 个 CSV 文件，共 `{total_rows:,}` 行。
2. 计算成本、表现分、3 套候选 VfM 指标和默认 `vfm_index`。
3. 输出排行榜、散点回归数据、回归摘要、雷达图数据和成本-表现分层表。
4. 生成可复现脚本 `vfm_pipeline.py`。

## 数据质量关键结论
- 可计算 VfM 的记录数：`{cost_eligible_total:,}` 行。
- `female_players_16.csv` 至 `female_players_21.csv` 的 `value_eur` 和 `wage_eur` 基本为空，无法计算成本型 VfM；`female_players_22.csv` 只有部分球员可计算。因此主榜默认以成本可用样本为准。
- 每个赛季内单独标准化，避免直接把 FIFA 16 和 FIFA 22 的价格水平混在一起比较。

## 默认 VfM Index
默认指标采用候选公式 3：

`vfm_index = percentile_rank(z(performance_score) - z(log_total_cost), within same FIFA version) * 100`

这意味着：同一赛季内，表现越高、总成本越低，`vfm_index` 越接近 100。

## {latest_name} 默认排行榜 Top 5
{top5_text}

## 成本-表现分层解释
- `high_perf_low_cost__value_buy`：高表现、低成本，优先关注。
- `high_perf_high_cost__premium_star`：高表现、高成本，明星/溢价球员。
- `low_perf_low_cost__budget_depth`：低表现、低成本，替补深度或青训储备。
- `low_perf_high_cost__overpriced_risk`：低表现、高成本，性价比风险。
- `mid_market`：中间市场。

## 主要输出文件
- `outputs/vfm_master.csv`：逐球员逐赛季指标全量表。
- `outputs/rankings_by_season_top20.csv`：每个 FIFA 版本 Top 20 排行榜。
- `outputs/rankings_latest_top100.csv`：最新 FIFA 版本 Top 100 排行榜。
- `outputs/scatter_regression_data.csv`：散点回归点数据。
- `outputs/regression_summary_by_season.csv`：回归摘要。
- `outputs/radar_chart_data_top8_latest.csv`：最新赛季 Top 8 雷达图长表数据。
- `outputs/cost_performance_segments.csv`：成本-表现象限/分层汇总。
- `figures/scatter_regression_latest.png`：最新赛季散点回归图。
- `figures/radar_top8_latest.png`：最新赛季 Top 8 雷达图。

## 使用建议
正式汇报时建议展示：
1. 默认 `vfm_index` 排行榜；
2. 散点回归图，用残差解释“低估/高估”；
3. 雷达图，用 6 个维度解释球员为什么高性价比。
"""

    outdir = OUT / 'outputs'
    outdir.mkdir(exist_ok=True)
    # Save outputs.
    quality.to_csv(outdir / 'data_quality_summary.csv', index=False)
    keep_cols = sorted(set(META_COLS + [
        'source_file','fifa_version','season_label','dataset_gender','primary_position','position_group',
        'overall','potential','age','position_skill_score','age_resale_score','performance_score',
        'value_eur','wage_eur','annual_wage_eur','total_cost_eur','cost_million_eur','log_total_cost','cost_eligible',
        'expected_performance_from_cost','regression_residual','vfm_formula_1_raw','vfm_formula_1_index',
        'vfm_formula_2_index','vfm_formula_3_raw','vfm_index','performance_percentile','potential_percentile',
        'position_skill_percentile','age_value_percentile','cost_efficiency_percentile','wage_efficiency_percentile',
        'cost_performance_segment'
    ]))
    # keep only existing columns
    keep_cols = [c for c in keep_cols if c in df.columns]
    df[keep_cols].to_csv(outdir / 'vfm_master.csv', index=False)
    rankings_all.to_csv(outdir / 'rankings_all_eligible.csv', index=False)
    rankings_by_season_top20.to_csv(outdir / 'rankings_by_season_top20.csv', index=False)
    latest_top100.to_csv(outdir / 'rankings_latest_top100.csv', index=False)
    overall_top100.to_csv(outdir / 'rankings_overall_top100.csv', index=False)
    scatter.to_csv(outdir / 'scatter_regression_data.csv', index=False)
    regression_summary.to_csv(outdir / 'regression_summary_by_season.csv', index=False)
    radar.to_csv(outdir / 'radar_chart_data_top8_latest.csv', index=False)
    segment_summary.to_csv(outdir / 'cost_performance_segments.csv', index=False)
    (OUT / 'candidate_formulas.md').write_text(formula_doc, encoding='utf-8')
    (OUT / 'vfm_analysis_report.md').write_text(report, encoding='utf-8')

    # Make figures.
    if latest_version is not None:
        latest = eligible_df[eligible_df['fifa_version'] == latest_version].copy()
        # To keep plot light, sample all if <=5000, otherwise deterministic sample.
        plot_df = latest if len(latest) <= 5000 else latest.sample(5000, random_state=42)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(plot_df['log_total_cost'], plot_df['performance_score'], alpha=0.35, s=12)
        # Regression line for latest season.
        summ = regression_summary[regression_summary['fifa_version'].astype(str) == str(latest_version)].iloc[0]
        xs = np.linspace(latest['log_total_cost'].min(), latest['log_total_cost'].max(), 100)
        ys = summ['intercept'] + summ['slope'] * xs
        ax.plot(xs, ys, linewidth=2)
        ax.set_title(f'Scatter Regression: Performance vs Log Cost ({latest_name})')
        ax.set_xlabel('log(1 + total_cost_eur)')
        ax.set_ylabel('performance_score')
        ax.text(0.02, 0.98, f"R²={summ['r2']:.3f}\nRMSE={summ['rmse']:.2f}\nn={int(summ['n'])}", transform=ax.transAxes, va='top')
        fig.tight_layout()
        fig.savefig(FIG / 'scatter_regression_latest.png', dpi=160)
        plt.close(fig)

        # Top 20 latest vfm bar chart.
        b = latest_top100.head(20).iloc[::-1]
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(b['short_name'], b['vfm_index'])
        ax.set_xlabel('VfM Index (0-100)')
        ax.set_title(f'Top 20 VfM Ranking ({latest_name})')
        fig.tight_layout()
        fig.savefig(FIG / 'vfm_top20_latest.png', dpi=160)
        plt.close(fig)

        # Radar chart for top 8, each own figure? Here one combined radar.
        if len(radar_base) > 0:
            dims = [d[0] for d in radar_dims]
            angles = np.linspace(0, 2*np.pi, len(dims), endpoint=False).tolist()
            angles += angles[:1]
            fig = plt.figure(figsize=(9, 9))
            ax = plt.subplot(111, polar=True)
            for _, r in radar_base.iterrows():
                vals = [float(r[col]) for _, col in radar_dims]
                vals += vals[:1]
                ax.plot(angles, vals, linewidth=1.5, label=f"{int(r['rank_vfm'])}. {r['short_name']}")
                ax.fill(angles, vals, alpha=0.05)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(dims)
            ax.set_ylim(0, 100)
            ax.set_title(f'Radar Data Preview: Top 8 VfM ({latest_name}, Overall ≥ 70)')
            ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=8)
            fig.tight_layout()
            fig.savefig(FIG / 'radar_top8_latest.png', dpi=160)
            plt.close(fig)

    # Reproducible pipeline script placed in module folder.
    current_code = Path(__file__).read_text(encoding='utf-8')
    (OUT / 'vfm_pipeline.py').write_text(current_code.replace("ROOT = Path(__file__).resolve().parents[3]", "ROOT = Path(__file__).resolve().parents[3]"), encoding='utf-8')

    # README.
    readme = """# services/data_analysis/vfm

这个目录包含 VfM（Value for Money）指标计算、排行榜、散点回归、雷达图数据和性价比分析的可复现输出。

## 快速运行
把 `players_16.csv` 至 `players_22.csv`、`female_players_16.csv` 至 `female_players_22.csv` 放在项目根目录，然后运行：

```bash
python services/data_analysis/vfm/vfm_pipeline.py
```

## 默认指标
默认 `vfm_index` 使用候选公式 3：

```text
vfm_index = percentile_rank(z(performance_score) - z(log(1 + total_cost_eur)), within same FIFA version) * 100
```

同一 FIFA 版本内，表现越高、成本越低，分数越接近 100。

## 输出说明
详见 `vfm_analysis_report.md` 和 `candidate_formulas.md`。
"""
    (OUT / 'README.md').write_text(readme, encoding='utf-8')

    # Build zip.
    zip_path = ROOT / 'vfm_analysis_package.zip'
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for f in OUT.rglob('*'):
            if f.is_file():
                z.write(f, f.relative_to(ROOT))
    return {
        'out_dir': str(OUT),
        'zip_path': str(zip_path),
        'rows': total_rows,
        'cost_eligible': cost_eligible_total,
        'latest_version': latest_version,
        'latest_top5': top5[['rank_vfm','short_name','overall','cost_million_eur','vfm_index']].to_dict(orient='records') if len(top5) else [],
        'files': [str(p.relative_to(OUT)) for p in sorted(OUT.rglob('*')) if p.is_file()]
    }

if __name__ == '__main__':
    result = make_analysis()
    print(json.dumps(result, ensure_ascii=False, indent=2))
