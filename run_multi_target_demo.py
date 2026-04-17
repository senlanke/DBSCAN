from __future__ import annotations

try:
    from DBSCAN.multi_target_dbscan_tracker import MultiTargetDBSCANTracker
    from DBSCAN.viz_utils import build_multi_target_demo_frames
except ModuleNotFoundError:
    from multi_target_dbscan_tracker import MultiTargetDBSCANTracker
    from viz_utils import build_multi_target_demo_frames


def main() -> None:
    tracker = MultiTargetDBSCANTracker(
        window_size=15,
        eps_mm=15.0,
        min_pts=8,
        sigma_thresh_mm=3.0,
        association_dist_thresh_mm=80.0,
        max_missed_frames=3,
    )

    for frame_idx, frame_points in enumerate(build_multi_target_demo_frames(), start=1):
        outputs = tracker.update(frame_points)
        print(f"\nFrame {frame_idx:02d} | detections={len(frame_points)} | active_tracks={len(tracker.get_active_track_ids())}")
        for track_id in sorted(outputs.keys()):
            out = outputs[track_id]
            obs = out.observation
            if out.result.p_final is None:
                print(
                    f"  track={track_id} obs=({obs[0]:.2f},{obs[1]:.2f},{obs[2]:.2f}) "
                    f"status={out.result.reason}"
                )
                continue
            p_final = out.result.p_final
            print(
                f"  track={track_id} obs=({obs[0]:.2f},{obs[1]:.2f},{obs[2]:.2f}) "
                f"locked={out.result.locked} sigma={out.result.sigma_mm:.3f} "
                f"core={out.result.core_size} "
                f"p_final=({p_final[0]:.2f},{p_final[1]:.2f},{p_final[2]:.2f})"
            )

    print("\nFinal active tracks:")
    for track_id, state in sorted(tracker.get_tracks().items()):
        result = state.last_result
        if result.p_final is None:
            print(f"  track={track_id} age={state.age} missed={state.missed_frames} status={result.reason}")
            continue
        p_final = result.p_final
        print(
            f"  track={track_id} age={state.age} missed={state.missed_frames} "
            f"locked={result.locked} sigma={result.sigma_mm:.3f} "
            f"p_final=({p_final[0]:.2f},{p_final[1]:.2f},{p_final[2]:.2f})"
        )


if __name__ == "__main__":
    main()
