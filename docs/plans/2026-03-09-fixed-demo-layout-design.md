# Fixed Demo Layout Design

**Date:** 2026-03-09

**Goal:** Replace adaptive cluster-panel zooming with a fixed publication layout so both left and right panels are enlarged in a repeatable way, while keeping the single-target and multi-target demos visually clear for GIF and PNG export.

## Context

The current publication figures use an adaptive result-panel zoom. That improves legibility, but the user wants a fixed-size presentation that produces the same view every time and does not depend on the current point distribution.

The multi-target demo also spreads the two targets too far apart for the desired paper figure. The user wants the true target centers moved closer together and the displayed axis ranges reduced accordingly.

## Chosen Approach

Use a fixed demo layout for the publication scripts:

- `single` gets one fixed range for the left panel and one fixed range for the right panel.
- `multi` gets one fixed range for the left panel and one fixed range for the right panel.
- `multi` demo source data is updated so the two real centers are closer together.
- No runtime adaptive zoom remains in the publication scripts for these demo outputs.

## Fixed View Specification

### Single-target demo

- Left panel fixed range:
  - `X=[92, 128]`
  - `Y=[-50, -18]`
  - `Z=[335, 367]`
- Right panel fixed range:
  - `X=[96, 124]`
  - `Y=[-46, -24]`
  - `Z=[338, 366]`

This keeps both panels enlarged while preserving some context in the left panel and stronger focus in the right panel.

### Multi-target demo

Update the true centers from a wide baseline to a closer baseline:

- Target A: `A=(118, -18, 350)`
- Target B: `B=(168, 22, 358)`

Fixed axis ranges:

- Left panel:
  - `X=[96, 186]`
  - `Y=[-38, 42]`
  - `Z=[338, 372]`
- Right panel:
  - `X=[106, 180]`
  - `Y=[-30, 34]`
  - `Z=[342, 370]`

This reduces empty space, keeps both targets separated, and makes the right-panel boxes and in-box points visibly clearer without adaptive zoom.

## Visual Rules Preserved

- Keep the edge-only box style.
- Keep smaller cluster markers.
- Keep stronger deterministic spreading for points inside the box.
- Apply the fixed layout to both PNG and GIF outputs.

## Testing

Add and update tests to lock in:

- Fixed single-target publication ranges.
- Fixed multi-target publication ranges.
- Updated multi-target demo center positions.
- Existing publication marker and box-style constraints.

## Notes

This is a demo-layout decision for publication assets. It is intentionally not generalized to arbitrary external input data.
