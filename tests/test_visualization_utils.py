import sys
from pathlib import Path

import numpy as np
import matplotlib
from PIL import Image

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_collect_multi_target_snapshots_keeps_last_state_of_pruned_tracks():
    from DBSCAN.viz_utils import collect_multi_target_snapshots, build_multi_target_demo_frames

    frames = build_multi_target_demo_frames(num_frames=6)
    snapshots, latest = collect_multi_target_snapshots(
        frames=frames[:2] + [np.empty((0, 3)), np.empty((0, 3)), np.empty((0, 3)), frames[-1]],
        window_size=3,
        eps_mm=15.0,
        min_pts=2,
        sigma_thresh_mm=3.0,
        association_dist_thresh_mm=60.0,
        max_missed_frames=1,
    )

    assert len(snapshots) == 6
    assert 1 in latest
    assert latest[1].history.shape[1] == 3
    assert latest[1].active is False


def test_fit_publication_box_dims_keeps_visible_minimum_box():
    from DBSCAN.viz_utils import fit_publication_box_dims

    tiny_core = np.array(
        [
            [10.0, 10.0, 10.0],
            [10.3, 10.2, 10.1],
        ]
    )

    box_w, box_l, box_h = fit_publication_box_dims(
        tiny_core,
        max_w_mm=30.0,
        max_l_mm=30.0,
        max_h_mm=30.0,
    )

    assert box_w >= 10.0
    assert box_l >= 10.0
    assert box_h >= 10.0


def test_spread_publication_points_visibly_separates_dense_points():
    from DBSCAN.viz_utils import spread_publication_points

    points = np.tile(np.array([[100.0, -30.0, 350.0]]), (8, 1))
    spread = spread_publication_points(points)
    offsets = np.linalg.norm(spread - points, axis=1)

    assert np.max(offsets) > 0.70


def test_spread_publication_cluster_points_separates_dense_points_more_aggressively():
    from DBSCAN.viz_utils import spread_publication_cluster_points

    points = np.tile(np.array([[100.0, -30.0, 350.0]]), (8, 1))
    spread = spread_publication_cluster_points(points)
    offsets = np.linalg.norm(spread - points, axis=1)

    assert np.max(offsets) > 1.80


def test_compute_focus_limits_zooms_cluster_panel_around_target_region():
    from DBSCAN.viz_utils import compute_focus_limits

    points = np.array(
        [
            [109.5, -35.8, 349.6],
            [110.6, -34.9, 350.3],
            [110.1, -35.3, 349.9],
        ]
    )
    center = np.array([110.0, -35.2, 350.0])

    xlim, ylim, zlim = compute_focus_limits(points, center=center, min_xy_span_mm=18.0, min_z_span_mm=18.0)

    assert (xlim[1] - xlim[0]) >= 18.0
    assert (ylim[1] - ylim[0]) >= 18.0
    assert (zlim[1] - zlim[0]) >= 18.0
    assert xlim[0] < center[0] < xlim[1]
    assert ylim[0] < center[1] < ylim[1]
    assert zlim[0] < center[2] < zlim[1]


def test_to_display_points_swaps_y_and_z():
    from DBSCAN.viz_utils import to_display_points

    points = np.array(
        [
            [1.0, 2.0, 3.0],
            [10.0, 20.0, 30.0],
        ]
    )

    assert np.allclose(
        to_display_points(points),
        np.array(
            [
                [1.0, 3.0, 2.0],
                [10.0, 30.0, 20.0],
            ]
        ),
    )


def test_publication_display_ranges_are_mapped_to_x_z_y_axes():
    from DBSCAN.viz_utils import publication_display_ranges

    xlim, ylim, zlim = publication_display_ranges("single", "raw")

    assert xlim == (84.0, 174.0)
    assert ylim == (348.0, 480.0)
    assert zlim == (-62.0, 18.0)


def test_publication_axis_labels_use_x_z_y_order():
    from DBSCAN.viz_utils import publication_axis_labels

    assert publication_axis_labels() == ("X (mm)", "Z (mm)", "Y (mm)")


