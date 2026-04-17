from __future__ import annotations

try:
    from DBSCAN.multi_target_dbscan_tracker import MultiTargetDBSCANTracker
    from DBSCAN.viz_utils import PSEUDO_TARGET_CENTER, build_pseudo_target_demo_frames
except ModuleNotFoundError:
    from multi_target_dbscan_tracker import MultiTargetDBSCANTracker
    from viz_utils import PSEUDO_TARGET_CENTER, build_pseudo_target_demo_frames


def main() -> None:
    tracker = MultiTargetDBSCANTracker(
        window_size=15,
        eps_mm=15.0,
        min_pts=8,
        sigma_thresh_mm=3.0,
        association_dist_thresh_mm=80.0,
        max_missed_frames=3,
    )

    print("Pseudo-target counterexample demo")
    print(f"Designed false-target center: ({PSEUDO_TARGET_CENTER[0]:.1f}, {PSEUDO_TARGET_CENTER[1]:.1f}, {PSEUDO_TARGET_CENTER[2]:.1f})")

    latest = {}
    for frame_idx, frame_points in enumerate(build_pseudo_target_demo_frames(num_frames=20), start=1):
        latest = tracker.update(frame_points)
        active_tracks = tracker.get_active_track_ids()
        print(f"\nFrame {frame_idx:02d} | detections={len(frame_points)} | active_tracks={len(active_tracks)}")
        for track_id in sorted(latest.keys()):
            out = latest[track_id]
            obs = out.observation
            result = out.result
            if result.p_final is None:
                print(
                    f"  track={track_id} obs=({obs[0]:.2f},{obs[1]:.2f},{obs[2]:.2f}) status={result.reason}"
                )
                continue

            p_final = result.p_final
            dist_to_false = float(((p_final - PSEUDO_TARGET_CENTER) ** 2).sum() ** 0.5)
            print(
                f"  track={track_id} obs=({obs[0]:.2f},{obs[1]:.2f},{obs[2]:.2f}) "
                f"locked={result.locked} sigma={result.sigma_mm:.3f} core={result.core_size} "
                f"p_final=({p_final[0]:.2f},{p_final[1]:.2f},{p_final[2]:.2f}) "
                f"dist_to_false={dist_to_false:.2f}"
            )

    pseudo_track = None
    for track_id, state in sorted(tracker.get_tracks().items()):
        result = state.last_result
        if result.p_final is None:
            continue
        dist_to_false = float(((result.p_final - PSEUDO_TARGET_CENTER) ** 2).sum() ** 0.5)
        if dist_to_false < 12.0:
            pseudo_track = (track_id, result, dist_to_false)
            break

    print("\nSummary:")
    if pseudo_track is None:
        print("  No pseudo target locked in this run.")
    else:
        track_id, result, dist_to_false = pseudo_track
        p_final = result.p_final
        print(
            f"  Pseudo target formed on track={track_id}, locked={result.locked}, "
            f"core={result.core_size}, sigma={result.sigma_mm:.3f}, "
            f"p_final=({p_final[0]:.2f},{p_final[1]:.2f},{p_final[2]:.2f}), "
            f"dist_to_false={dist_to_false:.2f}"
        )


if __name__ == "__main__":
    main()
