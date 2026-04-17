# DBSCAN 多帧聚类复现说明（命令与参数速查）

## 1. 目录说明
- 本目录：`/home/kesl/ke/DBSCAN`
- 你当前常用目录：`/home/kesl/ke/improved_rrt_robot`

注意：如果在 `improved_rrt_robot` 下执行，脚本路径需要写成 `../DBSCAN/...`。

## 2. 核心默认参数
- `window_size = 15`
- `eps_mm = 15.0`
- `min_pts = 8`
- `sigma_thresh_mm = 3.0`

多目标关联默认参数：
- `association_dist_thresh_mm = 80.0`
- `max_missed_frames = 3`

可视化包围框默认参数：
- `box_w_mm = 30.0`
- `box_l_mm = 30.0`
- `box_h_mm = 30.0`

说明：当前可视化已改为“自适应紧贴点云”的包围框，以上参数作为包围框**最大尺寸上限**。

## 3. 常用运行指令

### 3.1 在 `/home/kesl/ke` 下执行

单目标文字演示：
```bash
conda run -n ke python DBSCAN/run_demo.py
```

多目标文字演示：
```bash
conda run -n ke python DBSCAN/run_multi_target_demo.py
```

单目标静态图：
```bash
conda run -n ke python DBSCAN/visualize_demo.py \
  --output DBSCAN/output/dbscan_multiframe_demo.png
```

多目标静态图：
```bash
conda run -n ke python DBSCAN/visualize_multi_target_demo.py \
  --output DBSCAN/output/multi_target_tracker_demo.png
```

单目标 GIF：
```bash
conda run -n ke python DBSCAN/animate_demo.py \
  --output DBSCAN/output/dbscan_multiframe_animation.gif \
  --fps 3
```

多目标 GIF：
```bash
conda run -n ke python DBSCAN/animate_multi_target_demo.py \
  --output DBSCAN/output/multi_target_tracker_animation.gif \
  --fps 3
```

运行测试：
```bash
conda run -n ke pytest DBSCAN/tests -q
```

### 3.2 在 `/home/kesl/ke/improved_rrt_robot` 下执行

单目标 GIF：
```bash
conda run -n ke python ../DBSCAN/animate_demo.py \
  --output ../DBSCAN/output/dbscan_multiframe_animation.gif \
  --fps 3
```

多目标 GIF：
```bash
conda run -n ke python ../DBSCAN/animate_multi_target_demo.py \
  --output ../DBSCAN/output/multi_target_tracker_animation.gif \
  --fps 3
```

## 4. 脚本参数清单

### 4.1 `visualize_demo.py`
- `--txt`：可选，输入 txt 文件（每行形如 `[x, y, z]`）
- `--output`：输出图片路径（默认 `DBSCAN/output/dbscan_multiframe_demo.png`）
- `--window-size`（默认 `15`）
- `--eps-mm`（默认 `15.0`）
- `--min-pts`（默认 `8`）
- `--sigma-thresh-mm`（默认 `3.0`）
- `--box-w-mm`（默认 `30.0`，作为自适应框最大宽度）
- `--box-l-mm`（默认 `30.0`，作为自适应框最大长度）
- `--box-h-mm`（默认 `30.0`，作为自适应框最大高度）

### 4.2 `visualize_multi_target_demo.py`
- `--output`（默认 `DBSCAN/output/multi_target_tracker_demo.png`）
- `--box-w-mm`（默认 `30.0`，作为自适应框最大宽度）
- `--box-l-mm`（默认 `30.0`，作为自适应框最大长度）
- `--box-h-mm`（默认 `30.0`，作为自适应框最大高度）

### 4.3 `animate_demo.py`
- `--output`（默认 `DBSCAN/output/dbscan_multiframe_animation.gif`）
- `--window-size`（默认 `15`）
- `--eps-mm`（默认 `15.0`）
- `--min-pts`（默认 `8`）
- `--sigma-thresh-mm`（默认 `3.0`）
- `--box-w-mm`（默认 `30.0`，作为自适应框最大宽度）
- `--box-l-mm`（默认 `30.0`，作为自适应框最大长度）
- `--box-h-mm`（默认 `30.0`，作为自适应框最大高度）
- `--fps`（默认 `3`）

