from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Callable, Optional

import numpy as np

try:
    from DBSCAN.multi_target_dbscan_tracker import MultiTargetDBSCANTracker
    from DBSCAN.multiframe_dbscan_filter import MultiFrameDBSCANFilter
except ModuleNotFoundError:
    from multi_target_dbscan_tracker import MultiTargetDBSCANTracker
    from multiframe_dbscan_filter import MultiFrameDBSCANFilter


@dataclass
class SingleOutput:
    mode: str
    timestamp: Any
    frame_index: int
    input_points: int
    locked: bool
    cluster_xyz_mm: Optional[list[float]]
    sigma_mm: Optional[float]
    core_size: int
    reason: str


class _RuntimeRealtimeViewer:
    """Optional runtime viewer for quick online debugging."""

    def __init__(self, mode: str) -> None:
        self.enabled = False
        self.mode = mode
        self._plt = None
        self._fig = None
        self._ax3d = None
        self._ax_txt = None
        try:
            import matplotlib.pyplot as plt
        except Exception:
            return

        self._plt = plt
        try:
            plt.ion()
            self._fig = plt.figure(figsize=(10, 5))
            self._ax3d = self._fig.add_subplot(1, 2, 1, projection="3d")
            self._ax_txt = self._fig.add_subplot(1, 2, 2)
            self.enabled = True
        except Exception:
            self.enabled = False

    def update_single(self, filt: MultiFrameDBSCANFilter, output: dict[str, Any]) -> None:
        if not self.enabled:
            return
        self._ax3d.cla()
        self._ax_txt.cla()
        window = filt.get_window_points()
        if window.size > 0:
            self._ax3d.scatter(window[:, 0], window[:, 1], window[:, 2], c="#607d8b", s=10, alpha=0.8)
        if output["cluster_xyz_mm"] is not None:
            c = np.asarray(output["cluster_xyz_mm"], dtype=float)
            self._ax3d.scatter(c[0], c[1], c[2], c="#f57f17", marker="*", s=90)
        self._ax3d.set_title("Realtime Single-Target")
        self._ax3d.set_xlabel("X(mm)")
        self._ax3d.set_ylabel("Y(mm)")
        self._ax3d.set_zlabel("Z(mm)")

        self._ax_txt.axis("off")
        self._ax_txt.text(0.02, 0.92, f"frame: {output['frame_index']}", fontsize=10)
        self._ax_txt.text(0.02, 0.84, f"locked: {output['locked']}", fontsize=10)
        self._ax_txt.text(0.02, 0.76, f"reason: {output['reason']}", fontsize=10)
        self._ax_txt.text(0.02, 0.68, f"core_size: {output['core_size']}", fontsize=10)
        self._ax_txt.text(0.02, 0.60, f"sigma(mm): {output['sigma_mm']}", fontsize=10)
        self._ax_txt.text(0.02, 0.52, f"cluster: {output['cluster_xyz_mm']}", fontsize=10)
        self._fig.tight_layout()
        self._plt.pause(0.001)

    def update_multi(self, tracker: MultiTargetDBSCANTracker, output: dict[str, Any]) -> None:
        if not self.enabled:
            return
        self._ax3d.cla()
        self._ax_txt.cla()
        color_cycle = ["#1e88e5", "#43a047", "#e53935", "#8e24aa", "#fb8c00", "#00897b"]
        tracks = tracker.get_tracks()
        for idx, track_id in enumerate(sorted(tracks.keys())):
            color = color_cycle[idx % len(color_cycle)]
            state = tracks[track_id]
            win = state.filter_obj.get_window_points()
            if win.size > 0:
                self._ax3d.scatter(win[:, 0], win[:, 1], win[:, 2], c=color, s=10, alpha=0.8)
            r = state.last_result
            if r.p_final is not None:
                self._ax3d.scatter(r.p_final[0], r.p_final[1], r.p_final[2], c=color, marker="*", s=90)
        self._ax3d.set_title("Realtime Multi-Target")
        self._ax3d.set_xlabel("X(mm)")
        self._ax3d.set_ylabel("Y(mm)")
        self._ax3d.set_zlabel("Z(mm)")

        self._ax_txt.axis("off")
        self._ax_txt.text(0.02, 0.92, f"frame: {output['frame_index']}", fontsize=10)
        self._ax_txt.text(0.02, 0.84, f"active_track_count: {output['active_track_count']}", fontsize=10)
        self._ax_txt.text(0.02, 0.76, f"primary_track_id: {output['primary_track_id']}", fontsize=10)
        self._ax_txt.text(0.02, 0.68, f"primary_cluster: {output['primary_cluster_xyz_mm']}", fontsize=10)
        self._fig.tight_layout()
        self._plt.pause(0.001)


