# Pseudo Target Limitation Design

**Date:** 2026-03-11

**Goal:** Explain why the current demo noise does not form a pseudo target, then add a contrasting runnable demo where persistent, spatially separated false detections do become a pseudo target.

## Problem Statement

The current multi-target publication figure shows several red noise points. A reasonable reader may ask why those points are not recognized as a new target.

This must be answered explicitly in the technical reference document, otherwise the method description is incomplete.

At the same time, the thesis should also state the method's limitation: if false detections become sufficiently persistent and spatially separated, the current tracker plus windowed DBSCAN can indeed lock onto a pseudo target.

## Design

The work is split into two parts:

1. **Explanatory documentation**
   - explain why the current red noise points remain noise
   - formalize the conditions under which false detections do not form a cluster
   - formalize the conditions under which they can become a pseudo target

2. **Runnable counterexample demo**
   - add a dedicated frame generator for a persistent false target
   - add a command-line script that runs the tracker on this data and prints the emergence of the pseudo track

## Core Technical Explanation

Current publication noise does not become a pseudo target because:

- it appears only in a few frames
- it remains associated with an existing real track due to lateral proximity
- its count is below `MinPts`, so the track-internal DBSCAN cannot form a stable cluster from those points alone

The pseudo-target counterexample must enforce the opposite:

- the false detections persist for at least `window_size` frames
- they remain spatially compact across time
- they are laterally separated enough from true targets to force creation of a new track

## Deliverables

- documentation update in `docs/DBSCAN_theory_and_project_reference.md`
- new demo generator in `viz_utils.py`
- new runnable script `run_pseudo_target_demo.py`
- regression-style tests proving the pseudo target can appear
