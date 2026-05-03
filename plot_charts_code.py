"""
Plot code for services/data_analysis/vfm

用途：
1. 根据 outputs/scatter_regression_data.csv 和 outputs/regression_summary_by_season.csv 生成散点回归图。
2. 根据 outputs/radar_chart_data_top8_latest.csv 生成雷达图。
3. 根据 outputs/rankings_latest_top100.csv 生成 Top 20 VfM 排行榜柱状图。

运行方式：
python services/data_analysis/vfm/plot_charts_code.py

说明：
- 这份代码不会影响 VfM 计算结果，只负责读取 CSV 并绘图。
- 如果不想保存图片，可以把 plt.savefig(...) 改成 plt.show()。
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def plot_scatter_regression():
    """散点回归图：x=log(1+总成本)，y=表现分，并叠加线性回归线。"""
    scatter = pd.read_csv(OUTPUTS_DIR / "scatter_regression_data.csv")
    regression = pd.read_csv(OUTPUTS_DIR / "regression_summary_by_season.csv")

    latest_version = int(scatter["fifa_version"].max())
    latest = scatter[scatter["fifa_version"] == latest_version].copy()
    summary = regression[regression["fifa_version"].astype(str) == str(latest_version)].iloc[0]

    plot_df = latest if len(latest) <= 5000 else latest.sample(5000, random_state=42)

    plt.figure(figsize=(10, 6))
    plt.scatter(
        plot_df["log_total_cost"],
        plot_df["performance_score"],
        alpha=0.35,
        s=12,
    )

    x_values = np.linspace(latest["log_total_cost"].min(), latest["log_total_cost"].max(), 100)
    y_values = summary["intercept"] + summary["slope"] * x_values
    plt.plot(x_values, y_values, linewidth=2)

    plt.title(f"Scatter Regression: Performance vs Log Cost - FIFA {latest_version:02d}")
    plt.xlabel("log(1 + total_cost_eur)")
    plt.ylabel("performance_score")
    plt.text(
        0.02,
        0.98,
        f"R²={summary['r2']:.3f}\nRMSE={summary['rmse']:.2f}\nn={int(summary['n'])}",
        transform=plt.gca().transAxes,
        va="top",
    )
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scatter_regression_latest.png", dpi=160)
    # plt.show()


def plot_radar_chart():
    """雷达图：读取长表 radar_chart_data_top8_latest.csv，展示 Top 8 球员 6 个维度。"""
    radar = pd.read_csv(OUTPUTS_DIR / "radar_chart_data_top8_latest.csv")
    if radar.empty:
        print("radar_chart_data_top8_latest.csv 为空，无法绘制雷达图。")
        return

    dimensions = radar["dimension"].drop_duplicates().tolist()
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]

    plt.figure(figsize=(9, 9))
    ax = plt.subplot(111, polar=True)

    for player_name, player_df in radar.groupby("short_name", sort=False):
        player_df = player_df.set_index("dimension").loc[dimensions].reset_index()
        values = player_df["value_0_100"].astype(float).tolist()
        values += values[:1]
        rank = int(player_df["rank_vfm"].iloc[0])
        ax.plot(angles, values, linewidth=1.5, label=f"{rank}. {player_name}")
        ax.fill(angles, values, alpha=0.05)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions)
    ax.set_ylim(0, 100)
    latest_version = int(radar["fifa_version"].max())
    ax.set_title(f"Radar Chart: Top 8 VfM - FIFA {latest_version:02d}")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "radar_top8_latest.png", dpi=160)
    # plt.show()


def plot_vfm_top20_bar():
    """VfM Top 20 横向柱状图。"""
    ranking = pd.read_csv(OUTPUTS_DIR / "rankings_latest_top100.csv")
    top20 = ranking.head(20).iloc[::-1]
    latest_version = int(top20["fifa_version"].max())

    plt.figure(figsize=(10, 8))
    plt.barh(top20["short_name"], top20["vfm_index"])
    plt.xlabel("VfM Index (0-100)")
    plt.title(f"Top 20 VfM Ranking - FIFA {latest_version:02d}")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "vfm_top20_latest.png", dpi=160)
    # plt.show()


if __name__ == "__main__":
    plot_scatter_regression()
    plot_radar_chart()
    plot_vfm_top20_bar()
    print(f"绘图完成，输出目录：{FIGURES_DIR}")
