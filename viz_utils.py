from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

import numpy as np

try:
    from DBSCAN.multi_target_dbscan_tracker import MultiTargetDBSCANTracker
except ModuleNotFoundError:
    from multi_target_dbscan_tracker import MultiTargetDBSCANTracker


PUBLICATION_COLORS = {
    "background": "#FFFFFF",
    "history": "#9AA7B2",
    "current": "#0F4D92",
    "core": "#2E8B57",
    "noise": "#B35C52",
    "center": "#C67C2D",
    "box": "#37474F",
    "grid": "#D6DEE5",
    "text": "#18232D",
}

PUBLICATION_FIXED_RANGES = {
    "single": {
        "raw": {
            "x": (84.0, 174.0),
            "z": (348.0, 480.0),
            "y": (-62.0, 18.0),
        },
        "cluster": {
            "x": (92.0, 166.0),
            "z": (352.0, 480.0),
            "y": (-54.0, 10.0),
        },
    },
    "multi": {
        "raw": {
            "x": (96.0, 186.0),
            "z": (338.0, 470.0),
            "y": (-38.0, 42.0),
        },
        "cluster": {
            "x": (106.0, 180.0),
            "z": (342.0, 470.0),
            "y": (-30.0, 34.0),
        },
    },
}

MULTI_DEMO_CENTERS = {
    "A": np.array([112.0, -12.0, 346.0]),
    "B": np.array([142.0, 6.0, 356.0]),
    "C": np.array([172.0, -8.0, 349.0]),
}

PSEUDO_TARGET_CENTER = np.array([222.0, 92.0, 446.0])

PUBLICATION_BOX_STYLE = {
    "color": "#37474F",
    "linewidth": 1.2,
    "alpha": 0.98,
    "fill": False,
}

PUBLICATION_MARKER_SIZES = {
    "raw_history": 14,
    "raw_current": 52,
    "window_points": 8,
    "cluster_core": 10,
    "cluster_noise": 7,
    "cluster_other": 7,
    "center": 110,
}

TRACK_COLORS = [
    "#0F4D92",
    "#2E8B57",
    "#C67C2D",
    "#8F4E7A",
    "#1C8C8C",
    "#7A6F52",
]

_SCIENTIFIC_FIGURE_PRO = None


@dataclass(frozen=True)
class TrackSnapshot:
    track_id: int
    history: np.ndarray
    window: np.ndarray
    labels: np.ndarray
    center: Optional[np.ndarray]
    locked: bool
    core_size: int
    sigma: float
    reason: str
    last_observation: np.ndarray
    age: int
    missed_frames: int
    active: bool


def _load_scientific_figure_pro():
    global _SCIENTIFIC_FIGURE_PRO
    if _SCIENTIFIC_FIGURE_PRO is not None:
        return _SCIENTIFIC_FIGURE_PRO

    module_path = Path("/home/kesl/.codex/skills/scientific-figure-pro/scripts/scientific_figure_pro.py")
    if not module_path.exists():
        _SCIENTIFIC_FIGURE_PRO = False
        return None

    spec = importlib.util.spec_from_file_location("scientific_figure_pro_runtime", module_path)
    if spec is None or spec.loader is None:
        _SCIENTIFIC_FIGURE_PRO = False
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _SCIENTIFIC_FIGURE_PRO = module
    return module


