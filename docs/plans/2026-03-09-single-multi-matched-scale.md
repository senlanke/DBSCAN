# Single Multi Matched Scale Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the single-target publication views use the same display span as the multi-target views, while keeping the single-target camera window centered around the single target rather than copying the multi-target absolute coordinates.

**Architecture:** Keep the shared fixed publication range model, but change the single-target fixed ranges so their span matches the multi-target raw and cluster spans. Recenter the single-target absolute coordinates around the single-target location so the figure keeps the same framing logic with unified scale.

**Tech Stack:** Python, NumPy, Matplotlib, pytest

---

### Task 1: Lock the single-target fixed ranges to the multi-target spans

**Files:**
- Modify: `tests/test_visualization_utils.py`
- Test: `tests/test_visualization_utils.py`

**Step 1: Write the failing test**

Update the test expectations so `single` uses the same span as `multi`:

- raw span:
  - `x` width `= 90`
  - display `z` width `= 132`
  - display `y` width `= 80`
- cluster span:
  - `x` width `= 74`
  - display `z` width `= 128`
  - display `y` width `= 64`

and assert the chosen recentered fixed ranges explicitly.

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL because `single` still uses narrower ranges.

**Step 3: Write minimal implementation**

Update the single-target fixed range constants in `viz_utils.py`.

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

Confirm single-target framing now feels matched to the multi-target scale rather than tighter than it.

**Step 4: Commit**

Repository is not a git worktree here, so skip commit.