### 4.4 `animate_multi_target_demo.py`
- `--output`（默认 `DBSCAN/output/multi_target_tracker_animation.gif`）
- `--fps`（默认 `3`）
- `--window-size`（默认 `15`）
- `--eps-mm`（默认 `15.0`）
- `--min-pts`（默认 `8`）
- `--sigma-thresh-mm`（默认 `3.0`）
- `--association-dist-thresh-mm`（默认 `80.0`）
- `--max-missed-frames`（默认 `3`）
- `--box-w-mm`（默认 `30.0`，作为自适应框最大宽度）
- `--box-l-mm`（默认 `30.0`，作为自适应框最大长度）
- `--box-h-mm`（默认 `30.0`，作为自适应框最大高度）

## 5. 输出文件位置
默认都输出到：
- `DBSCAN/output/`

示例：
- `dbscan_multiframe_demo.png`
- `multi_target_tracker_demo.png`
- `dbscan_multiframe_animation.gif`
- `multi_target_tracker_animation.gif`

## 6. 输入/输出接口（对接相机数据）

### 6.1 Python 接口

核心类：
- `DBSCAN.runtime_interface.DBSCANRuntimeInterface`

最小示例（单目标）：
```python
from DBSCAN.runtime_interface import DBSCANRuntimeInterface

runtime = DBSCANRuntimeInterface(mode="single", realtime=False)
out = runtime.process_frame([110.2, -35.1, 349.9], timestamp=123)
print(out)  # dict
```

最小示例（多目标）：
```python
from DBSCAN.runtime_interface import DBSCANRuntimeInterface

runtime = DBSCANRuntimeInterface(mode="multi", realtime=False)
out = runtime.process_frame([[100.0, -30.0, 350.0], [260.0, 70.0, 360.0]], timestamp=1)
print(out["tracks"])
```

输出回调（输出接口）：
```python
def on_output(data: dict):
    print(data)

runtime.add_output_callback(on_output)
```

### 6.2 流式命令行接口（JSONL 输入 -> JSONL 输出）

脚本：
- `DBSCAN/run_runtime_interface.py`

在 `~/ke` 下运行：
```bash
conda run -n ke python DBSCAN/run_runtime_interface.py \
  --mode single \
  --input-jsonl /tmp/dbscan_runtime_single.jsonl
```

在 `~/ke/improved_rrt_robot` 下运行：
```bash
conda run -n ke python ../DBSCAN/run_runtime_interface.py \
  --mode multi \
  --input-jsonl /tmp/dbscan_runtime_multi.jsonl
```

开启实时显示（可选）：
```bash
conda run -n ke python ../DBSCAN/run_runtime_interface.py \
  --mode multi \
  --realtime \
  --input-jsonl /tmp/dbscan_runtime_multi.jsonl
```

### 6.3 输入格式

单目标每行 JSON（`point`）：
```json
{"timestamp": 1, "point": [110.0, -35.0, 350.0]}
```

多目标每行 JSON（`points`）：
```json
{"timestamp": 1, "points": [[100.0, -30.0, 350.0], [260.0, 70.0, 360.0]]}
```

### 6.4 输出格式（核心字段）

单目标输出：
- `mode`
- `timestamp`
- `frame_index`
- `input_points`
- `locked`
- `cluster_xyz_mm`
- `sigma_mm`
- `core_size`
- `reason`

多目标输出：
- `mode`
- `timestamp`
- `frame_index`
- `input_points`
- `active_track_count`
- `primary_track_id`
- `primary_cluster_xyz_mm`
- `tracks`（每条轨迹含 `track_id/locked/cluster_xyz_mm/sigma_mm/core_size/reason/missed_frames/age/last_observation_xyz_mm`）
