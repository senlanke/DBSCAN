import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from DBSCAN.multi_target_dbscan_tracker import MultiTargetDBSCANTracker
from DBSCAN.viz_utils import PSEUDO_TARGET_CENTER, build_pseudo_target_demo_frames


def _nearest_center_distance(point: np.ndarray, centers: list[np.ndarray]) -> float:
    return float(min(np.linalg.norm(point - c) for c in centers))


def test_associate_two_targets_without_stable_ids():
    tracker = MultiTargetDBSCANTracker(
        window_size=15,
        eps_mm=15.0,
        min_pts=8,
        sigma_thresh_mm=3.0,
        association_dist_thresh_mm=80.0,
        max_missed_frames=3,
    )
    rng = np.random.default_rng(20260304)
    center_a = np.array([100.0, -30.0, 350.0])
    center_b = np.array([260.0, 70.0, 360.0])

    latest = {}
    for frame_idx in range(20):
        p_a = center_a + rng.normal(0.0, 1.0, size=3)
        p_b = center_b + rng.normal(0.0, 1.0, size=3)
        # occasional depth penetration outlier on target A
        if frame_idx in (5, 11, 17):
            p_a = p_a + np.array([0.0, 0.0, 250.0])
        frame_points = np.vstack([p_a, p_b])
        # simulate detector output order instability
        if frame_idx % 2 == 0:
            frame_points = frame_points[::-1]
        latest = tracker.update(frame_points)

    assert len(latest) == 2
    assert len(tracker.get_active_track_ids()) == 2

    final_points = []
    locked_num = 0
    for track_out in latest.values():
        if track_out.result.p_final is not None:
            final_points.append(track_out.result.p_final)
        if track_out.result.locked:
            locked_num += 1

    assert len(final_points) == 2
    for p_final in final_points:
        assert _nearest_center_distance(p_final, [center_a, center_b]) < 10.0
    assert locked_num == 2


def test_create_new_track_for_far_new_target():
    tracker = MultiTargetDBSCANTracker(association_dist_thresh_mm=60.0, max_missed_frames=2)

    first_center = np.array([0.0, 0.0, 330.0])
    second_center = np.array([220.0, 0.0, 330.0])
    rng = np.random.default_rng(123)

    for _ in range(6):
        tracker.update(np.array([first_center + rng.normal(0.0, 0.5, size=3)]))

    assert len(tracker.get_active_track_ids()) == 1

    tracker.update(
        np.array(
            [
                first_center + rng.normal(0.0, 0.5, size=3),
                second_center + rng.normal(0.0, 0.5, size=3),
            ]
        )
    )
    assert len(tracker.get_active_track_ids()) == 2


def test_remove_stale_track_when_missing_too_long():
    tracker = MultiTargetDBSCANTracker(max_missed_frames=2)
    rng = np.random.default_rng(9)
    center = np.array([50.0, 10.0, 320.0])

    for _ in range(3):
        tracker.update(np.array([center + rng.normal(0.0, 0.5, size=3)]))
    assert len(tracker.get_active_track_ids()) == 1

    tracker.update(np.empty((0, 3)))
    tracker.update(np.empty((0, 3)))
    tracker.update(np.empty((0, 3)))
    assert len(tracker.get_active_track_ids()) == 0


def test_far_unmatched_point_creates_new_track_instead_of_reusing_old_one():
    tracker = MultiTargetDBSCANTracker(association_dist_thresh_mm=60.0, max_missed_frames=3)
    origin = np.array([0.0, 0.0, 330.0])
    far_point = np.array([320.0, 0.0, 580.0])

    for _ in range(2):
        tracker.update(np.array([origin]))

    outputs = tracker.update(np.array([far_point]))

    assert len(tracker.get_active_track_ids()) == 2
    new_track_ids = set(outputs.keys()) - {1}
    assert len(new_track_ids) == 1
    new_track_id = next(iter(new_track_ids))
    assert np.allclose(outputs[new_track_id].observation, far_point)


def test_xy_close_depth_jump_keeps_track_continuity():
    tracker = MultiTargetDBSCANTracker(association_dist_thresh_mm=60.0, max_missed_frames=3)
    base_point = np.array([100.0, -30.0, 350.0])
    depth_jump_point = np.array([102.0, -29.0, 610.0])

    for _ in range(2):
        tracker.update(np.array([base_point]))

    outputs = tracker.update(np.array([depth_jump_point]))

    assert tracker.get_active_track_ids() == [1]
    assert list(outputs.keys()) == [1]
    assert np.allclose(outputs[1].observation, depth_jump_point)


def test_persistent_false_detections_can_become_locked_pseudo_target():
    tracker = MultiTargetDBSCANTracker(
        window_size=15,
        eps_mm=15.0,
        min_pts=8,
        sigma_thresh_mm=3.0,
        association_dist_thresh_mm=80.0,
        max_missed_frames=3,
    )

    latest = {}
    for frame_points in build_pseudo_target_demo_frames(num_frames=20):
        latest = tracker.update(frame_points)

    assert len(tracker.get_active_track_ids()) == 4

    pseudo_tracks = []
    for track_out in latest.values():
        if track_out.result.p_final is None:
            continue
        if np.linalg.norm(track_out.result.p_final - PSEUDO_TARGET_CENTER) < 12.0:
            pseudo_tracks.append(track_out)

    assert len(pseudo_tracks) == 1
    assert pseudo_tracks[0].result.locked is True
