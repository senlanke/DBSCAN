# Publication-Grade DBSCAN Animation Design

**Date:** 2026-03-09

## Goal

Upgrade the single-target and multi-target DBSCAN visualization outputs so that:

- GIFs are suitable as supplementary material for an SCI Q1 paper.
- The last frame can be used directly as a publication-quality figure.
- The rendering stack shares a consistent visual language across static and animated outputs.
- Existing behavior issues in target association and visualization state handling are corrected during the refactor.

## Scope

In scope:

- `animate_demo.py`
- `animate_multi_target_demo.py`
- `visualize_demo.py`
- `visualize_multi_target_demo.py`
- shared plotting/data helpers
- targeted tracker and visualization bug fixes

Out of scope:

- replacing the DBSCAN algorithm itself
- adding external plotting dependencies beyond matplotlib/numpy
- redesigning the runtime realtime viewer

## User Intent

The GIFs are primarily supplementary-material outputs. The paper will use the last frame as a static figure. That means the rendering should optimize for:

- print-safe colors
- low-clutter composition
- clear distinction between raw observations, clustered cores, noise, and final centers
- consistent typography and framing across single-target and multi-target outputs

## Visual Direction

### Global style

- white background
- publication-style sans-serif typography
- thin, neutral grids
- high contrast but restrained color palette
- minimal legend chrome
- fixed viewing angle for reproducibility

### Semantic color mapping

- raw/history observations: muted blue-gray
- current frame observations: deep blue
- dominant/core cluster: green or track-specific scientific palette
- noise / penetration outliers: desaturated red-gray
- final center / `P_final`: warm highlight color with small footprint
- bounding box / emphasis lines: dark neutral or track color, not pure black unless needed

### Layout

Single-target:

- left: raw observations over time
- right: DBSCAN clustering result
- no separate sigma convergence subplot in publication outputs

Multi-target:

- left: raw detection history and current detections
- right: track-wise clustering result with stable colors
- compact annotation block for active/locked tracks and parameters

## Architecture

Introduce a shared visualization utility module to centralize:

- synthetic demo data generation
- publication rcParams and axes styling
- shared palettes
- 3D box drawing
- convergence line drawing
- deterministic point jitter
- stronger publication-specific point separation
- fixed two-panel publication layouts
- axis-limit computation
- legend deduplication
- multi-target snapshot precomputation for active and pruned tracks

The animation and static scripts become thin composition layers on top of these helpers.

## Behavior Fixes

### Tracker association

The current fallback association can force a far-away new point onto an existing track when detection count is not greater than track count. This should be replaced with a constrained fallback that preserves continuity under depth-only jumps without allowing arbitrary large lateral reassignment.

Recommended rule:

- primary association remains full 3D nearest-neighbor with threshold
- fallback association is allowed only for remaining pairs whose XY distance is within the association threshold
- unmatched far points remain eligible to create new tracks

This preserves robustness against penetration outliers while avoiding false identity carry-over.

### Multi-target static visualization

Current static visualization assumes all historically seen tracks still exist at the final frame. That breaks if a track is pruned. Snapshot generation should preserve the last known visualization state for each track so static plots can render historical tracks safely.

## Testing Strategy

Add tests for:

- far-away unmatched point should create a new track rather than hijack an old one
- depth-jump continuity remains supported by association fallback
- precomputed visualization snapshots retain pruned-track state without crashing consumers

Existing tests must continue to pass unchanged.

## Acceptance Criteria

- `pytest tests -q` passes
- both GIF scripts render successfully
- both static visualization scripts render successfully
- single-target and multi-target outputs share a consistent publication style
- final frames are suitable for direct insertion into a manuscript after cropping only