def apply_publication_style(font_size: float = 12.0, axes_linewidth: float = 1.2) -> None:
    helper = _load_scientific_figure_pro()
    if helper is not None:
        helper.apply_publication_style(
            helper.FigureStyle(
                font_size=int(round(font_size)),
                axes_linewidth=axes_linewidth,
                use_tex=False,
            )
        )
        import matplotlib.pyplot as plt

        plt.rcParams.update(
            {
                "axes.facecolor": PUBLICATION_COLORS["background"],
                "figure.facecolor": PUBLICATION_COLORS["background"],
                "savefig.facecolor": PUBLICATION_COLORS["background"],
                "xtick.color": PUBLICATION_COLORS["text"],
                "ytick.color": PUBLICATION_COLORS["text"],
                "text.color": PUBLICATION_COLORS["text"],
                "axes.labelcolor": PUBLICATION_COLORS["text"],
                "axes.edgecolor": "#6B7C88",
                "grid.color": PUBLICATION_COLORS["grid"],
                "grid.linewidth": 0.8,
                "grid.alpha": 0.5,
            }
        )
        return

    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "sans-serif"],
            "font.size": font_size,
            "axes.titlesize": font_size + 1,
            "axes.labelsize": font_size,
            "axes.linewidth": axes_linewidth,
            "axes.facecolor": PUBLICATION_COLORS["background"],
            "figure.facecolor": PUBLICATION_COLORS["background"],
            "savefig.facecolor": PUBLICATION_COLORS["background"],
            "savefig.bbox": "tight",
            "legend.frameon": False,
            "legend.fontsize": font_size - 1,
            "xtick.color": PUBLICATION_COLORS["text"],
            "ytick.color": PUBLICATION_COLORS["text"],
            "text.color": PUBLICATION_COLORS["text"],
            "axes.labelcolor": PUBLICATION_COLORS["text"],
            "axes.edgecolor": "#6B7C88",
            "grid.color": PUBLICATION_COLORS["grid"],
            "grid.linewidth": 0.8,
            "grid.alpha": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def build_single_target_demo_points() -> np.ndarray:
    rng = np.random.default_rng(20260304)
    stem_center = np.array([110.0, -35.0, 350.0])
    stem_points = stem_center + rng.normal(0.0, 1.2, size=(12, 3))
    penetration_noise = np.array(
        [
            [140.0, -20.0, 460.0],
            [90.0, -10.0, 440.0],
            [165.0, -45.0, 480.0],
        ]
    )
    return np.vstack([stem_points, penetration_noise])


def build_multi_target_demo_frames(num_frames: int = 20) -> list[np.ndarray]:
    rng = np.random.default_rng(20260304)
    center_a = MULTI_DEMO_CENTERS["A"]
    center_b = MULTI_DEMO_CENTERS["B"]
    center_c = MULTI_DEMO_CENTERS["C"]
    frames: list[np.ndarray] = []

    for i in range(num_frames):
        p_a = center_a + rng.normal(0.0, 1.0, size=3)
        p_b = center_b + rng.normal(0.0, 1.0, size=3)
        p_c = center_c + rng.normal(0.0, 1.0, size=3)
        if i in (5, 11, 17):
            p_a = p_a + np.array([0.0, 0.0, 95.0])
        if i in (3, 9, 15):
            p_c = p_c + np.array([0.0, 0.0, 95.0])
        frame = np.vstack([p_a, p_b, p_c])
        if i % 2 == 0:
            frame = frame[::-1]
        frames.append(frame)
    return frames


def build_pseudo_target_demo_frames(num_frames: int = 20) -> list[np.ndarray]:
    rng = np.random.default_rng(20260311)
    center_a = MULTI_DEMO_CENTERS["A"]
    center_b = MULTI_DEMO_CENTERS["B"]
    center_c = MULTI_DEMO_CENTERS["C"]
    frames: list[np.ndarray] = []

    for i in range(num_frames):
        p_a = center_a + rng.normal(0.0, 1.0, size=3)
        p_b = center_b + rng.normal(0.0, 1.0, size=3)
        p_c = center_c + rng.normal(0.0, 1.0, size=3)
        frame_points = [p_a, p_b, p_c]

        if i >= 5:
            p_false = PSEUDO_TARGET_CENTER + rng.normal(0.0, 1.0, size=3)
            frame_points.append(p_false)

        frame = np.vstack(frame_points)
        if i % 2 == 0:
            frame = frame[::-1]
        frames.append(frame)

    return frames


def dominant_label(labels: np.ndarray) -> int | None:
    positive = labels[labels > 0]
    if positive.size == 0:
        return None
    values, counts = np.unique(positive, return_counts=True)
    return int(values[int(np.argmax(counts))])


