from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from DBSCAN.multiframe_dbscan_filter import MultiFrameDBSCANFilter
    from DBSCAN.viz_utils import (
        PUBLICATION_COLORS,
        PUBLICATION_BOX_STYLE,
        PUBLICATION_FIXED_RANGES,
        add_summary_box,
        apply_publication_style,
        build_single_target_demo_points,
        create_publication_figure_axes,
        dedupe_legend,
        dominant_label,
        draw_box,
        draw_lines_to_center,
        fit_publication_box_dims,
        PUBLICATION_MARKER_SIZES,
        publication_display_ranges,
        spread_publication_cluster_points,
        spread_publication_points,
        style_3d_axis,
        to_display_point,
        to_display_points,
    )
except ModuleNotFoundError:
    from multiframe_dbscan_filter import MultiFrameDBSCANFilter
    from viz_utils import (
        PUBLICATION_COLORS,
        PUBLICATION_BOX_STYLE,
        PUBLICATION_FIXED_RANGES,
        add_summary_box,
        apply_publication_style,
        build_single_target_demo_points,
        create_publication_figure_axes,
        dedupe_legend,
        dominant_label,
        draw_box,
        draw_lines_to_center,
        fit_publication_box_dims,
        PUBLICATION_MARKER_SIZES,
        publication_display_ranges,
        spread_publication_cluster_points,
        spread_publication_points,
        style_3d_axis,
        to_display_point,
        to_display_points,
    )


