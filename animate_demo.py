from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
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


def precompute(points: np.ndarray, window_size: int, eps_mm: float, min_pts: int, sigma_thresh_mm: float):
    filt = MultiFrameDBSCANFilter(
        window_size=window_size,
        eps_mm=eps_mm,
        min_pts=min_pts,
        sigma_thresh_mm=sigma_thresh_mm,
    )
    results = []
    windows = []
    for p in points:
        result = filt.add_observation(p)
        results.append(result)
        windows.append(filt.get_window_points().copy())
    return results, windows


def make_animation(
    points: np.ndarray,
    output_path: Path,
    window_size: int,
    eps_mm: float,
    min_pts: int,
    sigma_thresh_mm: float,
    box_w_mm: float,
    box_l_mm: float,
    box_h_mm: float,
    fps: int,
) -> None:
    apply_publication_style(font_size=12.0, axes_linewidth=1.2)
    results, windows = precompute(
        points=points,
        window_size=window_size,
        eps_mm=eps_mm,
        min_pts=min_pts,
        sigma_thresh_mm=sigma_thresh_mm,
    )
    xlim, ylim, zlim = publication_display_ranges("single", "raw")
    cluster_xlim, cluster_ylim, cluster_zlim = publication_display_ranges("single", "cluster")

    fig, axes = create_publication_figure_axes(mode="single", figsize=(14.4, 6.8))
    ax_raw = axes["raw"]
    ax_cluster = axes["cluster"]

    def update(frame_idx: int):
        ax_raw.cla()
        ax_cluster.cla()

        shown = points[: frame_idx + 1]
        shown_disp = to_display_points(spread_publication_points(shown))
        current_point = shown_disp[-1]
        previous_points = shown_disp[:-1]
        if previous_points.size > 0:
            ax_raw.scatter(
                previous_points[:, 0],
                previous_points[:, 1],
                previous_points[:, 2],
                c=PUBLICATION_COLORS["history"],
                s=14,
                alpha=0.28,
                label="Observed history",
            )
        ax_raw.scatter(
            current_point[0],
            current_point[1],
            current_point[2],
            c=PUBLICATION_COLORS["current"],
            s=52,
            alpha=0.96,
            edgecolors="#0A2D57",
            linewidths=0.7,
            label="Current observation",
        )
        style_3d_axis(ax_raw, "Observed 3D Points", xlim, ylim, zlim)
        dedupe_legend(ax_raw, loc="upper left", bbox_to_anchor=(0.0, -0.06))

        result = results[frame_idx]
        window_points = windows[frame_idx]
        window_points_plot = spread_publication_cluster_points(window_points)
        window_points_disp = to_display_points(window_points_plot)
        labels = result.labels if result.labels.size == len(window_points) else np.full(len(window_points), -1, dtype=int)
        dom = dominant_label(labels) if labels.size > 0 else None
        dominant_mask = labels == dom if dom is not None else np.zeros_like(labels, dtype=bool)
        noise_mask = labels == -1
        other_mask = ~(dominant_mask | noise_mask)
        if window_points_disp.size > 0:
            ax_cluster.scatter(
                window_points_disp[:, 0],
                window_points_disp[:, 1],
                window_points_disp[:, 2],
                c="#B8C7D3",
                s=PUBLICATION_MARKER_SIZES["window_points"],
                alpha=0.35,
                label="Window observations",
            )
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
                alpha=0.72,
                marker="x",
                linewidths=0.95,
                label="Other clusters",
            )

        summary_lines = [
            f"frame={frame_idx + 1}/{len(points)}",
            f"N={window_size}  eps={eps_mm:.1f} mm  MinPts={min_pts}",
            f"locked={result.locked}  reason={result.reason}",
        ]
        if result.p_final is not None:
            center_disp = to_display_point(result.p_final)
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
            if np.any(dominant_mask):
                draw_lines_to_center(ax_cluster, window_points_plot[dominant_mask], result.p_final, color=PUBLICATION_COLORS["core"])
            box_w_cur, box_l_cur, box_h_cur = fit_publication_box_dims(
                window_points[dominant_mask] if np.any(dominant_mask) else np.empty((0, 3)),
                max_w_mm=box_w_mm,
                max_l_mm=box_l_mm,
                max_h_mm=box_h_mm,
            )
            draw_box(ax_cluster, result.p_final, box_w_cur, box_l_cur, box_h_cur)
            summary_lines.append(f"core={result.core_size}  sigma={result.sigma_mm:.2f} mm")
        else:
            summary_lines.append("core=0  sigma=NA")

        style_3d_axis(ax_cluster, "DBSCAN Window Result", cluster_xlim, cluster_ylim, cluster_zlim)
        add_summary_box(ax_cluster, summary_lines, loc=(0.58, 0.96))
        dedupe_legend(ax_cluster, loc="upper left", bbox_to_anchor=(0.0, -0.06))

        fig.suptitle("Single-Target DBSCAN Filtering", y=0.96, fontsize=14, weight="bold")

    ani = animation.FuncAnimation(fig, update, frames=len(points), interval=max(1, int(1000 / max(1, fps))), repeat=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = animation.PillowWriter(fps=fps)
    ani.save(output_path, writer=writer, dpi=180)
    plt.close(fig)
    print(f"GIF saved to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate frame-by-frame GIF for single-target DBSCAN filtering.")
    parser.add_argument("--output", default="DBSCAN/output/dbscan_multiframe_animation.gif", help="Output GIF path")
    parser.add_argument("--window-size", type=int, default=15)
    parser.add_argument("--eps-mm", type=float, default=15.0)
    parser.add_argument("--min-pts", type=int, default=8)
    parser.add_argument("--sigma-thresh-mm", type=float, default=3.0)
    parser.add_argument("--box-w-mm", type=float, default=30.0)
    parser.add_argument("--box-l-mm", type=float, default=30.0)
    parser.add_argument("--box-h-mm", type=float, default=30.0)
    parser.add_argument("--fps", type=int, default=3, help="GIF frame rate")
    args = parser.parse_args()

    points = build_single_target_demo_points()
    make_animation(
        points=points,
        output_path=Path(args.output),
        window_size=args.window_size,
        eps_mm=args.eps_mm,
        min_pts=args.min_pts,
        sigma_thresh_mm=args.sigma_thresh_mm,
        box_w_mm=args.box_w_mm,
        box_l_mm=args.box_l_mm,
        box_h_mm=args.box_h_mm,
        fps=args.fps,
    )


if __name__ == "__main__":
    main()
