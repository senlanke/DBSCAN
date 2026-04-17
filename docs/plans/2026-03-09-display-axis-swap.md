# Display Axis Swap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Render all publication figures using display axis order `X-Z-Y` without changing the underlying DBSCAN/tracking data model.

**Architecture:** Add shared display-axis transform helpers in `viz_utils.py`, then update all publication scripts to pass their points through the display mapping before plotting. Keep fixed publication ranges shared and map them to display axes through a helper to avoid duplicated swap logic.

**Tech Stack:** Python, NumPy, Matplotlib, pytest

---

### Task 1: Lock display-axis swap behavior in tests

**Files:**
- Modify: `tests/test_visualization_utils.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Add tests like:

```python
def test_to_display_points_swaps_y_and_z():
    from DBSCAN.viz_utils import to_display_points

    pts = np.array([[1.0, 2.0, 3.0]])
    assert np.allclose(to_display_points(pts), np.array([[1.0, 3.0, 2.0]]))


def test_publication_fixed_ranges_are_mapped_to_display_axes():
    from DBSCAN.viz_utils import publication_display_ranges

    xlim, ylim, zlim = publication_display_ranges("single", "raw")
    assert xlim == (92.0, 128.0)
    assert ylim == (335.0, 645.0)
    assert zlim == (-50.0, -18.0)
```

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL because the helpers do not yet exist.

**Step 3: Write minimal implementation**

Add the display-axis helpers to `viz_utils.py`.

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.

### Task 2: Route all publication plots through the shared display mapping

**Files:**
- Modify: `viz_utils.py`
- Modify: `visualize_demo.py`
- Modify: `animate_demo.py`
- Modify: `visualize_multi_target_demo.py`
- Modify: `animate_multi_target_demo.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Add a test that `publication_axis_labels()` returns `("X (mm)", "Z (mm)", "Y (mm)")`.

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL before the helper exists.

**Step 3: Write minimal implementation**

- Add shared label helper.
- Update `style_3d_axis(...)` to use display labels.
- Update scatter plotting to use display-mapped points.
- Update line and box helpers to draw in display coordinates.
- Use the shared display-range helper in all four publication scripts.

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.

### Task 3: Regenerate and inspect publication assets

**Files:**
- Modify: `output/publication_single.png`
- Modify: `output/publication_single.gif`
- Modify: `output/publication_multi.png`
- Modify: `output/publication_multi.gif`

**Step 1: Regenerate figures**

Run:

```bash
conda run -n ke python visualize_demo.py --output output/publication_single.png
conda run -n ke python visualize_multi_target_demo.py --output output/publication_multi.png
conda run -n ke python animate_demo.py --output output/publication_single.gif
conda run -n ke python animate_multi_target_demo.py --output output/publication_multi.gif
```

**Step 2: Run full verification**

Run: `conda run -n ke pytest tests -q`

Expected: PASS

**Step 3: Inspect outputs**

Confirm:

- plotted axes read `X-Z-Y`
- `Y` and `Z` are visually swapped in both static and animated outputs
- wireframe boxes and connection lines align with the swapped display axes

**Step 4: Commit**

Repository is not a git worktree here, so skip commit.
