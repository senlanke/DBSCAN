# Multi Figure Split Design

## Goal

将当前 `multi` 的双面板论文图拆成四个由脚本直接生成的独立产物，而不是对已有拼接图做后处理裁切。

## Context

当前多目标可视化由以下脚本生成：

- `/home/kesl/ke/DBSCAN/visualize_multi_target_demo.py`
- `/home/kesl/ke/DBSCAN/animate_multi_target_demo.py`

这两个脚本都使用一个双面板 figure：

- 左图：观测历史与当前检测
- 右图：轨迹内 DBSCAN 聚类、中心、包围框、噪声点与摘要框

直接裁切现有 `publication_multi.png` 和 `publication_multi.gif` 会破坏布局关系，因为：

- 双图的子图宽度不是简单等分
- 图例和摘要框依赖完整 figure 的 tight layout
- 动画帧内部元素的留白和渲染边界并不适合后处理裁切

## Requirements

新增四个独立输出：

- `output/publication_multi_observed.png`
- `output/publication_multi_tracking.png`
- `output/publication_multi_observed.gif`
- `output/publication_multi_tracking.gif`

要求：

- 由脚本直接生成，不做成品裁切
- 数据、颜色、坐标范围、视角与当前双图版本保持一致
- 双图旧输出继续可用
- 新输出命名与语义绑定，不依赖左右位置

## Recommended Approach

采用“共享绘图逻辑抽函数 + 双图/单图共用”的方式。

具体做法：

1. 将 `multi` 左图绘制逻辑抽成独立函数 `render_multi_observed_axis(...)`
2. 将 `multi` 右图绘制逻辑抽成独立函数 `render_multi_tracking_axis(...)`
3. 双图脚本继续调用这两个函数
4. 新增单图导出入口，分别创建单个 3D axis 并调用对应函数

这样能保证：

- 不重复实现核心绘图逻辑
- 单图和双图内容严格一致
- 后续只需维护一套视觉行为

## Testing

使用最小 TDD 约束：

- 新增测试调用新的多目标单图导出函数
- 断言 4 个文件被生成
- 断言 PNG 尺寸非零
- 断言 GIF 至少包含 1 帧，且与当前 demo 帧数一致为 20 帧

## Output Contract

建议新增一个统一导出入口，接受基础前缀并输出双图和单图，或者至少支持从脚本主函数中显式导出：

- `publication_multi.png`
- `publication_multi.gif`
- `publication_multi_observed.png`
- `publication_multi_tracking.png`
- `publication_multi_observed.gif`
- `publication_multi_tracking.gif`

本次任务只强制新增后四个单图产物，不改变既有双图文件名。
