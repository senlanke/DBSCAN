import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from DBSCAN.multiframe_dbscan_filter import MultiFrameDBSCANFilter


def _feed_points(filter_obj: MultiFrameDBSCANFilter, points: np.ndarray):
    result = None
    for p in points:
        result = filter_obj.add_observation(p)
    return result


def test_collecting_before_window_full():
    filt = MultiFrameDBSCANFilter(window_size=15, eps_mm=15.0, min_pts=8, sigma_thresh_mm=3.0)
    base = np.array([100.0, 50.0, 350.0])
    result = None

    for i in range(14):
        result = filt.add_observation(base + np.array([0.1 * i, 0.0, 0.0]))

    assert result is not None
    assert result.locked is False
    assert result.reason == "collecting"
    assert result.p_final is None
    assert result.sigma_mm is None


def test_reject_penetration_noise():
    filt = MultiFrameDBSCANFilter(window_size=15, eps_mm=15.0, min_pts=8, sigma_thresh_mm=3.0)
    rng = np.random.default_rng(7)
    true_center = np.array([120.0, -40.0, 350.0])

    stem_points = true_center + rng.normal(0.0, 1.0, size=(12, 3))
    penetration_noise = np.array(
        [
            [130.0, -50.0, 600.0],
            [80.0, -20.0, 580.0],
            [150.0, -30.0, 620.0],
        ]
    )
    points = np.vstack([stem_points, penetration_noise])

    result = _feed_points(filt, points)

    assert result is not None
    assert result.core_size >= 10
    assert np.linalg.norm(result.p_final - true_center) < 4.0
    assert result.locked is True


def test_lock_when_sigma_below_threshold():
    filt = MultiFrameDBSCANFilter(window_size=15, eps_mm=15.0, min_pts=8, sigma_thresh_mm=3.0)
    rng = np.random.default_rng(11)
    center = np.array([10.0, 20.0, 330.0])
    points = center + rng.normal(0.0, 0.6, size=(15, 3))

    result = _feed_points(filt, points)

    assert result is not None
    assert result.locked is True
    assert result.sigma_mm < 3.0
    assert result.core_size >= 8


def test_not_lock_when_sigma_too_large():
    filt = MultiFrameDBSCANFilter(window_size=15, eps_mm=15.0, min_pts=8, sigma_thresh_mm=3.0)
    rng = np.random.default_rng(23)
    center = np.array([0.0, 0.0, 350.0])
    points = center + rng.normal(0.0, 4.5, size=(15, 3))

    result = _feed_points(filt, points)

    assert result is not None
    assert result.core_size >= 8
    assert result.sigma_mm >= 3.0
    assert result.locked is False


def test_not_lock_when_core_size_below_minpts():
    filt = MultiFrameDBSCANFilter(window_size=15, eps_mm=15.0, min_pts=8, sigma_thresh_mm=3.0)
    points = np.array([[float(i * 40), 0.0, float(300 + i * 30)] for i in range(15)])

    result = _feed_points(filt, points)

    assert result is not None
    assert result.core_size < 8
    assert result.locked is False


def test_get_window_points_returns_latest_window():
    filt = MultiFrameDBSCANFilter(window_size=3, eps_mm=15.0, min_pts=2, sigma_thresh_mm=3.0)
    p1 = np.array([1.0, 0.0, 0.0])
    p2 = np.array([2.0, 0.0, 0.0])
    p3 = np.array([3.0, 0.0, 0.0])
    p4 = np.array([4.0, 0.0, 0.0])
    filt.add_observation(p1)
    filt.add_observation(p2)
    filt.add_observation(p3)
    filt.add_observation(p4)

    window = filt.get_window_points()
    assert window.shape == (3, 3)
    assert np.allclose(window[0], p2)
    assert np.allclose(window[1], p3)
    assert np.allclose(window[2], p4)
