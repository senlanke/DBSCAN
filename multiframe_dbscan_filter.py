from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class FilterResult:
    locked: bool
    p_final: Optional[np.ndarray]
    sigma_mm: Optional[float]
    core_size: int
    labels: np.ndarray
    reason: str


class MultiFrameDBSCANFilter:
    """Multi-frame DBSCAN filter for depth-penetration rejection."""

    def __init__(
        self,
        window_size: int = 15,
        eps_mm: float = 15.0,
        min_pts: int = 8,
        sigma_thresh_mm: float = 3.0,
    ) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        if eps_mm <= 0:
            raise ValueError("eps_mm must be positive")
        if min_pts <= 0:
            raise ValueError("min_pts must be positive")
        if sigma_thresh_mm <= 0:
            raise ValueError("sigma_thresh_mm must be positive")

        self.window_size = int(window_size)
        self.eps_mm = float(eps_mm)
        self.min_pts = int(min_pts)
        self.sigma_thresh_mm = float(sigma_thresh_mm)
        self._window: deque[np.ndarray] = deque(maxlen=self.window_size)

    def add_observation(self, point_xyz_mm: np.ndarray) -> FilterResult:
        point = np.asarray(point_xyz_mm, dtype=float).reshape(-1)
        if point.size != 3:
            raise ValueError("point_xyz_mm must have exactly 3 elements")

        self._window.append(point)

        if len(self._window) < self.window_size:
            return FilterResult(
                locked=False,
                p_final=None,
                sigma_mm=None,
                core_size=0,
                labels=np.array([], dtype=int),
                reason="collecting",
            )

        points = np.vstack(self._window)
        labels = self._dbscan(points)
        positive_labels = labels[labels > 0]
        if positive_labels.size == 0:
            return FilterResult(
                locked=False,
                p_final=None,
                sigma_mm=None,
                core_size=0,
                labels=labels,
                reason="no_core_cluster",
            )

        label_values, label_counts = np.unique(positive_labels, return_counts=True)
        dominant_label = label_values[int(np.argmax(label_counts))]
        core_points = points[labels == dominant_label]
        core_size = int(core_points.shape[0])
        if core_size == 0:
            return FilterResult(
                locked=False,
                p_final=None,
                sigma_mm=None,
                core_size=0,
                labels=labels,
                reason="no_core_cluster",
            )

        p_final = np.mean(core_points, axis=0)
        sigma_mm = float(np.sqrt(np.mean(np.sum((core_points - p_final) ** 2, axis=1))))
        locked = core_size >= self.min_pts and sigma_mm < self.sigma_thresh_mm
        if locked:
            reason = "locked"
        elif core_size < self.min_pts:
            reason = "insufficient_core_size"
        else:
            reason = "sigma_not_converged"

        return FilterResult(
            locked=locked,
            p_final=p_final,
            sigma_mm=sigma_mm,
            core_size=core_size,
            labels=labels,
            reason=reason,
        )

    def _dbscan(self, points: np.ndarray) -> np.ndarray:
        labels = np.zeros(points.shape[0], dtype=int)
        cluster_id = 0

        for idx in range(points.shape[0]):
            if labels[idx] != 0:
                continue

            neighbors = self._region_query(points, idx)
            if len(neighbors) < self.min_pts:
                labels[idx] = -1
                continue

            cluster_id += 1
            self._grow_cluster(points, labels, idx, neighbors, cluster_id)

        return labels

    def _grow_cluster(
        self,
        points: np.ndarray,
        labels: np.ndarray,
        seed_idx: int,
        neighbors: list[int],
        cluster_id: int,
    ) -> None:
        labels[seed_idx] = cluster_id
        queue = list(neighbors)
        cursor = 0

        while cursor < len(queue):
            point_idx = queue[cursor]

            if labels[point_idx] == -1:
                labels[point_idx] = cluster_id
            elif labels[point_idx] == 0:
                labels[point_idx] = cluster_id
                point_neighbors = self._region_query(points, point_idx)
                if len(point_neighbors) >= self.min_pts:
                    queue.extend(point_neighbors)

            cursor += 1

    def _region_query(self, points: np.ndarray, idx: int) -> list[int]:
        deltas = points - points[idx]
        dist = np.linalg.norm(deltas, axis=1)
        return np.where(dist <= self.eps_mm)[0].tolist()

    def get_window_points(self) -> np.ndarray:
        if len(self._window) == 0:
            return np.empty((0, 3), dtype=float)
        return np.vstack(self._window)