class DBSCANRuntimeInterface:
    """
    Runtime input/output interface for online camera XYZ stream.

    Input:
    - single mode: one point [x, y, z] each frame (or first point from Nx3)
    - multi mode: multiple points [[x,y,z], ...] each frame

    Output:
    - process_frame(...) returns structured dict
    - optional callback via add_output_callback
    - optional JSON serialization via dumps_output(...)
    """

    def __init__(
        self,
        mode: str = "single",
        window_size: int = 15,
        eps_mm: float = 15.0,
        min_pts: int = 8,
        sigma_thresh_mm: float = 3.0,
        association_dist_thresh_mm: float = 80.0,
        max_missed_frames: int = 3,
        realtime: bool = False,
    ) -> None:
        mode = mode.strip().lower()
        if mode not in {"single", "multi"}:
            raise ValueError("mode must be 'single' or 'multi'")

        self.mode = mode
        self.frame_index = 0
        self._last_output: Optional[dict[str, Any]] = None
        self._callbacks: list[Callable[[dict[str, Any]], None]] = []

        self._single_filter: Optional[MultiFrameDBSCANFilter] = None
        self._multi_tracker: Optional[MultiTargetDBSCANTracker] = None
        if self.mode == "single":
            self._single_filter = MultiFrameDBSCANFilter(
                window_size=window_size,
                eps_mm=eps_mm,
                min_pts=min_pts,
                sigma_thresh_mm=sigma_thresh_mm,
            )
        else:
            self._multi_tracker = MultiTargetDBSCANTracker(
                window_size=window_size,
                eps_mm=eps_mm,
                min_pts=min_pts,
                sigma_thresh_mm=sigma_thresh_mm,
                association_dist_thresh_mm=association_dist_thresh_mm,
                max_missed_frames=max_missed_frames,
            )

        self._viewer = _RuntimeRealtimeViewer(mode=self.mode) if realtime else None

    def add_output_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._callbacks.append(callback)

    def get_last_output(self) -> Optional[dict[str, Any]]:
        return self._last_output

    @staticmethod
    def dumps_output(output: dict[str, Any]) -> str:
        return json.dumps(output, ensure_ascii=False)

    def process_frame(self, points_xyz_mm: np.ndarray | list, timestamp: Any = None) -> dict[str, Any]:
        self.frame_index += 1
        points = self._normalize_points(points_xyz_mm)

        if self.mode == "single":
            output = self._process_single(points, timestamp=timestamp)
        else:
            output = self._process_multi(points, timestamp=timestamp)

        self._last_output = output
        for cb in self._callbacks:
            cb(output)
        return output

    @staticmethod
    def _normalize_points(points_xyz_mm: np.ndarray | list) -> np.ndarray:
        arr = np.asarray(points_xyz_mm, dtype=float)
        if arr.size == 0:
            return np.empty((0, 3), dtype=float)
        if arr.ndim == 1:
            if arr.size != 3:
                raise ValueError("point must be [x, y, z]")
            return arr.reshape(1, 3)
        if arr.ndim == 2 and arr.shape[1] == 3:
            return arr
        raise ValueError("points must be shape [3] or [N, 3]")

    def _process_single(self, points: np.ndarray, timestamp: Any) -> dict[str, Any]:
        assert self._single_filter is not None
        if points.shape[0] == 0:
            output = asdict(
                SingleOutput(
                    mode="single",
                    timestamp=timestamp,
                    frame_index=self.frame_index,
                    input_points=0,
                    locked=False,
                    cluster_xyz_mm=None,
                    sigma_mm=None,
                    core_size=0,
                    reason="no_detection",
                )
            )
            if self._viewer is not None:
                self._viewer.update_single(self._single_filter, output)
            return output

        # Single mode only consumes one point per frame; if multiple points are
        # provided, use the first and keep the count for tracing.
        result = self._single_filter.add_observation(points[0])
        output = asdict(
            SingleOutput(
                mode="single",
                timestamp=timestamp,
                frame_index=self.frame_index,
                input_points=int(points.shape[0]),
                locked=bool(result.locked),
                cluster_xyz_mm=None if result.p_final is None else [float(x) for x in result.p_final.tolist()],
                sigma_mm=None if result.sigma_mm is None else float(result.sigma_mm),
                core_size=int(result.core_size),
                reason=result.reason,
            )
        )
        if self._viewer is not None:
            self._viewer.update_single(self._single_filter, output)
        return output

    def _process_multi(self, points: np.ndarray, timestamp: Any) -> dict[str, Any]:
        assert self._multi_tracker is not None
        self._multi_tracker.update(points)
        tracks_state = self._multi_tracker.get_tracks()

        tracks_out = []
        for track_id in sorted(tracks_state.keys()):
            st = tracks_state[track_id]
            r = st.last_result
            tracks_out.append(
                {
                    "track_id": int(track_id),
                    "locked": bool(r.locked),
                    "cluster_xyz_mm": None if r.p_final is None else [float(x) for x in r.p_final.tolist()],
                    "sigma_mm": None if r.sigma_mm is None else float(r.sigma_mm),
                    "core_size": int(r.core_size),
                    "reason": r.reason,
                    "missed_frames": int(st.missed_frames),
                    "age": int(st.age),
                    "last_observation_xyz_mm": [float(x) for x in st.last_observation.tolist()],
                }
            )

        primary_track_id = None
        primary_cluster_xyz_mm = None
        candidates = [t for t in tracks_out if t["cluster_xyz_mm"] is not None]
        if candidates:
            # Prefer locked tracks, then larger core_size, then lower sigma.
            candidates.sort(
                key=lambda t: (
                    0 if t["locked"] else 1,
                    -t["core_size"],
                    float("inf") if t["sigma_mm"] is None else t["sigma_mm"],
                    t["track_id"],
                )
            )
            primary = candidates[0]
            primary_track_id = int(primary["track_id"])
            primary_cluster_xyz_mm = primary["cluster_xyz_mm"]

        output = {
            "mode": "multi",
            "timestamp": timestamp,
            "frame_index": int(self.frame_index),
            "input_points": int(points.shape[0]),
            "active_track_count": int(len(tracks_out)),
            "primary_track_id": primary_track_id,
            "primary_cluster_xyz_mm": primary_cluster_xyz_mm,
            "tracks": tracks_out,
        }
        if self._viewer is not None:
            self._viewer.update_multi(self._multi_tracker, output)
        return output
