from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

try:
    from DBSCAN.multiframe_dbscan_filter import FilterResult, MultiFrameDBSCANFilter
except ModuleNotFoundError:
    from multiframe_dbscan_filter import FilterResult, MultiFrameDBSCANFilter


@dataclass
class TrackState:
    track_id: int
    filter_obj: MultiFrameDBSCANFilter
    last_observation: np.ndarray
    last_result: FilterResult
    missed_frames: int = 0
    age: int = 1


@dataclass
class TrackOutput:
    track_id: int
    observation: np.ndarray
    result: FilterResult


class MultiTargetDBSCANTracker:
    """
    Multi-target tracker without stable detector IDs.

    Association strategy:
    - greedy nearest-neighbor matching between active tracks and current points
    - assignments accepted only if distance <= association_dist_thresh_mm
    """

    def __init__(
        self,
        window_size: int = 15,
        eps_mm: float = 15.0,
        min_pts: int = 8,
        sigma_thresh_mm: float = 3.0,
        association_dist_thresh_mm: float = 80.0,
        max_missed_frames: int = 3,
    ) -> None:
        if association_dist_thresh_mm <= 0:
            raise ValueError("association_dist_thresh_mm must be positive")
        if max_missed_frames < 0:
            raise ValueError("max_missed_frames must be >= 0")

        self.window_size = int(window_size)
        self.eps_mm = float(eps_mm)
        self.min_pts = int(min_pts)
        self.sigma_thresh_mm = float(sigma_thresh_mm)
        self.association_dist_thresh_mm = float(association_dist_thresh_mm)
        self.max_missed_frames = int(max_missed_frames)

        self._tracks: Dict[int, TrackState] = {}
        self._next_track_id = 1

    def update(self, frame_points_xyz_mm: np.ndarray) -> dict[int, TrackOutput]:
        points = np.asarray(frame_points_xyz_mm, dtype=float)
        if points.size == 0:
            points = np.empty((0, 3), dtype=float)
        points = np.atleast_2d(points)
        if points.shape[1] != 3:
            raise ValueError("frame_points_xyz_mm must have shape [N, 3]")

        track_ids = list(self._tracks.keys())
        assignments = self._associate(track_ids, points)

        assigned_track_ids = set(assignments.keys())
        assigned_point_indices = set(assignments.values())

        outputs: dict[int, TrackOutput] = {}

        for track_id, point_idx in assignments.items():
            obs = points[point_idx]
            track = self._tracks[track_id]
            result = track.filter_obj.add_observation(obs)
            track.last_observation = obs
            track.last_result = result
            track.missed_frames = 0
            track.age += 1
            outputs[track_id] = TrackOutput(track_id=track_id, observation=obs, result=result)

        for track_id in track_ids:
            if track_id in assigned_track_ids:
                continue
            track = self._tracks[track_id]
            track.missed_frames += 1

        for point_idx in range(points.shape[0]):
            if point_idx in assigned_point_indices:
                continue
            self._create_track(points[point_idx], outputs)

        self._prune_stale_tracks()
        return outputs

    def get_active_track_ids(self) -> list[int]:
        return sorted(self._tracks.keys())

    def get_tracks(self) -> dict[int, TrackState]:
        return dict(self._tracks)

    def _associate(self, track_ids: list[int], points: np.ndarray) -> dict[int, int]:
        if not track_ids or points.shape[0] == 0:
            return {}

        track_positions = np.vstack([self._tracks[tid].last_observation for tid in track_ids])
        dists = np.linalg.norm(track_positions[:, None, :] - points[None, :, :], axis=2)

        pairs = []
        for ti, track_id in enumerate(track_ids):
            for pi in range(points.shape[0]):
                pairs.append((float(dists[ti, pi]), track_id, pi))
        pairs.sort(key=lambda x: x[0])

        assigned_tracks = set()
        assigned_points = set()
        assignments: dict[int, int] = {}
        for dist, track_id, point_idx in pairs:
            if dist > self.association_dist_thresh_mm:
                break
            if track_id in assigned_tracks or point_idx in assigned_points:
                continue
            assignments[track_id] = point_idx
            assigned_tracks.add(track_id)
            assigned_points.add(point_idx)

        # Fallback for unstable depth jumps:
        # when detections are not more than active tracks, we keep continuity for
        # large depth-only jumps, but still require lateral proximity. This avoids
        # hijacking an old track with a truly far-away new target.
        if points.shape[0] <= len(track_ids):
            xy_dists = np.linalg.norm(track_positions[:, None, :2] - points[None, :, :2], axis=2)
            xy_pairs = []
            for ti, track_id in enumerate(track_ids):
                for pi in range(points.shape[0]):
                    xy_pairs.append((float(xy_dists[ti, pi]), track_id, pi))
            xy_pairs.sort(key=lambda x: x[0])

            for xy_dist, track_id, point_idx in xy_pairs:
                if xy_dist > self.association_dist_thresh_mm:
                    break
                if track_id in assigned_tracks or point_idx in assigned_points:
                    continue
                assignments[track_id] = point_idx
                assigned_tracks.add(track_id)
                assigned_points.add(point_idx)

        return assignments

    def _create_track(self, observation: np.ndarray, outputs: dict[int, TrackOutput]) -> None:
        track_id = self._next_track_id
        self._next_track_id += 1
        filt = MultiFrameDBSCANFilter(
            window_size=self.window_size,
            eps_mm=self.eps_mm,
            min_pts=self.min_pts,
            sigma_thresh_mm=self.sigma_thresh_mm,
        )
        result = filt.add_observation(observation)
        state = TrackState(
            track_id=track_id,
            filter_obj=filt,
            last_observation=observation,
            last_result=result,
            missed_frames=0,
            age=1,
        )
        self._tracks[track_id] = state
        outputs[track_id] = TrackOutput(track_id=track_id, observation=observation, result=result)

    def _prune_stale_tracks(self) -> None:
        stale = [tid for tid, tr in self._tracks.items() if tr.missed_frames > self.max_missed_frames]
        for tid in stale:
            del self._tracks[tid]