def read_txt_points(txt_path: Path) -> np.ndarray:
    """Read points from text lines like: [x, y, z]."""
    pattern = re.compile(
        r"\[\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*"
        r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*"
        r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*\]"
    )
    points = []
    with txt_path.open("r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if not match:
                continue
            points.append([float(match.group(1)), float(match.group(2)), float(match.group(3))])
    if not points:
        raise ValueError(f"No valid [x, y, z] points found in {txt_path}")
    return np.asarray(points, dtype=float)


def _points_in_box(
    points: np.ndarray,
    center: np.ndarray,
    box_w_mm: float,
    box_l_mm: float,
    box_h_mm: float,
) -> np.ndarray:
    x_min = center[0] - box_w_mm / 2.0
    x_max = center[0] + box_w_mm / 2.0
    y_min = center[1] - box_l_mm / 2.0
    y_max = center[1] + box_l_mm / 2.0
    z_min = center[2] - box_h_mm / 2.0
    z_max = center[2] + box_h_mm / 2.0
    return (
        (points[:, 0] >= x_min)
        & (points[:, 0] <= x_max)
        & (points[:, 1] >= y_min)
        & (points[:, 1] <= y_max)
        & (points[:, 2] >= z_min)
        & (points[:, 2] <= z_max)
    )


def run_and_plot(
    points: np.ndarray,
    output_path: Path,
    window_size: int,
    eps_mm: float,
    min_pts: int,
    sigma_thresh_mm: float,
    box_w_mm: float,
    box_l_mm: float,
    box_h_mm: float,
) -> None:
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must be an array with shape [N, 3]")

    apply_publication_style(font_size=12.0, axes_linewidth=1.2)

    filt = MultiFrameDBSCANFilter(
        window_size=window_size,
        eps_mm=eps_mm,
        min_pts=min_pts,
        sigma_thresh_mm=sigma_thresh_mm,
    )
    results = [filt.add_observation(p) for p in points]
    final = results[-1]
    window_points = points[-window_size:] if points.shape[0] >= window_size else points
    points_disp = to_display_points(spread_publication_points(points))
    window_points_plot = spread_publication_cluster_points(window_points)
    window_points_disp = to_display_points(window_points_plot)
    labels = final.labels if final.labels.size == len(window_points) else np.full(len(window_points), -1, dtype=int)
    dominant = dominant_label(labels)
    xlim, ylim, zlim = publication_display_ranges("single", "raw")
    cluster_xlim, cluster_ylim, cluster_zlim = publication_display_ranges("single", "cluster")

    fig, axes = create_publication_figure_axes(mode="single", figsize=(14.4, 6.8))
    ax_raw = axes["raw"]
    ax_cluster = axes["cluster"]

    recent_count = min(window_size, len(points))
    earlier_points = points_disp[:-recent_count] if len(points) > recent_count else np.empty((0, 3))
    recent_points = points_disp[-recent_count:]
    if earlier_points.size > 0:
        ax_raw.scatter(
            earlier_points[:, 0],
            earlier_points[:, 1],
            earlier_points[:, 2],
            c=PUBLICATION_COLORS["history"],
            s=14,
            alpha=0.32,
            label="Earlier observations",
        )
    ax_raw.scatter(
        recent_points[:, 0],
        recent_points[:, 1],
        recent_points[:, 2],
        c=PUBLICATION_COLORS["current"],
        s=26,
        alpha=0.82,
        label=f"Last {recent_count} observations",
    )
    style_3d_axis(ax_raw, "Observed 3D Points", xlim, ylim, zlim)
    dedupe_legend(ax_raw, loc="upper left", bbox_to_anchor=(0.0, -0.06))

    ax_cluster.scatter(
        window_points_disp[:, 0],
        window_points_disp[:, 1],
        window_points_disp[:, 2],
        c="#B8C7D3",
        s=PUBLICATION_MARKER_SIZES["window_points"],
        alpha=0.38,
        label="Window observations",
    )

    noise_mask = labels == -1
    dominant_mask = labels == dominant if dominant is not None else np.zeros_like(labels, dtype=bool)
    other_mask = ~(noise_mask | dominant_mask)
    if np.any(dominant_mask):
        ax_cluster.scatter(
            window_points_disp[dominant_mask, 0],
            window_points_disp[dominant_mask, 1],
            window_points_disp[dominant_mask, 2],
            c=PUBLICATION_COLORS["core"],
            s=PUBLICATION_MARKER_SIZES["cluster_core"],
            alpha=0.95,
            marker="x",
            linewidths=1.15,
            label="Dominant core cluster",
        )
    if np.any(noise_mask):
        ax_cluster.scatter(
            window_points_disp[noise_mask, 0],
            window_points_disp[noise_mask, 1],
            window_points_disp[noise_mask, 2],
            c=PUBLICATION_COLORS["noise"],
            s=PUBLICATION_MARKER_SIZES["cluster_noise"],
            alpha=0.88,
            marker="x",
            linewidths=0.95,
            label="Outliers / noise",
        )
    if np.any(other_mask):
        ax_cluster.scatter(
            window_points_disp[other_mask, 0],
            window_points_disp[other_mask, 1],
            window_points_disp[other_mask, 2],
            c="#5F8FB5",
            s=PUBLICATION_MARKER_SIZES["cluster_other"],
            alpha=0.75,
            marker="x",
            linewidths=0.95,
            label="Other clusters",
        )

    in_box_num = 0
    rate = float("nan")
    summary_lines = [
        f"N={window_size}  eps={eps_mm:.1f} mm  MinPts={min_pts}",
        f"locked={final.locked}  reason={final.reason}",
    ]
    if final.p_final is not None:
        center_disp = to_display_point(final.p_final)
        ax_cluster.scatter(
            center_disp[0],
            center_disp[1],
            center_disp[2],
            c=PUBLICATION_COLORS["center"],
            s=PUBLICATION_MARKER_SIZES["center"],
            marker="*",
            edgecolors=PUBLICATION_BOX_STYLE["color"],
            linewidths=1.0,
            label=r"Final center $P_{final}$",
        )
        core_points_for_lines = window_points_plot[dominant_mask] if np.any(dominant_mask) else np.empty((0, 3))
        core_points_for_box = window_points[dominant_mask] if np.any(dominant_mask) else np.empty((0, 3))
        if core_points_for_lines.size > 0:
            draw_lines_to_center(ax_cluster, core_points_for_lines, final.p_final, color=PUBLICATION_COLORS["core"])
        box_w_cur, box_l_cur, box_h_cur = fit_publication_box_dims(
            core_points_for_box,
            max_w_mm=box_w_mm,
            max_l_mm=box_l_mm,
            max_h_mm=box_h_mm,
        )
        draw_box(ax_cluster, final.p_final, box_w_cur, box_l_cur, box_h_cur)
        box_mask = _points_in_box(
            window_points,
            final.p_final,
            box_w_mm=box_w_cur,
            box_l_mm=box_l_cur,
            box_h_mm=box_h_cur,
        )
        in_box_num = int(np.sum(box_mask))
        rate = float(in_box_num) / float(len(window_points))
        summary_lines.append(f"core={final.core_size}  sigma={final.sigma_mm:.2f} mm")
        summary_lines.append(f"box occupancy={in_box_num}/{len(window_points)} ({rate:.2%})")
    else:
        summary_lines.append("core=0  sigma=NA")

    style_3d_axis(ax_cluster, "DBSCAN Window Result", cluster_xlim, cluster_ylim, cluster_zlim)
    add_summary_box(ax_cluster, summary_lines, loc=(0.58, 0.96))
    dedupe_legend(ax_cluster, loc="upper left", bbox_to_anchor=(0.0, -0.06))

    fig.suptitle("Single-Target DBSCAN Filtering", y=0.96, fontsize=14, weight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    print(f"Visualization saved to: {output_path}")
    if final.p_final is not None:
        x, y, z = final.p_final
        print(
            f"Center(mm)=({x:.3f}, {y:.3f}, {z:.3f}), "
            f"core_size={final.core_size}, sigma={final.sigma_mm:.3f}, "
            f"in_box={in_box_num}/{len(window_points)} ({rate:.3f})"
        )
    else:
        print(f"No converged center yet. reason={final.reason}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize multi-frame DBSCAN filtering result.")
    parser.add_argument(
        "--txt",
        default=None,
        help="Optional input txt file with lines containing [x, y, z]. If omitted, synthetic demo points are used.",
    )
    parser.add_argument("--output", default="DBSCAN/output/dbscan_multiframe_demo.png", help="Output image path")
    parser.add_argument("--window-size", type=int, default=15, help="Sliding window size")
    parser.add_argument("--eps-mm", type=float, default=15.0, help="DBSCAN eps in millimeters")
    parser.add_argument("--min-pts", type=int, default=8, help="DBSCAN minimum points")
    parser.add_argument("--sigma-thresh-mm", type=float, default=3.0, help="Lock sigma threshold in millimeters")
    parser.add_argument("--box-w-mm", type=float, default=30.0, help="Visualization box width in millimeters")
    parser.add_argument("--box-l-mm", type=float, default=30.0, help="Visualization box length in millimeters")
    parser.add_argument("--box-h-mm", type=float, default=30.0, help="Visualization box height in millimeters")
    args = parser.parse_args()

    if args.txt:
        points = read_txt_points(Path(args.txt))
    else:
        points = build_single_target_demo_points()

    run_and_plot(
        points=points,
        output_path=Path(args.output),
        window_size=args.window_size,
        eps_mm=args.eps_mm,
        min_pts=args.min_pts,
        sigma_thresh_mm=args.sigma_thresh_mm,
        box_w_mm=args.box_w_mm,
        box_l_mm=args.box_l_mm,
        box_h_mm=args.box_h_mm,
    )


if __name__ == "__main__":
    main()
