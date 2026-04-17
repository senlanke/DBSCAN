# Multi Figure Split Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让多目标论文图从脚本直接导出左右语义对应的单图 PNG/GIF，而不是裁切现有拼接图。

**Architecture:** 抽取多目标左图和右图的共享绘制函数，双图脚本继续复用它们；新增单图导出函数和主函数调用路径，分别生成 observed/tracking 两套静态图与动画。

**Tech Stack:** Python, matplotlib, Pillow, pytest

---

### Task 1: Add failing export test

**Files:**
- Modify: `/home/kesl/ke/DBSCAN/tests/test_visualization_utils.py`

**Step 1: Write the failing test**

增加一个测试，调用新的多目标单图导出函数，断言生成：

- `publication_multi_observed.png`
- `publication_multi_tracking.png`
- `publication_multi_observed.gif`
- `publication_multi_tracking.gif`

并检查 GIF 帧数为 20。

**Step 2: Run test to verify it fails**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: FAIL because export helpers do not exist yet.

### Task 2: Extract shared multi-panel renderers

**Files:**
- Modify: `/home/kesl/ke/DBSCAN/viz_utils.py`
- Modify: `/home/kesl/ke/DBSCAN/visualize_multi_target_demo.py`
- Modify: `/home/kesl/ke/DBSCAN/animate_multi_target_demo.py`

**Step 1: Write minimal implementation**

在 `viz_utils.py` 中新增：

- 多目标 observed 单轴绘制函数
- 多目标 tracking 单轴绘制函数
- 单图 figure/axis 创建助手

让现有双图脚本改为调用共享函数。

**Step 2: Run targeted test**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

### Task 3: Add direct export helpers for single-panel PNG/GIF

**Files:**
- Modify: `/home/kesl/ke/DBSCAN/visualize_multi_target_demo.py`
- Modify: `/home/kesl/ke/DBSCAN/animate_multi_target_demo.py`

**Step 1: Write minimal implementation**

新增可直接导出：

- `publication_multi_observed.png`
- `publication_multi_tracking.png`
- `publication_multi_observed.gif`
- `publication_multi_tracking.gif`

**Step 2: Run tests**

Run: `conda run -n ke pytest tests/test_visualization_utils.py -q`

Expected: PASS

### Task 4: Generate outputs and verify

**Files:**
- No code changes required if previous steps pass

**Step 1: Export figures**

Run the relevant scripts to generate both PNG and GIF single-panel outputs.

**Step 2: Verify output files**

Check that:

- all four files exist
- PNG sizes are non-zero
- GIF frame count is 20

**Step 3: Run full test suite**

Run: `conda run -n ke pytest tests -q`

Expected: PASS
