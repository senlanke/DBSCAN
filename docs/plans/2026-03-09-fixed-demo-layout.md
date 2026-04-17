# Fixed Demo Layout Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace adaptive publication-panel zooming with fixed demo ranges for single and multi figures, and move the multi-target demo centers closer together.

**Architecture:** Store fixed publication ranges in shared visualization helpers so the static and animated scripts reuse the same values. Update the multi-target demo generator to use the approved closer centers, then switch the publication scripts from adaptive focus logic to fixed shared ranges.

**Tech Stack:** Python, NumPy, Matplotlib, pytest

---

### Task 1: Lock fixed layout behavior in tests

**Files:**
- Modify: `tests/test_visualization_utils.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Add tests asserting:

```python
from DBSCAN.viz_utils import (
    MULTI_DEMO_CENTERS,
    PUBLICATION_FIXED_RANGES,
)

def test_publication_fixed_ranges_match_approved_demo_layout():
    assert PUBLICATION_FIXED_RANGES["single"]["raw"]["x"] == (92.0, 128.0)
    assert PUBLICATION_FIXED_RANGES["single"]["cluster"]["x"] == (96.0, 124.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["raw"]["x"] == (96.0, 186.0)
    assert PUBLICATION_FIXED_RANGES["multi"]["cluster"]["x"] == (106.0, 180.0)


def test_multi_demo_centers_match_publication_layout():
    assert np.allclose(MULTI_DEMO_CENTERS["A"], np.array([118.0, -18.0, 350.0]))
    assert np.allclose(MULTI_DEMO_CENTERS["B"], np.array([168.0, 22.0, 358.0]))
```

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL because the shared constants do not exist or do not match the approved values.

**Step 3: Write minimal implementation**

Add the shared fixed-range constants and closer multi-target centers to `viz_utils.py`.

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.

### Task 2: Replace adaptive publication ranges with fixed shared ranges

**Files:**
- Modify: `viz_utils.py`
- Modify: `visualize_demo.py`
- Modify: `animate_demo.py`
- Modify: `visualize_multi_target_demo.py`
- Modify: `animate_multi_target_demo.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Add tests asserting the fixed publication range helpers return the approved axes for:

- single raw panel
- single cluster panel
- multi raw panel
- multi cluster panel

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL before the scripts are wired to use the shared fixed ranges.

**Step 3: Write minimal implementation**

- Add a shared publication-range structure to `viz_utils.py`.
- Remove adaptive focus-limit calls from the four publication scripts.
- Use the shared fixed ranges directly in `style_3d_axis(...)`.

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.

### Task 3: Verify exported publication assets

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

Check that:

- Both single-target panels are enlarged with fixed ranges.
- Both multi-target panels use reduced ranges.
- The two multi-target boxes are closer together.
- Edge-only boxes remain visible.
- In-box points remain more spread than before.

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.