def to_display_points(points: np.ndarray) -> np.ndarray:
    arr = np.asarray(points, dtype=float)
    if arr.size == 0:
        return arr.reshape((-1, 3)) if arr.ndim != 1 else np.empty((0, 3), dtype=float)
    if arr.ndim == 1:
        return arr[[0, 2, 1]]
    return arr[:, [0, 2, 1]]


def to_display_point(point: np.ndarray) -> np.ndarray:
    return np.asarray(point, dtype=float)[[0, 2, 1]]


def publication_display_ranges(mode: str, panel: str) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    ranges = PUBLICATION_FIXED_RANGES[mode][panel]
    return ranges["x"], ranges["z"], ranges["y"]


def publication_axis_labels() -> tuple[str, str, str]:
    return ("X (mm)", "Z (mm)", "Y (mm)")


def draw_box(ax, center: np.ndarray, box_w_mm: float, box_l_mm: float, box_h_mm: float, color: str | None = None) -> None:
    center_disp = to_display_point(center)
    box_x_mm = box_w_mm
    box_y_mm = box_h_mm
    box_z_mm = box_l_mm
    x_min = center_disp[0] - box_x_mm / 2.0
    x_max = center_disp[0] + box_x_mm / 2.0
    y_min = center_disp[1] - box_y_mm / 2.0
    y_max = center_disp[1] + box_y_mm / 2.0
    z_min = center_disp[2] - box_z_mm / 2.0
    z_max = center_disp[2] + box_z_mm / 2.0
    edges = [
        [[x_min, x_min], [y_min, y_min], [z_min, z_max]],
        [[x_max, x_max], [y_min, y_min], [z_min, z_max]],
        [[x_min, x_min], [y_max, y_max], [z_min, z_max]],
        [[x_max, x_max], [y_max, y_max], [z_min, z_max]],
        [[x_min, x_max], [y_max, y_max], [z_min, z_min]],
        [[x_min, x_max], [y_max, y_max], [z_max, z_max]],
        [[x_min, x_max], [y_min, y_min], [z_max, z_max]],
        [[x_min, x_max], [y_min, y_min], [z_min, z_min]],
        [[x_min, x_min], [y_min, y_max], [z_min, z_min]],
        [[x_min, x_min], [y_min, y_max], [z_max, z_max]],
        [[x_max, x_max], [y_min, y_max], [z_min, z_min]],
        [[x_max, x_max], [y_min, y_max], [z_max, z_max]],
    ]
    box_color = PUBLICATION_BOX_STYLE["color"] if color is None else color
    for edge in edges:
        ax.plot3D(
            edge[0],
            edge[1],
            edge[2],
            color=box_color,
            linewidth=PUBLICATION_BOX_STYLE["linewidth"],
            alpha=PUBLICATION_BOX_STYLE["alpha"],
        )


def draw_lines_to_center(ax, points: np.ndarray, center: np.ndarray, color: str, alpha: float = 0.18) -> None:
    points_disp = to_display_points(points)
    center_disp = to_display_point(center)
    for p in points_disp:
        ax.plot3D(
            [p[0], center_disp[0]],
            [p[1], center_disp[1]],
            [p[2], center_disp[2]],
            color=color,
            alpha=alpha,
            linewidth=0.9,
        )


def spread_points(points: np.ndarray, xy_mm: float = 0.35, z_mm: float = 0.12) -> np.ndarray:
    if points.size == 0:
        return points
    idx = np.arange(points.shape[0], dtype=float)
    jitter = np.column_stack(
        [
            np.sin(idx * 1.7) * xy_mm,
            np.cos(idx * 1.3) * xy_mm,
            np.sin(idx * 0.9) * z_mm,
        ]
    )
    return points + jitter


def spread_publication_points(points: np.ndarray) -> np.ndarray:
    return spread_points(points, xy_mm=1.05, z_mm=0.34)


