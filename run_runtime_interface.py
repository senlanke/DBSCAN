from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterator

try:
    from DBSCAN.runtime_interface import DBSCANRuntimeInterface
except ModuleNotFoundError:
    from runtime_interface import DBSCANRuntimeInterface


def _line_iterator(input_jsonl: str | None) -> Iterator[str]:
    if input_jsonl is None:
        for line in sys.stdin:
            yield line
        return
    path = Path(input_jsonl)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            yield line


def _parse_points(payload: dict):
    if "points" in payload:
        return payload["points"]
    if "point" in payload:
        return payload["point"]
    raise ValueError("payload must contain 'point' or 'points'")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DBSCAN runtime IO interface for camera XYZ stream (JSON lines in -> JSON lines out)."
    )
    parser.add_argument("--mode", choices=["single", "multi"], default="single")
    parser.add_argument("--realtime", action="store_true", help="Enable realtime runtime visualization")
    parser.add_argument("--input-jsonl", default=None, help="Input JSONL file path. If omitted, read from stdin.")
    parser.add_argument("--output-jsonl", default=None, help="Optional output JSONL file path")
    parser.add_argument("--window-size", type=int, default=15)
    parser.add_argument("--eps-mm", type=float, default=15.0)
    parser.add_argument("--min-pts", type=int, default=8)
    parser.add_argument("--sigma-thresh-mm", type=float, default=3.0)
    parser.add_argument("--association-dist-thresh-mm", type=float, default=80.0)
    parser.add_argument("--max-missed-frames", type=int, default=3)
    args = parser.parse_args()

    runtime = DBSCANRuntimeInterface(
        mode=args.mode,
        window_size=args.window_size,
        eps_mm=args.eps_mm,
        min_pts=args.min_pts,
        sigma_thresh_mm=args.sigma_thresh_mm,
        association_dist_thresh_mm=args.association_dist_thresh_mm,
        max_missed_frames=args.max_missed_frames,
        realtime=args.realtime,
    )

    output_file = None
    if args.output_jsonl:
        output_path = Path(args.output_jsonl)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_file = output_path.open("w", encoding="utf-8")

    try:
        for line in _line_iterator(args.input_jsonl):
            raw = line.strip()
            if not raw:
                continue
            payload = json.loads(raw)
            points = _parse_points(payload)
            timestamp = payload.get("timestamp")
            out = runtime.process_frame(points, timestamp=timestamp)
            out_line = DBSCANRuntimeInterface.dumps_output(out)
            print(out_line, flush=True)
            if output_file is not None:
                output_file.write(out_line + "\n")
                output_file.flush()
    finally:
        if output_file is not None:
            output_file.close()


if __name__ == "__main__":
    main()

