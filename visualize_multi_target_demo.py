from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from DBSCAN.viz_utils import (
        PUBLICATION_COLORS,
        PUBLICATION_BOX_STYLE,
        apply_publication_style,
        build_multi_target_demo_frames,
        collect_multi_target_snapshots,
        create_publication_figure_axes,
        dedupe_legend,
        render_multi_observed_axis,
        render_multi_tracking_axis,
        style_3d_axis,
    )
except ModuleNotFoundError:
    from viz_utils import (
        PUBLICATION_COLORS,
        PUBLICATION_BOX_STYLE,
        apply_publication_style,
        build_multi_target_demo_frames,
        collect_multi_target_snapshots,
        create_publication_figure_axes,
        dedupe_legend,
        render_multi_observed_axis,
        render_multi_tracking_axis,
        style_3d_axis,
    )


def export_single_panel_publication_pngs(
    output_dir: Path,
    box_w_mm: float = 30.0,
    box_l_mm: float = 30.0,
    box_h_mm: float = 30.0,
    window_size: int = 15,
    eps_mm: float = 15.0,
    min_pts: int = 8,
    sigma_thresh_mm: float = 3.0,
    association_dist_thresh_mm: float = 80.0,
    max_missed_frames: int = 3,
) -> None:
    apply_publication_style(font_size=12.0, axes_linewidth=1.2)

    frames = build_multi_target_demo_frames()
    _, latest = collect_multi_target_snapshots(
        frames=frames,
        window_size=window_size,
        eps_mm=eps_mm,
        min_pts=min_pts,
        sigma_thresh_mm=sigma_thresh_mm,
        association_dist_thresh_mm=association_dist_thresh_mm,
        max_missed_frames=max_missed_frames,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    prev_bbox = plt.rcParams.get("savefig.bbox")
    plt.rcParams["savefig.bbox"] = None

    try:
        fig_observed = plt.figure(figsize=(7.2, 7.2))
        ax_observed = fig_observed.add_subplot(111, projection="3d")
        fig_observed.subplots_adjust(top=0.88, bottom=0.20, left=0.04, right=0.96)
        render_multi_observed_axis(
            ax_observed,
            frames=frames,
            frame_idx=len(frames) - 1,
            legend_loc="upper center",
            legend_bbox_to_anchor=(0.5, -0.08),
            legend_ncol=2,
        )
        fig_observed.suptitle("Observed Multi-target Detections", y=0.96, fontsize=14, weight="bold")
        fig_observed.savefig(output_dir / "publication_multi_observed.png", dpi=300, bbox_inches=None)
        plt.close(fig_observed)

        fig_tracking = plt.figure(figsize=(7.2, 7.2))
        ax_tracking = fig_tracking.add_subplot(111, projection="3d")
        fig_tracking.subplots_adjust(top=0.88, bottom=0.24, left=0.04, right=0.96)
        render_multi_tracking_axis(
            ax_tracking,
            state=latest,
            window_size=window_size,
            eps_mm=eps_mm,
            min_pts=min_pts,
            association_dist_thresh_mm=association_dist_thresh_mm,
            max_missed_frames=max_missed_frames,
            box_w_mm=box_w_mm,
            box_l_mm=box_l_mm,
            box_h_mm=box_h_mm,
            include_summary=False,
            legend_loc="upper center",
            legend_bbox_to_anchor=(0.5, -0.10),
            legend_ncol=2,
            title=None,
        )
        fig_tracking.suptitle("DBSCAN Track Consolidation", y=0.96, fontsize=14, weight="bold")
        fig_tracking.savefig(output_dir / "publication_multi_tracking.png", dpi=300, bbox_inches=None)
        plt.close(fig_tracking)
    finally:
        plt.rcParams["savefig.bbox"] = prev_bbox


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize multi-target DBSCAN tracking result.")
    parser.add_argument("--output", default="DBSCAN/output/multi_target_tracker_demo.png", help="Output image path")
    parser.add_argument("--box-w-mm", type=float, default=30.0)
    parser.add_argument("--box-l-mm", type=float, default=30.0)
    parser.add_argument("--box-h-mm", type=float, default=30.0)
    parser.add_argument("--window-size", type=int, default=15)
    parser.add_argument("--eps-mm", type=float, default=15.0)
    parser.add_argument("--min-pts", type=int, default=8)
    parser.add_argument("--sigma-thresh-mm", type=float, default=3.0)
    parser.add_argument("--association-dist-thresh-mm", type=float, default=80.0)
    parser.add_argument("--max-missed-frames", type=int, default=3)
    args = parser.parse_args()

    apply_publication_style(font_size=12.0, axes_linewidth=1.2)

    frames = build_multi_target_demo_frames()
    _, latest = collect_multi_target_snapshots(
        frames=frames,
        window_size=args.window_size,
        eps_mm=args.eps_mm,
        min_pts=args.min_pts,
        sigma_thresh_mm=args.sigma_thresh_mm,
        association_dist_thresh_mm=args.association_dist_thresh_mm,
        max_missed_frames=args.max_missed_frames,
    )

    fig, axes = create_publication_figure_axes(mode="multi", figsize=(14.4, 6.8))
    ax_raw = axes["raw"]
    ax_cluster = axes["cluster"]
    render_multi_observed_axis(ax_raw, frames=frames, frame_idx=len(frames) - 1)
    render_multi_tracking_axis(
        ax_cluster,
        state=latest,
        window_size=args.window_size,
        eps_mm=args.eps_mm,
        min_pts=args.min_pts,
        association_dist_thresh_mm=args.association_dist_thresh_mm,
        max_missed_frames=args.max_missed_frames,
        box_w_mm=args.box_w_mm,
        box_l_mm=args.box_l_mm,
        box_h_mm=args.box_h_mm,
    )

    fig.suptitle("Multi-target DBSCAN Tracking", y=0.96, fontsize=14, weight="bold")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    print(f"Visualization saved to: {output_path}")


if __name__ == "__main__":
    main()