def spread_publication_cluster_points(points: np.ndarray) -> np.ndarray:
    return spread_points(points, xy_mm=2.10, z_mm=0.62)


def fit_box_dims(
    core_points: np.ndarray,
    max_w_mm: float,
    max_l_mm: float,
    max_h_mm: float,
    padding_mm: float = 1.5,
    min_size_mm: float = 3.0,
) -> tuple[float, float, float]:
    if core_points.size == 0:
        return float(max_w_mm), float(max_l_mm), float(max_h_mm)
    ranges = np.ptp(core_points, axis=0)
    dims = np.maximum(ranges + 2.0 * padding_mm, min_size_mm)
    return (
        float(min(max_w_mm, dims[0])),
        float(min(max_l_mm, dims[1])),
        float(min(max_h_mm, dims[2])),
    )


def fit_publication_box_dims(
    core_points: np.ndarray,
    max_w_mm: float,
    max_l_mm: float,
    max_h_mm: float,
) -> tuple[float, float, float]:
    return fit_box_dims(
        core_points,
        max_w_mm=max_w_mm,
        max_l_mm=max_l_mm,
        max_h_mm=max_h_mm,
        padding_mm=2.0,
        min_size_mm=10.0,
    )


def compute_3d_limits(
    points: np.ndarray,
    xy_pad_ratio: float = 0.18,
    z_pad_ratio: float = 0.15,
    min_pad: float = 1.0,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    xpad = (np.max(points[:, 0]) - np.min(points[:, 0])) * xy_pad_ratio + min_pad
    ypad = (np.max(points[:, 1]) - np.min(points[:, 1])) * xy_pad_ratio + min_pad
    zpad = (np.max(points[:, 2]) - np.min(points[:, 2])) * z_pad_ratio + min_pad
    return (
        (float(np.min(points[:, 0]) - xpad), float(np.max(points[:, 0]) + xpad)),
        (float(np.min(points[:, 1]) - ypad), float(np.max(points[:, 1]) + ypad)),
        (float(np.min(points[:, 2]) - zpad), float(np.max(points[:, 2]) + zpad)),
    )


def compute_focus_limits(
    points: np.ndarray,
    center: np.ndarray | None = None,
    min_xy_span_mm: float = 18.0,
    min_z_span_mm: float = 18.0,
    pad_ratio: float = 0.32,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    if points.size == 0:
        if center is None:
            raise ValueError("points or center must be provided")
        points = np.asarray(center, dtype=float).reshape(1, 3)
    else:
        points = np.asarray(points, dtype=float).reshape(-1, 3)

    if center is not None:
        center_arr = np.asarray(center, dtype=float).reshape(1, 3)
        bounds_points = np.vstack([points, center_arr])
    else:
        bounds_points = points

    mins = np.min(bounds_points, axis=0)
    maxs = np.max(bounds_points, axis=0)
    spans = np.maximum(maxs - mins, np.array([min_xy_span_mm, min_xy_span_mm, min_z_span_mm], dtype=float))
    pads = np.maximum(spans * pad_ratio, np.array([1.4, 1.4, 1.2], dtype=float))
    mids = (mins + maxs) / 2.0
    half_spans = spans / 2.0 + pads

    return (
        (float(mids[0] - half_spans[0]), float(mids[0] + half_spans[0])),
        (float(mids[1] - half_spans[1]), float(mids[1] + half_spans[1])),
        (float(mids[2] - half_spans[2]), float(mids[2] + half_spans[2])),
    )


def create_publication_figure_axes(mode: str, figsize: tuple[float, float]) -> tuple[object, dict[str, object]]:
    import matplotlib.pyplot as plt

    mode = mode.strip().lower()
    if mode not in {"single", "multi"}:
        raise ValueError("mode must be 'single' or 'multi'")

    fig = plt.figure(figsize=figsize)
    grid = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.12)
    fig.subplots_adjust(top=0.88, bottom=0.16, left=0.04, right=0.98)
    axes = {
        "raw": fig.add_subplot(grid[0, 0], projection="3d"),
        "cluster": fig.add_subplot(grid[0, 1], projection="3d"),
    }
    return fig, axes


def dedupe_legend(ax, loc: str = "best", bbox_to_anchor=None, ncol: int = 1) -> None:
    handles, labels = ax.get_legend_handles_labels()
    seen: dict[str, object] = {}
    for handle, label in zip(handles, labels):
        if label not in seen:
            seen[label] = handle
    if seen:
        ax.legend(
            list(seen.values()),
            list(seen.keys()),
            loc=loc,
            bbox_to_anchor=bbox_to_anchor,
            handlelength=1.6,
            ncol=ncol,
            columnspacing=0.9,
        )


def style_3d_axis(ax, title: str, xlim, ylim, zlim, elev: float = 20.0, azim: float = -58.0) -> None:
    from matplotlib import colors as mcolors

    xlabel, ylabel, zlabel = publication_axis_labels()
    ax.set_title(title, pad=10.0, weight="semibold")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.set_xlabel(xlabel, labelpad=8.0)
    ax.set_ylabel(ylabel, labelpad=8.0)
    ax.set_zlabel(zlabel, labelpad=8.0)
    ax.view_init(elev=elev, azim=azim)
    ax.set_box_aspect((1.25, 1.0, 0.78))
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis._axinfo["grid"]["color"] = mcolors.to_rgba(PUBLICATION_COLORS["grid"], 0.65)
        axis._axinfo["grid"]["linewidth"] = 0.8
    ax.tick_params(colors=PUBLICATION_COLORS["text"], pad=1.5)


def style_2d_axis(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, pad=8.0, weight="semibold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="both", linestyle="-", alpha=0.35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def add_summary_box(ax, lines: list[str], loc: tuple[float, float] = (0.02, 0.98)) -> None:
    ax.text2D(
        loc[0],
        loc[1],
        "\n".join(lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=10.0,
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": "#F7FAFC",
            "edgecolor": "#C8D4DD",
            "linewidth": 0.9,
        },
    )


def render_multi_observed_axis(
    ax,
    frames: list[np.ndarray],
    frame_idx: int | None = None,
    legend_loc: str = "upper left",
    legend_bbox_to_anchor=None,
    legend_ncol: int = 1,
) -> None:
    xlim, ylim, zlim = publication_display_ranges("multi", "raw")
    if frame_idx is None:
        frame_idx = len(frames) - 1

    shown = np.vstack(frames[: frame_idx + 1])
    shown_disp = to_display_points(spread_publication_points(shown))
    current_frame = to_display_points(spread_publication_points(frames[frame_idx]))
    total_frames = len(frames)

    ax.scatter(
        shown_disp[:, 0],
        shown_disp[:, 1],
        shown_disp[:, 2],
        c=PUBLICATION_COLORS["history"],
        s=14,
        alpha=0.22,
        label="Detection history",
    )
    ax.scatter(
        current_frame[:, 0],
        current_frame[:, 1],
        current_frame[:, 2],
        c=PUBLICATION_COLORS["current"],
        s=54,
        alpha=0.94,
        edgecolors="#0A2D57",
        linewidths=0.6,
        label="Current detections",
    )
    style_3d_axis(ax, f"Observed Detections (frame {frame_idx + 1}/{total_frames})", xlim, ylim, zlim)
    dedupe_legend(ax, loc=legend_loc, bbox_to_anchor=legend_bbox_to_anchor, ncol=legend_ncol)


def render_multi_tracking_axis(
    ax,
    state: dict[int, TrackSnapshot],
    window_size: int,
    eps_mm: float,
    min_pts: int,
    association_dist_thresh_mm: float,
    max_missed_frames: int,
    box_w_mm: float,
    box_l_mm: float,
    box_h_mm: float,
    include_summary: bool = True,
    legend_loc: str = "upper left",
    legend_bbox_to_anchor=None,
    legend_ncol: int = 1,
    title: str | None = "DBSCAN Track Consolidation",
) -> None:
    cluster_xlim, cluster_ylim, cluster_zlim = publication_display_ranges("multi", "cluster")
    locked_count = 0
    active_count = 0
    total_core_points = 0
    total_noise_points = 0
    overlay_noise_groups: list[tuple[np.ndarray, float]] = []

    for idx, track_id in enumerate(sorted(state.keys())):
        snapshot = state[track_id]
        color = TRACK_COLORS[(track_id - 1) % len(TRACK_COLORS)]
        alpha_scale = 1.0 if snapshot.active else 0.5

        history_points_plot = spread_publication_points(snapshot.history)
        history_points = to_display_points(history_points_plot)
        if history_points.size > 0:
            ax.scatter(
                history_points[:, 0],
                history_points[:, 1],
                history_points[:, 2],
                c=color,
                s=20 if snapshot.active else 16,
                alpha=0.26 * alpha_scale,
                label="Track history" if idx == 0 else None,
            )

        window_points = snapshot.window
        window_points_plot = spread_publication_cluster_points(window_points)
        window_points_disp = to_display_points(window_points_plot)
        labels = snapshot.labels if snapshot.labels.size == len(window_points) else np.full(len(window_points), -1, dtype=int)
        core_mask = labels > 0
        noise_mask = labels == -1
        if window_points_disp.size > 0:
            ax.scatter(
                window_points_disp[:, 0],
                window_points_disp[:, 1],
                window_points_disp[:, 2],
                c="#CFD8DF",
                s=PUBLICATION_MARKER_SIZES["window_points"],
                alpha=0.18,
            )
        if np.any(core_mask):
            ax.scatter(
                window_points_disp[core_mask, 0],
                window_points_disp[core_mask, 1],
                window_points_disp[core_mask, 2],
                c=color,
                s=PUBLICATION_MARKER_SIZES["cluster_core"],
                alpha=0.94 * alpha_scale,
                marker="x",
                linewidths=1.1,
                label="Core points" if idx == 0 else None,
            )
            total_core_points += int(np.sum(core_mask))
        if np.any(noise_mask):
            overlay_noise_groups.append((window_points_disp[noise_mask].copy(), alpha_scale))
            total_noise_points += int(np.sum(noise_mask))

        if snapshot.center is not None:
            center_disp = to_display_point(snapshot.center)
            ax.scatter(
                center_disp[0],
                center_disp[1],
                center_disp[2],
                c=color,
                marker="*",
                s=PUBLICATION_MARKER_SIZES["center"],
                edgecolors=PUBLICATION_BOX_STYLE["color"],
                linewidths=1.0,
                label="Track center" if idx == 0 else None,
            )
            if np.any(core_mask):
                draw_lines_to_center(ax, window_points_plot[core_mask], snapshot.center, color=color, alpha=0.16)
            box_w_cur, box_l_cur, box_h_cur = fit_publication_box_dims(
                window_points[core_mask] if np.any(core_mask) else np.empty((0, 3)),
                max_w_mm=box_w_mm,
                max_l_mm=box_l_mm,
                max_h_mm=box_h_mm,
            )
            draw_box(ax, snapshot.center, box_w_cur, box_l_cur, box_h_cur)

        if snapshot.locked:
            locked_count += 1
        if snapshot.active:
            active_count += 1

    for idx, (noise_points, alpha_scale) in enumerate(overlay_noise_groups):
        ax.scatter(
            noise_points[:, 0],
            noise_points[:, 1],
            noise_points[:, 2],
            c=PUBLICATION_COLORS["noise"],
            s=max(18, PUBLICATION_MARKER_SIZES["cluster_noise"]),
            alpha=0.95 * alpha_scale,
            marker="x",
            linewidths=1.2,
            depthshade=False,
            label="Noise points" if idx == 0 else None,
        )

    style_3d_axis(ax, title or "", cluster_xlim, cluster_ylim, cluster_zlim)
    if include_summary:
        add_summary_box(
            ax,
            [
                f"observed tracks={len(state)}  active={active_count}  locked={locked_count}",
                f"N={window_size}  eps={eps_mm:.1f} mm  MinPts={min_pts}",
                f"assoc={association_dist_thresh_mm:.1f} mm  max_missed={max_missed_frames}",
                f"core points={total_core_points}  noise points={total_noise_points}",
            ],
            loc=(0.55, 0.96),
        )
    dedupe_legend(ax, loc=legend_loc, bbox_to_anchor=legend_bbox_to_anchor, ncol=legend_ncol)


def _snapshot_track(track_id: int, history: dict[int, list[np.ndarray]], state, active: bool) -> TrackSnapshot:
    result = state.last_result
    return TrackSnapshot(
        track_id=int(track_id),
        history=np.vstack(history[track_id]).copy() if track_id in history else np.empty((0, 3), dtype=float),
        window=state.filter_obj.get_window_points().copy(),
        labels=result.labels.copy(),
        center=None if result.p_final is None else result.p_final.copy(),
        locked=bool(result.locked),
        core_size=int(result.core_size),
        sigma=float("nan") if result.sigma_mm is None else float(result.sigma_mm),
        reason=result.reason,
        last_observation=state.last_observation.copy(),
        age=int(state.age),
        missed_frames=int(state.missed_frames),
        active=active,
    )


def collect_multi_target_snapshots(
    frames: list[np.ndarray],
    window_size: int,
    eps_mm: float,
    min_pts: int,
    sigma_thresh_mm: float,
    association_dist_thresh_mm: float,
    max_missed_frames: int,
) -> tuple[list[dict[int, TrackSnapshot]], dict[int, TrackSnapshot]]:
    tracker = MultiTargetDBSCANTracker(
        window_size=window_size,
        eps_mm=eps_mm,
        min_pts=min_pts,
        sigma_thresh_mm=sigma_thresh_mm,
        association_dist_thresh_mm=association_dist_thresh_mm,
        max_missed_frames=max_missed_frames,
    )

    history: dict[int, list[np.ndarray]] = {}
    snapshots: list[dict[int, TrackSnapshot]] = []
    latest: dict[int, TrackSnapshot] = {}

    for frame_points in frames:
        outputs = tracker.update(frame_points)
        for track_id, out in outputs.items():
            history.setdefault(track_id, []).append(out.observation.copy())

        active_tracks = tracker.get_tracks()
        frame_state: dict[int, TrackSnapshot] = {}
        for track_id, state in active_tracks.items():
            snapshot = _snapshot_track(track_id, history, state, active=True)
            frame_state[track_id] = snapshot
            latest[track_id] = snapshot

        active_ids = set(active_tracks.keys())
        for track_id in list(latest.keys()):
            if track_id not in active_ids and latest[track_id].active:
                latest[track_id] = replace(latest[track_id], active=False)

        snapshots.append(frame_state)

    return snapshots, latest


def freeze_locked_multi_snapshots(snapshots: list[dict[int, TrackSnapshot]]) -> list[dict[int, TrackSnapshot]]:
    frozen_by_track: dict[int, TrackSnapshot] = {}
    frozen_frames: list[dict[int, TrackSnapshot]] = []

    for frame_state in snapshots:
        frozen_state: dict[int, TrackSnapshot] = {}
        for track_id, snapshot in frame_state.items():
            if track_id not in frozen_by_track and snapshot.locked:
                frozen_by_track[track_id] = snapshot

            if track_id in frozen_by_track:
                frozen_snapshot = frozen_by_track[track_id]
                frozen_state[track_id] = replace(
                    frozen_snapshot,
                    active=snapshot.active,
                    missed_frames=snapshot.missed_frames,
                    age=snapshot.age,
                    last_observation=snapshot.last_observation.copy(),
                )
            else:
                frozen_state[track_id] = snapshot
        frozen_frames.append(frozen_state)

    return frozen_frames
