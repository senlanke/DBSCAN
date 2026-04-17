# Third Multi Target Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a third stable target to the multi-target publication demo so the tracking figures show three normal targets instead of two.

**Architecture:** Extend the shared multi-target demo generator in `viz_utils.py` with a third stable center `C=(142, 6, 354)`. Keep the existing plotting pipeline unchanged so the new target flows naturally through snapshot collection, clustering, and publication rendering.

**Tech Stack:** Python, NumPy, Matplotlib, pytest

---

### Task 1: Lock the third stable target in tests

**Files:**
- Modify: `tests/test_visualization_utils.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Assert:

```python
def test_multi_demo_centers_include_third_stable_target():
    from DBSCAN.viz_utils import MULTI_DEMO_CENTERS

    assert np.allclose(MULTI_DEMO_CENTERS["C"], np.array([142.0, 6.0, 354.0]))
```

and:

```python
def test_multi_demo_frames_now_contain_three_targets_per_frame():
    from DBSCAN.viz_utils import build_multi_target_demo_frames

    frames = build_multi_target_demo_frames(num_frames=4)
    assert all(frame.shape == (3, 3) for frame in frames)
```

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL because only two stable targets exist today.

**Step 3: Write minimal implementation**

Update `MULTI_DEMO_CENTERS` and `build_multi_target_demo_frames()` in `viz_utils.py`.

**Step 4: Run test to verify it passes**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

**Step 5: Commit**

Repository is not a git worktree here, so skip commit.

### Task 2: Regenerate and inspect multi-target publication outputs

**Files:**
- Modify: `output/publication_multi.png`
- Modify: `output/publication_multi.gif`

**Step 1: Regenerate outputs**

Run:

```bash
conda run -n ke python visualize_multi_target_demo.py --output output/publication_multi.png
conda run -n ke python animate_multi_target_demo.py --output output/publication_multi.gif
```

**Step 2: Run full verification**

Run: `conda run -n ke pytest tests -q`

Expected: PASS

**Step 3: Inspect outputs**

Confirm three stable targets appear in both raw and clustered publication views.

**Step 4: Commit**

Repository is not a git worktree here, so skip commit.
