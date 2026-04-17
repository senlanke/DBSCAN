from __future__ import annotations

try:
    from DBSCAN.multiframe_dbscan_filter import MultiFrameDBSCANFilter
    from DBSCAN.viz_utils import build_single_target_demo_points
except ModuleNotFoundError:
    from multiframe_dbscan_filter import MultiFrameDBSCANFilter
    from viz_utils import build_single_target_demo_points


def main() -> None:
    filt = MultiFrameDBSCANFilter(window_size=15, eps_mm=15.0, min_pts=8, sigma_thresh_mm=3.0)
    points = build_single_target_demo_points()

    print("Frame-by-frame filtering:")
    final_result = None
    for idx, p in enumerate(points, start=1):
        result = filt.add_observation(p)
        final_result = result
        if result.p_final is None:
            print(f"frame={idx:02d}, locked={result.locked}, reason={result.reason}")
        else:
            x, y, z = result.p_final
            print(
                f"frame={idx:02d}, locked={result.locked}, reason={result.reason}, "
                f"core_size={result.core_size}, sigma={result.sigma_mm:.3f} mm, "
                f"p_final=({x:.3f}, {y:.3f}, {z:.3f})"
            )

    if final_result is None:
        return

    print("\nFinal decision:")
    if final_result.p_final is None:
        print(f"locked={final_result.locked}, reason={final_result.reason}")
        return

    x, y, z = final_result.p_final
    print(
        f"locked={final_result.locked}, reason={final_result.reason}, "
        f"core_size={final_result.core_size}, sigma={final_result.sigma_mm:.3f} mm"
    )
    print(f"P_final(mm) = ({x:.3f}, {y:.3f}, {z:.3f})")


if __name__ == "__main__":
    main()
