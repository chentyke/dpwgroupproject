from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MPL_CACHE_DIR = Path(
    os.environ.get("MPLCONFIGDIR", "/private/tmp/dpwgroupproject-matplotlib-cache")
)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 1))
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

from app.services.advanced import build_cluster_response, build_prediction_response
from app.services.data_repository import get_player_repository
from app.services.dataset import build_cleaning_report
from app.services.fairness import (
    build_fairness_by_league,
    build_nationality_heatmap,
)
from app.services.vfm import build_vfm_response

FIG_DPI = 180
TEXT_COLOR = "#111827"
MUTED_COLOR = "#6b7280"
GRID_COLOR = "#e5e7eb"
BLUE = "#2563eb"
TEAL = "#0f766e"
GREEN = "#16a34a"
AMBER = "#d97706"
ROSE = "#e11d48"
PURPLE = "#7c3aed"
SLATE = "#64748b"
PALETTE = [BLUE, TEAL, GREEN, AMBER, ROSE, PURPLE, "#0891b2", "#4f46e5"]


def compact_currency(value: float, _position: int | None = None) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"€{value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"€{value / 1_000:.0f}K"
    return f"€{value:.0f}"


def compact_number(value: float, _position: int | None = None) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:.0f}"


def compact_league_name(name: str) -> str:
    replacements = {
        "English Premier League": "Premier League",
        "Spain Primera Division": "LaLiga",
        "German 1. Bundesliga": "Bundesliga",
        "Italian Serie A": "Serie A",
        "French Ligue 1": "Ligue 1",
        "English League Championship": "Championship",
        "Campeonato Brasileiro Serie A": "Brasileirao",
        "Campeonato Brasileiro Série A": "Brasileirao",
        "Portuguese Liga ZON SAGRES": "Liga Portugal",
        "Argentina Primera Division": "Argentina Primera",
        "Argentina Primera División": "Argentina Primera",
        "Saudi Abdul L. Jameel League": "Saudi Pro League",
        "USA Major League Soccer": "MLS",
    }
    compacted = replacements.get(name, name)
    return compacted if len(compacted) <= 28 else f"{compacted[:25]}..."


def style_axis(ax: plt.Axes, *, grid_axis: str = "y") -> None:
    ax.tick_params(colors=MUTED_COLOR, labelsize=9)
    ax.xaxis.label.set_color(MUTED_COLOR)
    ax.yaxis.label.set_color(MUTED_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(True, axis=grid_axis, color=GRID_COLOR, linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)


def save_figure(fig: plt.Figure, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=FIG_DPI,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
    return output_path


def empty_chart(title: str, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.text(0.5, 0.5, "No data available", ha="center", va="center", color=MUTED_COLOR)
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=TEXT_COLOR)
    ax.set_axis_off()
    return save_figure(fig, output_path)


def export_null_hotspots(repository, output_dir: Path) -> Path:
    report = build_cleaning_report(repository)
    hotspots = list(report.null_hotspots)
    output_path = output_dir / "00_data_cleaning_null_hotspots.png"
    if not hotspots:
        return empty_chart("Data cleaning null hotspots", output_path)

    labels = [item.column for item in hotspots]
    values = [item.null_rate * 100 for item in hotspots]
    y_positions = np.arange(len(labels))

    fig_height = max(4.8, len(labels) * 0.55 + 1.8)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    ax.barh(y_positions, values, color=BLUE, alpha=0.88)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Null rate")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
    ax.set_title(
        "Data cleaning null hotspots",
        loc="left",
        fontsize=14,
        fontweight="bold",
        color=TEXT_COLOR,
    )
    ax.set_xlim(0, max(values) * 1.18 if values else 1)
    for index, value in enumerate(values):
        ax.text(
            value + max(values) * 0.025,
            index,
            f"{value:.1f}%",
            va="center",
            fontsize=9,
            color=MUTED_COLOR,
        )
    style_axis(ax, grid_axis="x")
    fig.tight_layout()
    return save_figure(fig, output_path)


def export_vfm_radar(repository, output_dir: Path, position: str, max_value: int) -> Path:
    response = build_vfm_response(repository, position=position, max_value=max_value)
    output_path = output_dir / "01_value_for_money_benchmark_radar.png"
    metrics = response.benchmark_metrics
    if not metrics and response.candidates:
        metrics = response.candidates[0].metrics
    if not metrics:
        return empty_chart("Value-for-money benchmark radar", output_path)

    labels = [metric.label for metric in metrics]
    values = [float(metric.value) for metric in metrics]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    fig = plt.figure(figsize=(7.2, 7.2))
    ax = fig.add_subplot(111, projection="polar")
    ax.plot(angles_closed, values_closed, color=BLUE, linewidth=2.2)
    ax.fill(angles_closed, values_closed, color=BLUE, alpha=0.18)
    ax.set_ylim(0, 100)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, color=MUTED_COLOR, fontsize=9)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], color=MUTED_COLOR, fontsize=8)
    ax.grid(color=GRID_COLOR, linewidth=0.9)
    ax.spines["polar"].set_color(GRID_COLOR)
    ax.set_title(
        f"{response.benchmark_name} attribute radar",
        loc="left",
        pad=26,
        fontsize=14,
        fontweight="bold",
        color=TEXT_COLOR,
    )
    fig.tight_layout()
    return save_figure(fig, output_path)


