# VfM Index 计算与性价比分析报告

## 已完成内容
1. 合并并清洗 14 个 CSV 文件，共 `128,168` 行。
2. 计算成本、表现分、3 套候选 VfM 指标和默认 `vfm_index`。
3. 输出排行榜、散点回归数据、回归摘要、雷达图数据和成本-表现分层表。
4. 生成可复现脚本 `vfm_pipeline.py`。

## 数据质量关键结论
- 可计算 VfM 的记录数：`124,384` 行。
- `female_players_16.csv` 至 `female_players_21.csv` 的 `value_eur` 和 `wage_eur` 基本为空，无法计算成本型 VfM；`female_players_22.csv` 只有部分球员可计算。因此主榜默认以成本可用样本为准。
- 每个赛季内单独标准化，避免直接把 FIFA 16 和 FIFA 22 的价格水平混在一起比较。

## 默认 VfM Index
默认指标采用候选公式 3：

`vfm_index = percentile_rank(z(performance_score) - z(log_total_cost), within same FIFA version) * 100`

这意味着：同一赛季内，表现越高、总成本越低，`vfm_index` 越接近 100。

## FIFA 22 默认排行榜 Top 5
1. A. Gabbarini（GK，Overall 72，成本 €0.28m，VfM 100.00）
2. A. Hruška（GK，Overall 71，成本 €0.24m，VfM 99.99）
3. W. Sandilands（GK，Overall 71，成本 €0.24m，VfM 99.99）
4. D. Akpeyi（GK，Overall 74，成本 €0.50m，VfM 99.98）
5. D. Frascarelli（GK，Overall 70，成本 €0.21m，VfM 99.98）



## 最新赛季实用筛选榜 Top 5（age <= 30 且 Overall >= 75 或 Potential >= 80）
这个榜比原始总榜更适合转会/阵容分析，因为它过滤掉了大量“成本极低但年龄偏大”的替补或门将样本。

1. G. Bazunu（GK，19岁，Overall 64，Potential 83，成本 €1.35m，VfM 98.44）
2. M. Vandevoordt（GK，19岁，Overall 71，Potential 87，成本 €4.46m，VfM 98.34）
3. R. Jones（ST，18岁，Overall 60，Potential 80，成本 €0.73m，VfM 98.18）
4. V. Korniienko（LB，22岁，Overall 71，Potential 82，成本 €4.03m，VfM 97.81）
5. L. Morales（GK，21岁，Overall 72，Potential 85，成本 €5.31m，VfM 97.74）

新增输出：
- `outputs/rankings_latest_practical_top100.csv`：最新赛季实用筛选 Top 100。
- `outputs/rankings_latest_young_value_top100.csv`：U25 高潜力性价比 Top 100。
- `outputs/rankings_latest_by_position_group_top20.csv`：按 GK/DEF/MID/ATT/OTHER 分组 Top 20。

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
