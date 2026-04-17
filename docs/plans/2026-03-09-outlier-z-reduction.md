# Outlier Z Reduction Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reduce the demo outlier `z` offsets to a moderate level and tighten the fixed publication `Z` ranges accordingly.

**Architecture:** Update the single-target injected outlier points and the multi-target added `z` offset in `viz_utils.py`, then shrink the fixed `Z` ranges in the shared publication constants. Since all publication scripts already consume the shared demo data and fixed ranges, no extra plotting logic changes are needed.

**Tech Stack:** Python, NumPy, Matplotlib, pytest

---

### Task 1: Lock the new outlier heights and fixed Z ranges

**Files:**
- Modify: `tests/test_visualization_utils.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Assert:

```python
def test_publication_fixed_ranges_use_tighter_moderate_z_spans():
    from DBSCAN.viz_utils import PUBLICATION_FIXED_RANGES

    assert PUBLICATION_FIXED_RANGES["single"]["raw"]["z"] == (335.0, 500.0)
    assert PUBLICATION_FIXED_RANGES["single"]["cluster"]["z"] == (338.0, 500.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["raw"]["z"] == (338.0, 470.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["cluster"]["z"] == (342.0, 470.0)
```

and:

```python
def test_single_demo_contains_moderate_high_z_outliers():
    from DBSCAN.viz_utils import build_single_target_demo_points

    zs = np.sort(build_single_target_demo_points()[:, 2])[-3:]
    assert np.allclose(zs, np.array([440.0, 460.0, 480.0]))
```

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL because the current outlier heights and ranges are higher.

**Step 3: Write minimal implementation**

Update the injected single-target outliers, the multi-target added `z` offset, and the shared fixed `Z` ranges in `viz_utils.py`.

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.

### Task 2: Regenerate publication outputs and verify

**Files:**
- Modify: `output/publication_single.png`
- Modify: `output/publication_single.gif`
- Modify: `output/publication_multi.png`
- Modify: `output/publication_multi.gif`

**Step 1: Regenerate outputs**

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

Confirm the outliers remain visible but the `Z` span is visibly tighter than before.

**Step 4: Commit**

Repository is not a git worktree here, so skip commit.
