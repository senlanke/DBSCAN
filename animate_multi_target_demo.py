from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

try:
    from DBSCAN.viz_utils import (
        apply_publication_style,
        build_multi_target_demo_frames,
        collect_multi_target_snapshots,
        create_publication_figure_axes,
        freeze_locked_multi_snapshots,
        render_multi_observed_axis,
        render_multi_tracking_axis,
    )
except ModuleNotFoundError:
    from viz_utils import (
        apply_publication_style,
        build_multi_target_demo_frames,
        collect_multi_target_snapshots,
        create_publication_figure_axes,
        freeze_locked_multi_snapshots,
        render_multi_observed_axis,
        render_multi_tracking_axis,
    )


def export_single_panel_publication_gifs(
    output_dir: Path,
    fps: int = 3,
    window_size: int = 15,
    eps_mm: float = 15.0,
    min_pts: int = 8,
    sigma_thresh_mm: float = 3.0,
    association_dist_thresh_mm: float = 80.0,
    max_missed_frames: int = 3,
    box_w_mm: float = 30.0,
    box_l_mm: float = 30.0,
    box_h_mm: float = 30.0,
) -> None:
    apply_publication_style(font_size=12.0, axes_linewidth=1.2)

    frames = build_multi_target_demo_frames()
    snapshots, _ = collect_multi_target_snapshots(
        frames=frames,
        window_size=window_size,
        eps_mm=eps_mm,
        min_pts=min_pts,
        sigma_thresh_mm=sigma_thresh_mm,
        association_dist_thresh_mm=association_dist_thresh_mm,
        max_missed_frames=max_missed_frames,
    )
    frozen_snapshots = freeze_locked_multi_snapshots(snapshots)
    output_dir.mkdir(parents=True, exist_ok=True)
    prev_bbox = plt.rcParams.get("savefig.bbox")
    plt.rcParams["savefig.bbox"] = None

    try:
        fig_observed = plt.figure(figsize=(7.2, 7.2))
        ax_observed = fig_observed.add_subplot(111, projection="3d")
        fig_observed.subplots_adjust(top=0.88, bottom=0.20, left=0.04, right=0.96)

        def update_observed(frame_idx: int):
            ax_observed.cla()
            render_multi_observed_axis(
                ax_observed,
                frames=frames,
                frame_idx=frame_idx,
                legend_loc="upper center",
                legend_bbox_to_anchor=(0.5, -0.08),
                legend_ncol=2,
            )
            fig_observed.suptitle("Observed Multi-target Detections", y=0.96, fontsize=14, weight="bold")

        ani_observed = animation.FuncAnimation(
            fig_observed,
            update_observed,
            frames=len(frames),
            interval=max(1, int(1000 / max(1, fps))),
            repeat=False,
        )
        ani_observed.save(
            output_dir / "publication_multi_observed.gif",
            writer=animation.PillowWriter(fps=fps),
            dpi=180,
            savefig_kwargs={"bbox_inches": None},
        )
        plt.close(fig_observed)

        fig_tracking = plt.figure(figsize=(7.2, 7.2))
        ax_tracking = fig_tracking.add_subplot(111, projection="3d")
        fig_tracking.subplots_adjust(top=0.88, bottom=0.24, left=0.04, right=0.96)

        def update_tracking(frame_idx: int):
            ax_tracking.cla()
            render_multi_tracking_axis(
                ax_tracking,
                state=frozen_snapshots[frame_idx],
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

        ani_tracking = animation.FuncAnimation(
            fig_tracking,
            update_tracking,
            frames=len(frames),
            interval=max(1, int(1000 / max(1, fps))),
            repeat=False,
        )
        ani_tracking.save(
            output_dir / "publication_multi_tracking.gif",
            writer=animation.PillowWriter(fps=fps),
            dpi=180,
            savefig_kwargs={"bbox_inches": None},
        )
        plt.close(fig_tracking)
    finally:
        plt.rcParams["savefig.bbox"] = prev_bbox


def make_animation(
    output_path: Path,
    fps: int,
    window_size: int,
    eps_mm: float,
    min_pts: int,
    sigma_thresh_mm: float,
    association_dist_thresh_mm: float,
    max_missed_frames: int,
    box_w_mm: float,
    box_l_mm: float,
    box_h_mm: float,
) -> None:
    apply_publication_style(font_size=12.0, axes_linewidth=1.2)

    frames = build_multi_target_demo_frames()
    snapshots, _ = collect_multi_target_snapshots(
        frames=frames,
        window_size=window_size,
        eps_mm=eps_mm,
        min_pts=min_pts,
        sigma_thresh_mm=sigma_thresh_mm,
        association_dist_thresh_mm=association_dist_thresh_mm,
        max_missed_frames=max_missed_frames,
    )
    frozen_snapshots = freeze_locked_multi_snapshots(snapshots)

    fig, axes = create_publication_figure_axes(mode="multi", figsize=(14.4, 6.8))
    ax_left = axes["raw"]
    ax_right = axes["cluster"]

    def update(frame_idx: int):
        ax_left.cla()
        ax_right.cla()
        render_multi_observed_axis(ax_left, frames=frames, frame_idx=frame_idx)
        render_multi_tracking_axis(
            ax_right,
            state=frozen_snapshots[frame_idx],
            window_size=window_size,
            eps_mm=eps_mm,
            min_pts=min_pts,
            association_dist_thresh_mm=association_dist_thresh_mm,
            max_missed_frames=max_missed_frames,
            box_w_mm=box_w_mm,
            box_l_mm=box_l_mm,
            box_h_mm=box_h_mm,
        )
        fig.suptitle("Multi-target DBSCAN Tracking", y=0.96, fontsize=14, weight="bold")

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=max(1, int(1000 / max(1, fps))), repeat=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = animation.PillowWriter(fps=fps)
    ani.save(output_path, writer=writer, dpi=180)
    plt.close(fig)
    print(f"GIF saved to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate frame-by-frame GIF for multi-target DBSCAN tracking.")
    parser.add_argument("--output", default="DBSCAN/output/multi_target_tracker_animation.gif", help="Output GIF path")
    parser.add_argument("--fps", type=int, default=3, help="GIF frame rate")
    parser.add_argument("--window-size", type=int, default=15)
    parser.add_argument("--eps-mm", type=float, default=15.0)
    parser.add_argument("--min-pts", type=int, default=8)
    parser.add_argument("--sigma-thresh-mm", type=float, default=3.0)
    parser.add_argument("--association-dist-thresh-mm", type=float, default=80.0)
    parser.add_argument("--max-missed-frames", type=int, default=3)
    parser.add_argument("--box-w-mm", type=float, default=30.0)
    parser.add_argument("--box-l-mm", type=float, default=30.0)
    parser.add_argument("--box-h-mm", type=float, default=30.0)
    args = parser.parse_args()

    make_animation(
        output_path=Path(args.output),
        fps=args.fps,
        window_size=args.window_size,
        eps_mm=args.eps_mm,
        min_pts=args.min_pts,
        sigma_thresh_mm=args.sigma_thresh_mm,
        association_dist_thresh_mm=args.association_dist_thresh_mm,
        max_missed_frames=args.max_missed_frames,
        box_w_mm=args.box_w_mm,
        box_l_mm=args.box_l_mm,
        box_h_mm=args.box_h_mm,
    )


if __name__ == "__main__":
    main()
