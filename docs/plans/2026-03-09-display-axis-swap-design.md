# Display Axis Swap Design

**Date:** 2026-03-09

**Goal:** Swap the plotted `Y` and `Z` axes so publication figures are displayed in `X-Z-Y` order, while leaving the underlying point data and clustering logic unchanged.

## Decision

Apply the axis swap only in the visualization layer.

- Raw point data remains `x, y, z`
- DBSCAN and tracking remain `x, y, z`
- Displayed plots become `x, z, y`

This keeps algorithm semantics stable and makes the change fully reversible inside shared plotting helpers.

## Scope

The swap applies to:

- scatter points
- center markers
- center-connection lines
- wireframe boxes
- axis labels
- fixed publication axis ranges

The swap does not apply to:

- input file parsing
- clustering or tracking calculations
- stored point arrays

## Shared Helper Strategy

Add shared helpers in `viz_utils.py`:

- convert points from `x, y, z` to display `x, z, y`
- convert a single center from `x, y, z` to display `x, z, y`
- convert box dimensions from `(w=x, l=y, h=z)` to display dimensions `(x=w, y=h, z=l)`
- map fixed range dictionaries from original keys to display axes

This avoids scattering one-off swaps through each plotting script.

## Fixed Range Reorder

Publication fixed ranges remain explicit, but the displayed axis order becomes:

- `x` axis uses original `x`
- displayed `y` axis uses original `z`
- displayed `z` axis uses original `y`

So the publication layout is read and rendered as `X-Z-Y`.

## Validation

Tests should lock:

- point reorder helper returns `x,z,y`
- fixed publication ranges are routed to display axes in `x,z,y` order
- displayed labels read `X (mm)`, `Z (mm)`, `Y (mm)`

After implementation, regenerate PNG and GIF outputs and inspect them.
