import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from DBSCAN.runtime_interface import DBSCANRuntimeInterface


def test_single_mode_returns_cluster_coordinate_after_convergence():
    runtime = DBSCANRuntimeInterface(
        mode="single",
        window_size=15,
        eps_mm=15.0,
        min_pts=8,
        sigma_thresh_mm=3.0,
        realtime=False,
    )
    rng = np.random.default_rng(77)
    center = np.array([120.0, -40.0, 350.0])

    outputs = []
    for i in range(15):
        point = center + rng.normal(0.0, 1.0, size=3)
        if i in (4, 9, 13):
            point = point + np.array([0.0, 0.0, 240.0])
        outputs.append(runtime.process_frame(point, timestamp=i))

    last = outputs[-1]
    assert last["mode"] == "single"
    assert last["locked"] is True
    assert last["cluster_xyz_mm"] is not None
    assert np.linalg.norm(np.array(last["cluster_xyz_mm"]) - center) < 10.0


def test_single_mode_no_detection_keeps_running():
    runtime = DBSCANRuntimeInterface(mode="single", realtime=False)
    out = runtime.process_frame([], timestamp=1)
    assert out["mode"] == "single"
    assert out["locked"] is False
    assert out["cluster_xyz_mm"] is None
    assert out["reason"] == "no_detection"


def test_multi_mode_outputs_tracks_and_primary_coordinate():
    runtime = DBSCANRuntimeInterface(
        mode="multi",
        window_size=15,
        eps_mm=15.0,
        min_pts=8,
        sigma_thresh_mm=3.0,
        association_dist_thresh_mm=80.0,
        max_missed_frames=3,
        realtime=False,
    )
    rng = np.random.default_rng(20260304)
    center_a = np.array([100.0, -30.0, 350.0])
    center_b = np.array([260.0, 70.0, 360.0])

    final = None
    for frame_idx in range(20):
        p_a = center_a + rng.normal(0.0, 1.0, size=3)
        p_b = center_b + rng.normal(0.0, 1.0, size=3)
        if frame_idx in (5, 11, 17):
            p_a = p_a + np.array([0.0, 0.0, 250.0])
        frame = np.vstack([p_a, p_b])
        if frame_idx % 2 == 0:
            frame = frame[::-1]
        final = runtime.process_frame(frame, timestamp=frame_idx)

    assert final is not None
    assert final["mode"] == "multi"
    assert len(final["tracks"]) == 2
    assert final["primary_cluster_xyz_mm"] is not None

    centers = [center_a, center_b]
    for tr in final["tracks"]:
        if tr["cluster_xyz_mm"] is None:
            continue
        p = np.array(tr["cluster_xyz_mm"])
        assert min(np.linalg.norm(p - c) for c in centers) < 10.0