def test_publication_fixed_ranges_match_approved_demo_layout():
    from DBSCAN.viz_utils import PUBLICATION_FIXED_RANGES

    assert PUBLICATION_FIXED_RANGES["single"]["raw"]["x"] == (84.0, 174.0)
    assert PUBLICATION_FIXED_RANGES["single"]["raw"]["z"] == (348.0, 480.0)
    assert PUBLICATION_FIXED_RANGES["single"]["raw"]["y"] == (-62.0, 18.0)
    assert PUBLICATION_FIXED_RANGES["single"]["cluster"]["x"] == (92.0, 166.0)
    assert PUBLICATION_FIXED_RANGES["single"]["cluster"]["z"] == (352.0, 480.0)
    assert PUBLICATION_FIXED_RANGES["single"]["cluster"]["y"] == (-54.0, 10.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["raw"]["x"] == (96.0, 186.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["raw"]["z"] == (338.0, 470.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["raw"]["y"] == (-38.0, 42.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["cluster"]["x"] == (106.0, 180.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["cluster"]["z"] == (342.0, 470.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["cluster"]["y"] == (-30.0, 34.0)

    assert (PUBLICATION_FIXED_RANGES["single"]["raw"]["x"][1] - PUBLICATION_FIXED_RANGES["single"]["raw"]["x"][0]) == 90.0
    assert (PUBLICATION_FIXED_RANGES["single"]["raw"]["z"][1] - PUBLICATION_FIXED_RANGES["single"]["raw"]["z"][0]) == 132.0
    assert (PUBLICATION_FIXED_RANGES["single"]["raw"]["y"][1] - PUBLICATION_FIXED_RANGES["single"]["raw"]["y"][0]) == 80.0
    assert (PUBLICATION_FIXED_RANGES["single"]["cluster"]["x"][1] - PUBLICATION_FIXED_RANGES["single"]["cluster"]["x"][0]) == 74.0
    assert (PUBLICATION_FIXED_RANGES["single"]["cluster"]["z"][1] - PUBLICATION_FIXED_RANGES["single"]["cluster"]["z"][0]) == 128.0
    assert (PUBLICATION_FIXED_RANGES["single"]["cluster"]["y"][1] - PUBLICATION_FIXED_RANGES["single"]["cluster"]["y"][0]) == 64.0


def test_single_demo_contains_moderate_high_z_outliers():
    from DBSCAN.viz_utils import build_single_target_demo_points

    points = build_single_target_demo_points()
    zs = np.sort(points[:, 2])[-3:]

    assert np.allclose(zs, np.array([440.0, 460.0, 480.0]))


def test_multi_demo_centers_match_publication_layout():
    from DBSCAN.viz_utils import MULTI_DEMO_CENTERS

    assert np.allclose(MULTI_DEMO_CENTERS["A"], np.array([112.0, -12.0, 346.0]))
    assert np.allclose(MULTI_DEMO_CENTERS["B"], np.array([142.0, 6.0, 356.0]))
    assert np.allclose(MULTI_DEMO_CENTERS["C"], np.array([172.0, -8.0, 349.0]))


def test_multi_demo_frames_now_contain_three_targets_per_frame():
    from DBSCAN.viz_utils import build_multi_target_demo_frames

    frames = build_multi_target_demo_frames(num_frames=4)

    assert len(frames) == 4
    assert all(frame.shape == (3, 3) for frame in frames)


def test_multi_demo_injects_outliers_for_first_and_third_targets_on_separate_frames():
    from DBSCAN.viz_utils import build_multi_target_demo_frames

    frames = build_multi_target_demo_frames(num_frames=18)
    frame_max_z = np.array([np.max(frame[:, 2]) for frame in frames], dtype=float)
    outlier_frames = np.where(frame_max_z > 430.0)[0].tolist()

    assert outlier_frames == [3, 5, 9, 11, 15, 17]


def test_pseudo_target_demo_frames_add_fourth_detection_after_false_target_appears():
    from DBSCAN.viz_utils import build_pseudo_target_demo_frames, PSEUDO_TARGET_CENTER

    frames = build_pseudo_target_demo_frames(num_frames=20)

    assert len(frames) == 20
    assert all(frame.shape == (3, 3) for frame in frames[:5])
    assert all(frame.shape == (4, 3) for frame in frames[5:])
    assert np.allclose(PSEUDO_TARGET_CENTER, np.array([222.0, 92.0, 446.0]))


def test_create_publication_figure_axes_for_single_target_uses_two_panels():
    from DBSCAN.viz_utils import create_publication_figure_axes

    fig, axes = create_publication_figure_axes(mode="single", figsize=(10.0, 5.0))

    try:
        assert set(axes.keys()) == {"raw", "cluster"}
        assert len(fig.axes) == 2
    finally:
        import matplotlib.pyplot as plt

        plt.close(fig)


def test_apply_publication_style_loads_scientific_figure_pro_without_import_error():
    from DBSCAN.viz_utils import apply_publication_style

    apply_publication_style(font_size=12.0, axes_linewidth=1.2)


def test_publication_box_style_uses_edge_only_presentation_defaults():
    from DBSCAN.viz_utils import PUBLICATION_BOX_STYLE

    assert PUBLICATION_BOX_STYLE["color"] == "#37474F"
    assert PUBLICATION_BOX_STYLE["linewidth"] <= 1.4
    assert PUBLICATION_BOX_STYLE["fill"] is False


def test_publication_marker_sizes_keep_cluster_points_small():
    from DBSCAN.viz_utils import PUBLICATION_MARKER_SIZES

    assert PUBLICATION_MARKER_SIZES["window_points"] <= 10
    assert PUBLICATION_MARKER_SIZES["cluster_core"] <= 12
    assert PUBLICATION_MARKER_SIZES["cluster_noise"] <= 8


def test_export_multi_single_panel_publication_outputs(tmp_path):
    from DBSCAN.animate_multi_target_demo import export_single_panel_publication_gifs
    from DBSCAN.visualize_multi_target_demo import export_single_panel_publication_pngs

    export_single_panel_publication_pngs(output_dir=tmp_path)
    export_single_panel_publication_gifs(output_dir=tmp_path, fps=3)

    observed_png = tmp_path / "publication_multi_observed.png"
    tracking_png = tmp_path / "publication_multi_tracking.png"
    observed_gif = tmp_path / "publication_multi_observed.gif"
    tracking_gif = tmp_path / "publication_multi_tracking.gif"

    for path in (observed_png, tracking_png, observed_gif, tracking_gif):
        assert path.exists()
        assert path.stat().st_size > 0

    observed_png_img = Image.open(observed_png)
    tracking_png_img = Image.open(tracking_png)
    observed_gif_img = Image.open(observed_gif)
    tracking_gif_img = Image.open(tracking_gif)

    assert observed_png_img.size[0] == observed_png_img.size[1]
    assert tracking_png_img.size[0] == tracking_png_img.size[1]
    assert observed_gif_img.size[0] == observed_gif_img.size[1]
    assert tracking_gif_img.size[0] == tracking_gif_img.size[1]
    assert observed_gif_img.n_frames == 20
    assert 15 <= tracking_gif_img.n_frames <= 20


def test_render_multi_tracking_axis_can_hide_summary_box():
    import matplotlib.pyplot as plt

    from DBSCAN.viz_utils import (
        build_multi_target_demo_frames,
        collect_multi_target_snapshots,
        render_multi_tracking_axis,
    )

    frames = build_multi_target_demo_frames()
    _, latest = collect_multi_target_snapshots(
        frames=frames,
        window_size=15,
        eps_mm=15.0,
        min_pts=8,
        sigma_thresh_mm=3.0,
        association_dist_thresh_mm=80.0,
        max_missed_frames=3,
    )

    fig = plt.figure(figsize=(6.0, 6.0))
    ax = fig.add_subplot(111, projection="3d")
    try:
        render_multi_tracking_axis(
            ax,
            state=latest,
            window_size=15,
            eps_mm=15.0,
            min_pts=8,
            association_dist_thresh_mm=80.0,
            max_missed_frames=3,
            box_w_mm=30.0,
            box_l_mm=30.0,
            box_h_mm=30.0,
            include_summary=False,
            legend_loc="upper center",
            legend_bbox_to_anchor=(0.5, -0.08),
            legend_ncol=2,
            title=None,
        )
        assert len(ax.texts) == 0
        legend = ax.get_legend()
        assert legend is not None
        assert len(legend.texts) == 4
        assert ax.get_title() == ""
    finally:
        plt.close(fig)


def test_freeze_locked_multi_snapshots_keeps_first_locked_state_for_later_frames():
    from DBSCAN.viz_utils import build_multi_target_demo_frames, collect_multi_target_snapshots, freeze_locked_multi_snapshots

    snapshots, _ = collect_multi_target_snapshots(
        frames=build_multi_target_demo_frames(),
        window_size=15,
        eps_mm=15.0,
        min_pts=8,
        sigma_thresh_mm=3.0,
        association_dist_thresh_mm=80.0,
        max_missed_frames=3,
    )
    frozen = freeze_locked_multi_snapshots(snapshots)

    first_locked_frame_idx = None
    first_locked_track_id = None
    for frame_idx, frame_state in enumerate(snapshots):
        for track_id, snapshot in sorted(frame_state.items()):
            if snapshot.locked:
                first_locked_frame_idx = frame_idx
                first_locked_track_id = track_id
                break
        if first_locked_frame_idx is not None:
            break

    assert first_locked_frame_idx is not None
    assert first_locked_track_id is not None

    raw_first = snapshots[first_locked_frame_idx][first_locked_track_id]
    raw_last = snapshots[-1][first_locked_track_id]
    frozen_last = frozen[-1][first_locked_track_id]

    assert not np.allclose(raw_last.center, raw_first.center)
    assert np.allclose(frozen_last.center, raw_first.center)
    assert np.array_equal(frozen_last.window, raw_first.window)
