# Publication Animation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build publication-grade single-target and multi-target DBSCAN visual outputs, remove plotting redundancy, and fix tracker/visualization edge cases.

**Architecture:** Add a shared visualization utility module for data generation, styling, and plot primitives, then refactor the static and animated scripts to compose around that module. Fix the multi-target association fallback and precompute persistent visualization snapshots so animation and static rendering share safe, deterministic state.

**Tech Stack:** Python, numpy, matplotlib, pytest

---

### Task 1: Lock in failing regression tests

**Files:**
- Create: `tests/test_visualization_utils.py`
- Modify: `tests/test_multi_target_dbscan_tracker.py`

**Step 1: Write the failing test**

Add tests for:

```python
def test_far_unmatched_point_creates_new_track_instead_of_reusing_old_one():
    ...

def test_xy_close_depth_jump_keeps_track_continuity():
    ...

def test_collect_multi_target_snapshots_keeps_last_state_of_pruned_tracks():
    ...
```

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_multi_target_dbscan_tracker.py tests/test_visualization_utils.py -q`

Expected:

- tracker regression test fails because current fallback reuses old track for far point
- visualization utils test fails because shared snapshot helper does not exist yet

**Step 3: Write minimal implementation**

Implement only enough code to:

- constrain fallback reassignment in tracker
- provide a minimal snapshot helper module/API required by the tests

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_multi_target_dbscan_tracker.py tests/test_visualization_utils.py -q`

Expected: PASS

### Task 2: Introduce shared visualization utilities

**Files:**
- Create: `viz_utils.py`
- Modify: `__init__.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Add assertions for shared helper behavior such as:

- deterministic demo data shape
- snapshot state retention
- semantic helper outputs where practical

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL for missing imports/functions

**Step 3: Write minimal implementation**

Implement shared helpers for:

- publication style setup
- single/multi demo data generation
- dominant label lookup
- 3D box drawing
- convergence line drawing
- deterministic point spreading
- adaptive box sizing
- legend deduplication
- axis-limit computation
- multi-target snapshot collection

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

### Task 3: Refactor single-target static and animated output

**Files:**
- Modify: `visualize_demo.py`
- Modify: `animate_demo.py`
- Modify: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Add a focused test for any new single-target helper used to keep threshold/style behavior parameterized instead of hardcoded.

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL due to missing helper or incorrect hardcoded threshold behavior

**Step 3: Write minimal implementation**

Refactor both scripts to:

- import shared demo/style helpers
- apply publication-style two-panel layout
- remove the convergence subplot
- use stronger deterministic point separation
- force a publication-visible target box
- improve final frame readability and legend placement

**Step 4: Run targeted verification**

Run:

- `conda run -n ke pytest tests/test_visualization_utils.py tests/test_multiframe_dbscan_filter.py -q`
- `conda run -n ke python animate_demo.py --output output/publication_single.gif`
- `conda run -n ke python visualize_demo.py --output output/publication_single.png`

Expected:

- tests pass
- files are generated successfully

### Task 4: Refactor multi-target static and animated output

**Files:**
- Modify: `visualize_multi_target_demo.py`
- Modify: `animate_multi_target_demo.py`
- Modify: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Add or extend tests to verify multi-target snapshot consumption and persistent historical state are safe after pruning.

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py tests/test_multi_target_dbscan_tracker.py -q`

Expected: FAIL if the refactor still depends on active-only final tracks

**Step 3: Write minimal implementation**

Refactor both scripts to:

- import shared demo/style helpers
- use precomputed persistent snapshots
- render stable track colors and cleaner annotations
- reduce label clutter to avoid overlap
- use stronger deterministic point separation
- force a publication-visible target box
- make the final frame publication-ready

**Step 4: Run targeted verification**

Run:

- `conda run -n ke pytest tests/test_visualization_utils.py tests/test_multi_target_dbscan_tracker.py -q`
- `conda run -n ke python animate_multi_target_demo.py --output output/publication_multi.gif`
- `conda run -n ke python visualize_multi_target_demo.py --output output/publication_multi.png`

Expected:

- tests pass
- files are generated successfully

### Task 5: Final verification

**Files:**
- Modify: as needed from previous tasks

**Step 1: Run full test suite**

Run: `conda run -n ke pytest tests -q`

Expected: PASS

**Step 2: Regenerate polished outputs**

Run:

- `conda run -n ke python animate_demo.py --output output/publication_single.gif`
- `conda run -n ke python animate_multi_target_demo.py --output output/publication_multi.gif`
- `conda run -n ke python visualize_demo.py --output output/publication_single.png`
- `conda run -n ke python visualize_multi_target_demo.py --output output/publication_multi.png`

Expected: all outputs generated successfully

**Step 3: Review deliverables**

Confirm:

- publication-style visuals are consistent
- last frames are manuscript-ready
- no behavior regressions are introduced
