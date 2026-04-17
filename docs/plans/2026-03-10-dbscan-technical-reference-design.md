# DBSCAN Technical Reference Design

**Date:** 2026-03-10

**Goal:** Produce a thesis-grade technical reference document that explains standard DBSCAN theory from primary sources and contrasts it with the exact engineering design implemented in this repository.

## Audience

- thesis author
- reviewer who needs to understand both the standard algorithm and the repository-specific adaptation
- engineer who must reproduce the method from the document alone

## Scope

The document must cover two layers clearly and separately:

1. **Standard DBSCAN theory**
   - formal definitions
   - cluster formation logic
   - algorithm flow
   - parameter meanings
   - complexity and strengths/limits

2. **Repository implementation**
   - sliding-window single-target filter
   - dominant-cluster center estimation
   - convergence metric `sigma_mm`
   - multi-target association and lifecycle
   - runtime input/output interface

## Source Policy

### Standard theory

Use primary or first-order sources only, centered on the original DBSCAN paper:

- Martin Ester, Hans-Peter Kriegel, Jörg Sander, Xiaowei Xu, 1996
- supplemental metadata pages only when needed for bibliographic confirmation

### Repository implementation

Use current repository files as the sole implementation authority:

- `multiframe_dbscan_filter.py`
- `multi_target_dbscan_tracker.py`
- `runtime_interface.py`
- relevant tests

No implementation claims should exceed what the code does.

## Document Structure

1. Introduction and problem statement
2. Standard DBSCAN theory
3. Mathematical workflow of standard DBSCAN
4. Repository single-target method
5. Repository multi-target extension
6. Runtime interface and system integration
7. Parameter interpretation and tuning logic
8. Comparison between standard DBSCAN and this project
9. Advantages, limitations, and applicable conditions
10. Reference list

## Writing Rules

- Write in formal Chinese.
- Keep notation consistent across theory and implementation.
- Include formulas for all key definitions and project-specific metrics.
- Distinguish “standard DBSCAN” from “this project’s engineering adaptation” at every stage.
- Make the document standalone enough to support thesis writing.

## Deliverable

Create one main document in `docs/` as the canonical technical reference, with bibliography links at the end.
