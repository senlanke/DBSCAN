# Pseudo Target Limitation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a runnable pseudo-target counterexample demo and document both the current non-pseudo-target behavior and the limitation scenario in the main technical reference.

**Architecture:** Add a dedicated multi-frame demo generator that injects a persistent false target far enough from true targets to form its own track. Then document the contrast between transient in-track noise and persistent separated false detections.

**Tech Stack:** Python, NumPy, Markdown, pytest

---

### Task 1: Lock the pseudo-target scenario in tests

**Files:**
- Modify: `tests/test_visualization_utils.py`
- Modify: `tests/test_multi_target_dbscan_tracker.py`

**Step 1: Write failing tests**

Add tests that:

- the pseudo-target demo frames include four detections after the false target appears
- the tracker eventually produces four active tracks
- one extra locked track is spatially close to the designed false-target center

**Step 2: Run tests to verify failure**

Run:

```bash
conda run -n ke pytest tests/test_visualization_utils.py tests/test_multi_target_dbscan_tracker.py -q
```

Expected: FAIL before the new generator exists.

**Step 3: Implement minimal generator support**

Add the dedicated frame generator to `viz_utils.py`.

**Step 4: Re-run tests**

Expected: PASS

### Task 2: Add a runnable demo entry point

**Files:**
- Create: `run_pseudo_target_demo.py`

**Step 1: Implement the script**

The script should:

- build the pseudo-target frames
- run `MultiTargetDBSCANTracker`
- print frame-by-frame track state
- summarize whether a pseudo target locked

### Task 3: Update the technical reference

**Files:**
- Modify: `docs/DBSCAN_theory_and_project_reference.md`

**Step 1: Add explanation for current noise behavior**

Document why current transient red noise remains noise.

**Step 2: Add limitation subsection**

Document the sufficient conditions for false detections to become a pseudo target.

**Step 3: Reference the runnable demo**

Mention the new script path and intended use in thesis limitation analysis.

### Task 4: Final verification

**Files:**
- Modify: `output/` files only if a visual artifact is produced

**Step 1: Run tests**

Run:

```bash
conda run -n ke pytest tests -q
```

**Step 2: Run the demo**

Run:

```bash
conda run -n ke python run_pseudo_target_demo.py
```

**Step 3: Confirm the document and demo are consistent**