def export_vfm_scatter(repository, output_dir: Path, position: str, max_value: int) -> Path:
    response = build_vfm_response(repository, position=position, max_value=max_value)
    output_path = output_dir / "02_value_for_money_market_scatter.png"
    points = [point for point in response.scatter_points if point.value_eur > 0]
    if not points:
        return empty_chart("Value-for-money market scatter", output_path)

    base_points = [point for point in points if not point.highlight]
    highlight_points = [point for point in points if point.highlight]

    fig, ax = plt.subplots(figsize=(11, 6.4))
    if base_points:
        ax.scatter(
            [point.value_eur for point in base_points],
            [point.overall for point in base_points],
            s=18,
            color=SLATE,
            alpha=0.28,
            edgecolors="none",
            label="Market players",
        )
    if highlight_points:
        ax.scatter(
            [point.value_eur for point in highlight_points],
            [point.overall for point in highlight_points],
            s=72,
            color=AMBER,
            alpha=0.95,
            edgecolors="white",
            linewidths=0.9,
            label="Top highlighted candidates",
        )
        for point in highlight_points:
            ax.annotate(
                point.short_name,
                (point.value_eur, point.overall),
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=8,
                color=TEXT_COLOR,
            )

    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(compact_currency))
    ax.set_xlabel("Market value")
    ax.set_ylabel("Overall rating")
    ax.set_title(
        f"{response.position} candidates: value vs. rating",
        loc="left",
        fontsize=14,
        fontweight="bold",
        color=TEXT_COLOR,
    )
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    style_axis(ax, grid_axis="both")
    fig.tight_layout()
    return save_figure(fig, output_path)


def export_wage_spread(
    repository,
    output_dir: Path,
    overall_min: int,
    overall_max: int,
) -> Path:
    response = build_fairness_by_league(
        repository,
        overall_min=overall_min,
        overall_max=overall_max,
    )
    output_path = output_dir / "03_fairness_league_wage_spread.png"
    items = response.distributions
    if not items:
        return empty_chart("League wage spread", output_path)

    labels = [compact_league_name(item.league_name) for item in items]
    y_positions = np.arange(len(items))
    min_values = [item.min_wage for item in items]
    average_values = [item.average_wage for item in items]
    median_values = [item.median_wage for item in items]
    max_values = [item.max_wage for item in items]

    fig_height = max(7.0, len(items) * 0.34 + 2.0)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.hlines(y_positions, min_values, max_values, color=SLATE, alpha=0.55, linewidth=3)
    ax.scatter(average_values, y_positions, color=BLUE, s=54, label="Average", zorder=3)
    ax.scatter(
        median_values,
        y_positions,
        color=AMBER,
        marker="D",
        s=36,
        label="Median",
        zorder=4,
    )
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(compact_currency))
    ax.set_xlabel("Wage")
    ax.set_title(
        f"League wage spread for overall {response.overall_min}-{response.overall_max}",
        loc="left",
        fontsize=14,
        fontweight="bold",
        color=TEXT_COLOR,
    )
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    style_axis(ax, grid_axis="x")
    fig.tight_layout()
    return save_figure(fig, output_path)


