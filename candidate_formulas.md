# VfM 指标设计候选公式（4/29 前准备版）

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
