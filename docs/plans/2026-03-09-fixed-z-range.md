# Fixed Z Range Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Widen the fixed publication `Z` ranges so high outlier points remain visible while preserving the fixed-layout publication style.

**Architecture:** Keep the existing fixed-layout approach and only update the shared `PUBLICATION_FIXED_RANGES` constants in `viz_utils.py`. Static and animated scripts already consume those shared constants, so widening the `Z` limits in one place updates all outputs.

**Tech Stack:** Python, NumPy, Matplotlib, pytest

---

### Task 1: Lock widened fixed Z ranges in tests

**Files:**
- Modify: `tests/test_visualization_utils.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Assert the widened fixed `Z` ranges:

```python
def test_publication_fixed_ranges_include_high_outliers():
    from DBSCAN.viz_utils import PUBLICATION_FIXED_RANGES

    assert PUBLICATION_FIXED_RANGES["single"]["raw"]["z"] == (335.0, 645.0)
    assert PUBLICATION_FIXED_RANGES["single"]["cluster"]["z"] == (338.0, 645.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["raw"]["z"] == (338.0, 620.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["cluster"]["z"] == (342.0, 620.0)
```

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL because the current fixed `Z` ranges are lower.

**Step 3: Write minimal implementation**

Update `PUBLICATION_FIXED_RANGES` in `viz_utils.py`.

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.

### Task 2: Regenerate and verify publication outputs

**Files:**
- Modify: `output/publication_single.png`
- Modify: `output/publication_single.gif`
- Modify: `output/publication_multi.png`
- Modify: `output/publication_multi.gif`

**Step 1: Regenerate static figures**

Run:

```bash
conda run -n ke python visualize_demo.py --output output/publication_single.png
conda run -n ke python visualize_multi_target_demo.py --output output/publication_multi.png
```

**Step 2: Regenerate GIFs**

Run:

```bash
conda run -n ke python animate_demo.py --output output/publication_single.gif
conda run -n ke python animate_multi_target_demo.py --output output/publication_multi.gif
```

**Step 3: Run full verification**

Run: `conda run -n ke pytest tests -q`

Expected: PASS

**Step 4: Inspect outputs**

Confirm the high-`z` outlier points are now visible in the fixed-layout views.

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.