def _sorted_heatmap_categories(cells, key_name: str) -> list[str]:
    totals: dict[str, list[int]] = {}
    for cell in cells:
        key = getattr(cell, key_name)
        totals.setdefault(key, []).append(cell.average_wage)
    return [
        key
        for key, _values in sorted(
            totals.items(),
            key=lambda item: (sum(item[1]) / len(item[1]), item[0]),
            reverse=True,
        )
    ]


def export_nationality_heatmap(repository, output_dir: Path) -> Path:
    response = build_nationality_heatmap(repository)
    output_path = output_dir / "04_fairness_nationality_heatmap.png"
    cells = response.cells
    if not cells:
        return empty_chart("Nationality wage heatmap", output_path)

    nationalities = _sorted_heatmap_categories(cells, "nationality_name")
    leagues = _sorted_heatmap_categories(cells, "league_name")
    matrix = np.full((len(nationalities), len(leagues)), np.nan)
    for cell in cells:
        row = nationalities.index(cell.nationality_name)
        column = leagues.index(cell.league_name)
        matrix[row, column] = cell.average_wage

    fig_width = max(11.5, len(leagues) * 0.8 + 3.0)
    fig_height = max(7.0, len(nationalities) * 0.34 + 2.2)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    cmap = plt.colormaps["YlGnBu"].copy()
    cmap.set_bad("#f3f4f6")
    image = ax.imshow(matrix, cmap=cmap, aspect="auto")

    ax.set_xticks(np.arange(len(leagues)))
    ax.set_xticklabels([compact_league_name(name) for name in leagues], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(nationalities)))
    ax.set_yticklabels(nationalities)
    ax.set_title(
        "Average wage by nationality and league",
        loc="left",
        fontsize=14,
        fontweight="bold",
        color=TEXT_COLOR,
    )

    max_value = np.nanmax(matrix)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = matrix[row, column]
            if np.isnan(value):
                continue
            color = "white" if value > max_value * 0.62 else TEXT_COLOR
            ax.text(
                column,
                row,
                compact_number(value),
                ha="center",
                va="center",
                fontsize=7,
                color=color,
            )

    colorbar = fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02)
    colorbar.ax.yaxis.set_major_formatter(FuncFormatter(compact_currency))
    colorbar.ax.tick_params(labelsize=8, colors=MUTED_COLOR)
    ax.tick_params(colors=MUTED_COLOR, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    fig.tight_layout()
    return save_figure(fig, output_path)


def export_cluster_scatter(repository, output_dir: Path, clusters: int) -> Path:
    response = build_cluster_response(repository, k=clusters)
    output_path = output_dir / "05_advanced_cluster_scatter.png"
    if not response.points:
        return empty_chart("Playing-style clusters", output_path)

    sample_every = max(1, len(response.points) // 1600)
    sampled_points = response.points[::sample_every]
    labels = [summary.label for summary in response.summaries]

    fig, ax = plt.subplots(figsize=(11, 6.6))
    for index, label in enumerate(labels):
        label_points = [point for point in sampled_points if point.label == label]
        if not label_points:
            continue
        ax.scatter(
            [point.x for point in label_points],
            [point.y for point in label_points],
            s=18,
            color=PALETTE[index % len(PALETTE)],
            alpha=0.68,
            edgecolors="none",
            label=f"{label} ({len(label_points)})",
        )

    ax.set_xlabel("PCA component 1")
    ax.set_ylabel("PCA component 2")
    ax.set_title(
        f"FIFA 22 playing-style clusters (k={response.k})",
        loc="left",
        fontsize=14,
        fontweight="bold",
        color=TEXT_COLOR,
    )
    ax.legend(frameon=False, fontsize=8, loc="best", markerscale=1.4)
    style_axis(ax, grid_axis="both")
    fig.tight_layout()
    return save_figure(fig, output_path)


def export_prediction_weights(repository, output_dir: Path) -> Path:
    response = build_prediction_response(
        repository,
        overall=87,
        potential=92,
        age=21,
        wage_eur=85_000,
        pace=84,
        shooting=78,
        dribbling=91,
        passing=82,
        defending=57,
        physic=64,
    )
    output_path = output_dir / "06_advanced_prediction_feature_weights.png"
    contributions = sorted(
        response.contributions,
        key=lambda item: abs(item.weight),
        reverse=True,
    )
    if not contributions:
        return empty_chart("Prediction feature weights", output_path)

    labels = [item.feature for item in contributions]
    values = [item.weight for item in contributions]
    colors = [GREEN if value >= 0 else ROSE for value in values]
    y_positions = np.arange(len(labels))

    fig_height = max(5.4, len(labels) * 0.42 + 1.8)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    ax.barh(y_positions, values, color=colors, alpha=0.88)
    ax.axvline(0, color=TEXT_COLOR, linewidth=0.9)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Standardized model weight")
    ax.set_title(
        "Value prediction feature weights",
        loc="left",
        fontsize=14,
        fontweight="bold",
        color=TEXT_COLOR,
    )
    for index, value in enumerate(values):
        alignment = "left" if value >= 0 else "right"
        offset = 0.02 * max(abs(number) for number in values)
        ax.text(
            value + (offset if value >= 0 else -offset),
            index,
            f"{value:.2f}",
            va="center",
            ha=alignment,
            fontsize=8,
            color=MUTED_COLOR,
        )
    style_axis(ax, grid_axis="x")
    fig.tight_layout()
    return save_figure(fig, output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export the dashboard analysis charts as PNG files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "charts_png",
        help="Directory where PNG files will be written.",
    )
    parser.add_argument("--position", default="CAM", help="VfM position filter.")
    parser.add_argument(
        "--max-value",
        type=int,
        default=120_000_000,
        help="VfM maximum value filter in EUR.",
    )
    parser.add_argument(
        "--overall-min",
        type=int,
        default=80,
        help="Minimum overall rating for fairness wage spread.",
    )
    parser.add_argument(
        "--overall-max",
        type=int,
        default=90,
        help="Maximum overall rating for fairness wage spread.",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=5,
        choices=range(2, 7),
        metavar="{2,3,4,5,6}",
        help="Cluster count for the advanced cluster chart.",
    )
    return parser.parse_args()


def export_all_charts(args: argparse.Namespace) -> Iterable[Path]:
    output_dir = args.output_dir.resolve()
    repository = get_player_repository()
    return [
        export_null_hotspots(repository, output_dir),
        export_vfm_radar(repository, output_dir, args.position, args.max_value),
        export_vfm_scatter(repository, output_dir, args.position, args.max_value),
        export_wage_spread(
            repository,
            output_dir,
            args.overall_min,
            args.overall_max,
        ),
        export_nationality_heatmap(repository, output_dir),
        export_cluster_scatter(repository, output_dir, args.clusters),
        export_prediction_weights(repository, output_dir),
    ]


def main() -> None:
    args = parse_args()
    exported = export_all_charts(args)
    for path in exported:
        print(path)


if __name__ == "__main__":
    main()
