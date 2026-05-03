# services/data_analysis/vfm

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

## 补充榜单
- `rankings_latest_practical_top100.csv`：过滤年龄和能力门槛，更适合实战推荐。
- `rankings_latest_young_value_top100.csv`：U25 高潜力性价比榜。
- `rankings_latest_by_position_group_top20.csv`：按位置组分榜，避免某一位置垄断总榜。


## 绘图代码
图片不需要手动提交。需要生成散点回归图、雷达图或 Top 20 柱状图时，运行：

```bash
python services/data_analysis/vfm/plot_charts_code.py
```

对应数据源：
- 散点回归图：`outputs/scatter_regression_data.csv` + `outputs/regression_summary_by_season.csv`
- 雷达图：`outputs/radar_chart_data_top8_latest.csv`
- 排行榜柱状图：`outputs/rankings_latest_top100.csv`
