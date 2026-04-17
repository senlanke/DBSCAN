# DBSCAN 理论与本项目实现对照技术文档

**文档版本：** 2026-03-11  
**适用代码范围：** 当前仓库 `DBSCAN` 目录下的实现  
**文档目的：** 作为毕业论文写作与方法说明的技术参考材料，系统说明标准 DBSCAN 理论、数学定义、算法流程，以及本项目基于 DBSCAN 的工程化改造方法

---

## 1. 引言

### 1.1 问题背景

在三维感知任务中，输入通常表现为连续到达的空间点坐标流，即每一帧由一个或多个三维点

\[
\mathbf{p} = [x, y, z]^\top
\]

组成。若这些点直接来自视觉识别、深度估计或检测器输出，则常见问题包括：

- 偶发深度穿透点或飞点
- 部分帧没有检测结果
- 多目标场景下的目标身份不稳定
- 单帧坐标抖动较大，难以直接作为控制或定位结果

标准 DBSCAN 是一种经典的基于密度的聚类算法，适用于从含噪点集里提取高密度区域。本项目并未将 DBSCAN 作为一次性静态聚类工具使用，而是将其嵌入到一个面向在线三维坐标流的工程框架中，用于实现：

- **单目标稳态滤波**
- **多目标轨迹内稳定聚类**
- **运行时在线输入输出接口**

因此，本项目可以理解为：**以标准 DBSCAN 为核心、面向多帧三维点流稳定估计的工程化改造方案**。

### 1.2 文档结构

本文档分为两大部分：

1. **标准 DBSCAN 理论**
2. **本项目实现与标准理论的对照**

文中所有与“标准 DBSCAN”有关的定义，均以 Ester 等人在 1996 年提出的原始论文为基准；与“本项目”有关的描述，均以当前仓库代码实现为准。

---

## 2. 记号与符号约定

为避免理论部分与实现部分混淆，本文统一使用以下符号：

- 数据集或窗口点集：\(D\)
- 单个点：\(\mathbf{p}_i \in \mathbb{R}^3\)
- 两点间欧氏距离：\(\mathrm{dist}(\mathbf{p}_i,\mathbf{p}_j)\)
- 邻域半径：\(\varepsilon\)
- 最小邻域点数：\(\mathrm{MinPts}\)
- 第 \(k\) 个簇：\(C_k\)
- 本项目滑动窗口长度：\(N\)
- 本项目主簇中心：\(\mathbf{P}_{\text{final}}\)
- 本项目簇内离散度：\(\sigma\)
- 第 \(t\) 帧输入点：\(\mathbf{p}^{(t)}\)
- 第 \(m\) 条轨迹在第 \(t\) 帧的观测：\(\mathbf{o}_m^{(t)}\)

本项目所有坐标的物理单位均为毫米，即 `mm`。

---

## 3. 标准 DBSCAN 理论

## 3.1 算法思想

DBSCAN 全称为 **Density-Based Spatial Clustering of Applications with Noise**。其核心思想是：

> 若某一区域内点的局部密度足够高，则这些点应被视为同一簇；密度不足的点则应被视为噪声或边界点。

与基于质心的聚类方法不同，DBSCAN 不需要预先指定簇数，且能够识别任意形状的连通高密度区域，并天然具备噪声点剔除能力。

标准 DBSCAN 的核心输入参数只有两个：

- 邻域半径 \(\varepsilon\)
- 最小邻域点数 \(\mathrm{MinPts}\)

---

## 3.2 \(\varepsilon\)-邻域

对于数据集 \(D\) 中的任意一点 \(\mathbf{p}\)，其 \(\varepsilon\)-邻域定义为：

\[
N_\varepsilon(\mathbf{p}) = \left\{\mathbf{q}\in D \mid \mathrm{dist}(\mathbf{p}, \mathbf{q}) \le \varepsilon \right\}
\]

若使用欧氏距离，则有：

\[
\mathrm{dist}(\mathbf{p}, \mathbf{q}) = \|\mathbf{p} - \mathbf{q}\|_2
= \sqrt{\sum_{d=1}^{m}(p_d-q_d)^2}
\]

其中 \(m\) 为特征维数。本项目中 \(m=3\)。

---

## 3.3 核心点、边界点与噪声点

### 3.3.1 核心点

若某点 \(\mathbf{p}\) 的 \(\varepsilon\)-邻域内点数不少于 \(\mathrm{MinPts}\)，则称 \(\mathbf{p}\) 为核心点：

\[
|N_\varepsilon(\mathbf{p})| \ge \mathrm{MinPts}
\]

### 3.3.2 边界点

若某点本身不是核心点，但它位于某个核心点的 \(\varepsilon\)-邻域内，则通常可被并入某簇，称为边界点。

### 3.3.3 噪声点

若某点既不是核心点，也不属于任何核心点可扩展出的簇，则该点为噪声点。

从语义上看：

- 核心点决定簇的“密度支撑结构”
- 边界点附着在簇边界
- 噪声点不属于任何有效高密度区域

---

## 3.4 密度可达与密度相连

DBSCAN 的簇不是依靠“与质心距离最近”定义的，而是依靠密度连通性定义的。

### 3.4.1 直接密度可达

若满足：

1. \(\mathbf{q} \in N_\varepsilon(\mathbf{p})\)
2. \(\mathbf{p}\) 是核心点

则称 \(\mathbf{q}\) **从 \(\mathbf{p}\) 直接密度可达**。

### 3.4.2 密度可达

若存在点序列

\[
\mathbf{p}_1,\mathbf{p}_2,\dots,\mathbf{p}_n
\]

使得：

- \(\mathbf{p}_1 = \mathbf{p}\)
- \(\mathbf{p}_n = \mathbf{q}\)
- 对任意 \(i=1,\dots,n-1\)，\(\mathbf{p}_{i+1}\) 从 \(\mathbf{p}_i\) 直接密度可达

则称 \(\mathbf{q}\) **从 \(\mathbf{p}\) 密度可达**。

### 3.4.3 密度相连

若存在某点 \(\mathbf{o}\)，使得 \(\mathbf{p}\) 与 \(\mathbf{q}\) 都从 \(\mathbf{o}\) 密度可达，则称 \(\mathbf{p}\) 与 \(\mathbf{q}\) **密度相连**。

密度相连是标准 DBSCAN 里定义同一簇的关键关系。

---

## 3.5 标准簇定义

设 \(C \subseteq D\)。若同时满足以下两个条件，则 \(C\) 可视为 DBSCAN 意义下的一个簇：

### 3.5.1 最大性

若 \(\mathbf{p}\in C\)，且 \(\mathbf{q}\) 从 \(\mathbf{p}\) 密度可达，则 \(\mathbf{q}\in C\)。

### 3.5.2 连通性

对任意 \(\mathbf{p},\mathbf{q}\in C\)，\(\mathbf{p}\) 与 \(\mathbf{q}\) 必须密度相连。

因此，标准 DBSCAN 的簇本质上是一个**最大密度连通子集**。

---

## 3.6 标准 DBSCAN 算法流程

标准 DBSCAN 可简述为以下流程。

### 步骤 1：初始化

- 所有点初始均为“未访问”
- 当前簇编号初始化为 0

### 步骤 2：逐点遍历

对每个尚未处理的点 \(\mathbf{p}\)：

1. 计算其 \(\varepsilon\)-邻域 \(N_\varepsilon(\mathbf{p})\)
2. 若 \(|N_\varepsilon(\mathbf{p})| < \mathrm{MinPts}\)，则暂时将其标记为噪声
3. 否则，以 \(\mathbf{p}\) 为种子生成一个新簇

### 步骤 3：簇扩展

若种子点为核心点，则将其邻域中的点加入扩展队列。对队列中的点重复：

1. 若该点此前被标记为噪声，则改为当前簇成员
2. 若该点尚未归类，则归入当前簇
3. 若该点也是核心点，则把它的邻域点继续并入扩展队列

### 步骤 4：结束

直到所有点都被访问完毕。最终：

- 已归入簇的点构成若干密度连通簇
- 未被簇吸收的点为噪声

---

## 3.7 标准 DBSCAN 伪代码思想

其核心逻辑可以写为：

\[
\text{for each unvisited point } \mathbf{p}\in D
\]

\[
\quad N_\varepsilon(\mathbf{p}) \leftarrow \mathrm{RegionQuery}(\mathbf{p})
\]

\[
\quad \text{if } |N_\varepsilon(\mathbf{p})| < \mathrm{MinPts}
\Rightarrow \mathbf{p}\text{ is noise}
\]

\[
\quad \text{else create new cluster and expand from } \mathbf{p}
\]

其中 `RegionQuery` 的作用是返回与当前点距离不超过 \(\varepsilon\) 的全部点。

---

## 3.8 参数物理意义

### 3.8.1 \(\varepsilon\)

\(\varepsilon\) 决定局部密度的空间尺度。若 \(\varepsilon\) 过小，则会把同一簇拆碎；若 \(\varepsilon\) 过大，则会把不同簇错误连接。

### 3.8.2 \(\mathrm{MinPts}\)

\(\mathrm{MinPts}\) 决定一个区域至少需要多少点才能被认为具有足够密度。若取值过小，则噪声点容易误成簇；若取值过大，则真实稠密区域也可能被误判为噪声。

---

## 3.9 时间复杂度

标准 DBSCAN 的复杂度主要由邻域查询决定。

若采用空间索引结构支持高效范围查询，则原始论文指出平均复杂度可接近：

\[
O(n \log n)
\]

其中 \(n\) 为样本点数。

若不使用空间索引，而对每个点都直接与全体点计算距离，则复杂度会退化为：

\[
O(n^2)
\]

本项目的 DBSCAN 实现属于后一种，即窗口内暴力距离计算。

---

## 3.10 标准 DBSCAN 的优点与局限

### 优点

- 不需要预先指定簇数
- 能识别任意形状簇
- 能自然识别噪声点
- 对离群点有一定鲁棒性

### 局限

- 对 \(\varepsilon\) 与 \(\mathrm{MinPts}\) 较敏感
- 当不同区域的密度差异很大时，单组参数难以同时兼顾
- 若使用暴力邻域查询，大规模数据下复杂度较高

---

## 4. 本项目的单目标 DBSCAN 工程化实现

## 4.1 设计目标

本项目的单目标模块并不是为了输出“所有簇”，而是为了从连续三维点流中稳定估计一个可信的目标中心，尤其用于抑制深度穿透点、偶发离群点和帧间抖动。

其核心文件为：

- [multiframe_dbscan_filter.py](/home/kesl/ke/DBSCAN/multiframe_dbscan_filter.py)

工程思想可概括为：

> 不直接相信单帧点，而是在最近 \(N\) 帧内做一次 DBSCAN，并从最大主簇估计最终位置。

---

## 4.2 滑动窗口建模

设当前时刻为 \(t\)，窗口长度为 \(N\)。项目维护最近 \(N\) 帧观测构成的窗口：

\[
W_t = \left\{\mathbf{p}^{(t-N+1)}, \mathbf{p}^{(t-N+2)}, \dots, \mathbf{p}^{(t)} \right\}
\]

只有当窗口被填满后，系统才开始输出稳定估计。若窗口尚未满，则状态为：

\[
\text{reason} = \texttt{collecting}
\]

这意味着本项目不是单帧聚类，而是**时间窗口内的稠密一致性判断**。

---

## 4.3 窗口内 DBSCAN

在窗口 \(W_t\) 上，本项目执行一次 DBSCAN：

\[
\mathrm{labels}_t = \mathrm{DBSCAN}\left(W_t;\varepsilon,\mathrm{MinPts}\right)
\]

这里使用的距离仍是三维欧氏距离：

\[
\mathrm{dist}(\mathbf{p}_i,\mathbf{p}_j)=\|\mathbf{p}_i-\mathbf{p}_j\|_2
\]

实现层面，本项目用自定义 `_dbscan()`、`_grow_cluster()` 与 `_region_query()` 完成这一过程，而不是调用外部库。

---

## 4.4 主簇选择策略

标准 DBSCAN 可能返回多个正标签簇与噪声点。本项目不会把这些簇全部作为最终输出，而是只保留**样本数最多的正标签簇**作为主簇：

\[
C_t^\star = \arg\max_{C_k} |C_k|
\]

若窗口内没有任何正标签簇，即：

\[
\forall i,\ \mathrm{labels}_t(i)\le 0
\]

则输出状态为：

\[
\text{reason}=\texttt{no\_core\_cluster}
\]

因此，本项目把 DBSCAN 从“完整聚类工具”改造成了“主簇发现器”。

---

## 4.5 最终中心估计

在主簇 \(C_t^\star\) 上，本项目采用均值作为最终中心：

\[
\mathbf{P}_{\text{final}}^{(t)}=
\frac{1}{|C_t^\star|}
\sum_{\mathbf{p}\in C_t^\star}\mathbf{p}
\]

与某些基于质心漂移或中位数的方案相比，本项目采用均值有两个工程原因：

- 计算简单
- 对窗口内稳定密集团的中心位置有较好代表性

---

## 4.6 收敛离散度 \(\sigma\)

本项目引入了一个标准 DBSCAN 中并不存在的工程判据，即主簇内点对中心的均方根离散度：

\[
\sigma_t=
\sqrt{
\frac{1}{|C_t^\star|}
\sum_{\mathbf{p}\in C_t^\star}
\left\|\mathbf{p}-\mathbf{P}_{\text{final}}^{(t)}\right\|_2^2
}
\]

代码中该量记为 `sigma_mm`，物理单位为毫米。

该指标的意义是：

- 若簇内点围绕中心非常集中，则 \(\sigma_t\) 小
- 若簇仍然较散，说明目标估计尚未收敛，则 \(\sigma_t\) 大

---

## 4.7 锁定判据

本项目将“输出稳定可用目标”定义为 `locked=True`。其判据为：

\[
|C_t^\star| \ge \mathrm{MinPts}
\quad \text{and} \quad
\sigma_t < \sigma_{\text{thresh}}
\]

其中：

- \(\mathrm{MinPts}\) 与 DBSCAN 的最小核心点阈值共用同一参数
- \(\sigma_{\text{thresh}}\) 对应代码参数 `sigma_thresh_mm`

因此，单目标模块的输出逻辑可概括为：

\[
\text{DBSCAN 找到主簇} \Rightarrow
\text{计算主簇中心} \Rightarrow
\text{检查离散度是否收敛}
\]

这一步是本项目与标准 DBSCAN 最本质的差异之一。

---

## 4.8 单目标模块完整流程

给定每帧一个三维观测 \(\mathbf{p}^{(t)}\)，本项目的单目标流程为：

1. 将 \(\mathbf{p}^{(t)}\) 加入窗口 \(W_t\)
2. 若窗口长度 \(<N\)，返回 `collecting`
3. 否则对 \(W_t\) 执行 DBSCAN
4. 若无有效簇，返回 `no_core_cluster`
5. 取最大主簇 \(C_t^\star\)
6. 计算 \(\mathbf{P}_{\text{final}}^{(t)}\)
7. 计算 \(\sigma_t\)
8. 若满足锁定判据，则输出 `locked`
9. 否则输出 `insufficient_core_size` 或 `sigma_not_converged`

可见，该模块输出的不是“某一帧的聚类结果”，而是“最近 \(N\) 帧上最稳定的稠密一致估计”。

---

## 5. 本项目的多目标扩展

## 5.1 设计目标

当每帧不止一个点时，单纯对整帧点做一次 DBSCAN 并不能稳定区分不同目标，因为不同目标之间缺少时间连续性约束。

本项目为此引入：

- 多目标数据关联
- 每条轨迹内部独立 DBSCAN 滑动窗口

核心文件为：

- [multi_target_dbscan_tracker.py](/home/kesl/ke/DBSCAN/multi_target_dbscan_tracker.py)

---

## 5.2 轨迹状态定义

每条轨迹维护如下状态：

- `track_id`
- `filter_obj`：该轨迹内部的 `MultiFrameDBSCANFilter`
- `last_observation`
- `last_result`
- `missed_frames`
- `age`

因此，多目标模块本质上是：

\[
\text{轨迹管理器} + \text{多份独立单目标 DBSCAN 滤波器}
\]

---

## 5.3 基于最近观测的贪心关联

设上一时刻存在轨迹集合：

\[
\mathcal{T}_{t-1} = \{T_1, T_2, \dots, T_M\}
\]

当前帧检测点为：

\[
\mathcal{O}_t=\{\mathbf{o}_1^{(t)}, \mathbf{o}_2^{(t)}, \dots, \mathbf{o}_K^{(t)}\}
\]

项目先取每条轨迹的最近观测作为关联基准，构造三维距离矩阵：

\[
d_{ij}^{(t)} =
\left\|
\mathbf{x}_i^{(t-1)}-\mathbf{o}_j^{(t)}
\right\|_2
\]

然后对所有候选二元组 \((i,j)\) 按距离从小到大排序，执行贪心匹配，并要求：

\[
d_{ij}^{(t)} \le d_{\text{assoc}}
\]

其中 \(d_{\text{assoc}}\) 对应代码参数 `association_dist_thresh_mm`。

若某条轨迹或某个检测点已被分配，则不再参与后续匹配。

---

## 5.4 横向近邻回退关联

本项目还增加了一个标准多目标跟踪中较有工程意味的“回退关联”：

- 仅当当前检测点数不超过活动轨迹数时触发
- 允许三维深度发生较大跳变
- 但要求平面横向距离仍然足够接近

设横向距离为：

\[
d_{ij,xy}^{(t)}=
\left\|
\mathbf{x}_{i,xy}^{(t-1)}-\mathbf{o}_{j,xy}^{(t)}
\right\|_2
\]

其中 \(\mathbf{x}_{i,xy}\) 与 \(\mathbf{o}_{j,xy}\) 仅取前两个坐标分量。

若满足：

\[
d_{ij,xy}^{(t)} \le d_{\text{assoc}}
\]

则在某些情况下仍允许维持轨迹连续性。

该策略的工程含义是：

- 防止仅因深度方向异常跳变而打断同一目标轨迹
- 同时避免把横向位置差得很远的新目标错误并入旧轨迹

---

## 5.5 新建轨迹与轨迹删除

### 5.5.1 新建轨迹

若某检测点在当前帧未与任何已有轨迹匹配，则创建一条新轨迹：

\[
T_{\text{new}} \leftarrow \text{new track}(\mathbf{o}_j^{(t)})
\]

并为其初始化一个新的单目标 DBSCAN 滤波器。

### 5.5.2 轨迹丢失与删除

若某轨迹在当前帧未匹配到任何检测点，则：

\[
\mathrm{missed\_frames} \leftarrow \mathrm{missed\_frames}+1
\]

当满足：

\[
\mathrm{missed\_frames} > M_{\max}
\]

时，轨迹被删除，其中 \(M_{\max}\) 对应参数 `max_missed_frames`。

---

## 5.6 多目标模块完整流程

对每一帧点集 \(\mathcal{O}_t\)，多目标模块流程如下：

1. 读取当前活动轨迹
2. 构造轨迹到检测点的距离矩阵
3. 按最近距离进行贪心匹配
4. 必要时执行横向回退关联
5. 对已匹配轨迹：
   - 写入新观测
   - 调用该轨迹内部单目标 DBSCAN 滤波器
6. 对未匹配轨迹：
   - `missed_frames += 1`
7. 对未匹配检测点：
   - 新建轨迹
8. 删除超出最大丢失阈值的轨迹

因此，多目标部分并不是“多目标 DBSCAN”，而是：

\[
\text{多目标关联} + \text{轨迹内单目标多帧 DBSCAN}
\]

---

## 5.7 为什么常规多目标 demo 中的错误点不会被识别为伪目标

在当前仓库的常规多目标演示数据中，错误点并不是“额外生成的第四个目标”，而是对已有目标观测的偶发高 \(z\) 偏移。其生成逻辑位于：

- [viz_utils.py](/home/kesl/ke/DBSCAN/viz_utils.py)

设三条真实目标轨迹对应的理想观测分别为

\[
\mathbf{o}_A^{(t)},\mathbf{o}_B^{(t)},\mathbf{o}_C^{(t)}
\]

则常规 demo 中只有目标 \(A\) 与 \(C\) 会在个别帧出现抬高观测：

\[
\tilde{\mathbf{o}}_A^{(t)} = \mathbf{o}_A^{(t)} + [0,0,\Delta z]^\top,\quad t\in\{5,11,17\}
\]

\[
\tilde{\mathbf{o}}_C^{(t)} = \mathbf{o}_C^{(t)} + [0,0,\Delta z]^\top,\quad t\in\{3,9,15\}
\]

其中当前演示中 \(\Delta z = 95 \text{ mm}\)。

这类错误点不会形成伪目标，原因可以归纳为以下三点。

### 5.7.1 每帧并没有新增一个独立检测目标

常规多目标 demo 在每一帧中仍然只提供 3 个检测点，即：

\[
K_t = 3,\quad \forall t
\]

这意味着错误点只是“某个真实目标在该帧被测错了”，而不是“场景中新增了一个空间上独立的检测点”。因此，多目标跟踪器不会仅因这类抬高观测而自动创建第四条轨迹。

### 5.7.2 关联层会把它继续并入原有轨迹

虽然抬高观测在三维距离上发生了跳变，但其横向坐标基本仍与原目标一致，因此满足横向近邻回退关联的工程条件：

\[
\left\|
\tilde{\mathbf{o}}_{A,xy}^{(t)}-\mathbf{x}_{A,xy}^{(t-1)}
\right\|_2
\le d_{\text{assoc}}
\]

\[
\left\|
\tilde{\mathbf{o}}_{C,xy}^{(t)}-\mathbf{x}_{C,xy}^{(t-1)}
\right\|_2
\le d_{\text{assoc}}
\]

其中 \(d_{\text{assoc}}\) 对应参数 `association_dist_thresh_mm`。因此，这些错误点会被继续写入已有轨迹的滑动窗口，而不是触发新轨迹创建。

### 5.7.3 单轨迹窗口内的错误点数量不足以形成独立密度簇

对任一真实轨迹而言，窗口中的错误观测个数仅为：

\[
K_{\text{false}} = 3
\]

而当前实现使用的最小核心点阈值为：

\[
\mathrm{MinPts} = 8
\]

因此，对任一错误点 \(\mathbf{e}\) 而言，其邻域内错误点总数至多满足：

\[
|N_\varepsilon(\mathbf{e})| \le K_{\text{false}} < \mathrm{MinPts}
\]

根据标准 DBSCAN 的核心点条件，这些错误点无法构成核心支撑簇，只会被标记为噪声 `-1`。进一步地，本项目单目标滤波器只输出最大正标签主簇，故这部分离群点不会形成稳定的 \(\mathbf{P}_{\text{final}}\)。

因此，常规多目标 demo 中图上看到的一小团红色错误点，其本质是：

- 已有轨迹窗口内累计的少量离群观测
- 在显示层面同时画出后看起来像一团
- 在算法层面仍然属于原轨迹内部的噪声点，而不是新目标

---

## 6. 运行时接口设计

核心文件为：

- [runtime_interface.py](/home/kesl/ke/DBSCAN/runtime_interface.py)

其设计目的不是改变算法，而是把前述单目标/多目标逻辑包装成在线接口，便于与相机或识别系统对接。

## 6.1 输入模式

### 单目标模式

每帧输入一个点，或给出多个点时只取第一个点：

\[
\mathbf{p}^{(t)} = [x,y,z]
\]

### 多目标模式

每帧输入一个点集：

\[
\mathcal{O}_t = \{\mathbf{o}_1^{(t)}, \dots, \mathbf{o}_K^{(t)}\}
\]

---

## 6.2 输出内容

### 单目标输出

输出包括：

- `locked`
- `cluster_xyz_mm`
- `sigma_mm`
- `core_size`
- `reason`

### 多目标输出

输出包括：

- `active_track_count`
- `tracks`
- `primary_track_id`
- `primary_cluster_xyz_mm`

---

## 6.3 主轨迹选择策略

在多目标模式下，接口还会从所有轨迹中选出一条“主轨迹”。其排序规则为：

1. 优先 `locked=True`
2. 其次 `core_size` 更大
3. 再次 `sigma_mm` 更小
4. 最后 `track_id` 更小

可写成排序键：

\[
\text{rank}(T_i)=
\left(
\mathbb{I}[\neg locked_i],
-core\_size_i,
\sigma_i,
track\_id_i
\right)
\]

排序后最优轨迹即主轨迹。

这一步属于运行时接口层的业务选择，不属于标准 DBSCAN 理论范畴。

---

## 7. 参数解释与调节逻辑

## 7.1 `window_size`

窗口越大，多帧统计越稳定，但响应越慢；窗口越小，响应更快，但更容易受瞬时噪声影响。

## 7.2 `eps_mm`

`eps_mm` 决定窗口内哪些点被视为同一局部密度结构。其物理意义是“同一目标在多帧观测中的允许空间散布半径”。

## 7.3 `min_pts`

在标准 DBSCAN 中，它决定核心点条件；在本项目中，它还有第二层作用：

- 用于判断主簇规模是否足够大
- 进而影响是否能进入锁定状态

## 7.4 `sigma_thresh_mm`

这是本项目新增的稳态收敛阈值。它衡量主簇内部的紧致程度，而不是 DBSCAN 原始定义中的参数。

## 7.5 `association_dist_thresh_mm`

该参数只在多目标模块中起作用，用于控制轨迹与当前检测点能否视为同一目标。

## 7.6 `max_missed_frames`

该参数决定轨迹在连续多少帧无匹配后被删除。

---

## 8. 标准 DBSCAN 与本项目实现的对照

## 8.1 任务目标不同

### 标准 DBSCAN

目标是对静态数据集进行密度聚类。

### 本项目

目标是从**连续在线三维点流**中输出稳定目标位置。

---

## 8.2 输出对象不同

### 标准 DBSCAN

输出是完整簇划分：

\[
\{C_1, C_2, \dots, C_K\} + \text{noise}
\]

### 本项目

单目标时只保留最大主簇，并进一步输出：

\[
\mathbf{P}_{\text{final}}, \sigma, locked
\]

多目标时则对每条轨迹分别执行这一逻辑。

---

## 8.3 时间建模不同

### 标准 DBSCAN

通常对一次性静态数据执行聚类。

### 本项目

在长度为 \(N\) 的滑动窗口上反复执行 DBSCAN：

\[
W_1, W_2, \dots, W_t, \dots
\]

因此本项目是**时序窗口上的重复 DBSCAN**。

---

## 8.4 稳定性判据不同

### 标准 DBSCAN

没有“锁定”或“收敛”概念。

### 本项目

额外引入：

\[
\sigma_t < \sigma_{\text{thresh}}
\]

作为工程稳态判据。

---

## 8.5 多目标机制不同

### 标准 DBSCAN

不解决多帧多目标关联问题。

### 本项目

引入了：

- 轨迹状态管理
- 贪心最近邻关联
- 横向回退关联
- 轨迹新建与删除

因此多目标部分本质上是 DBSCAN 与轻量级跟踪器的耦合。

---

## 8.6 复杂度实现不同

### 标准 DBSCAN

可借助空间索引实现接近 \(O(n\log n)\)。

### 本项目

窗口内 `_region_query()` 直接对当前点与窗口所有点做欧氏距离计算，窗口规模记为 \(N\)，则单次窗口 DBSCAN 的代价近似为：

\[
O(N^2)
\]

由于本项目默认窗口仅为 15，故当前实现仍然可接受。

---

## 9. 本项目方法的作用、优势与局限

## 9.1 方法作用

本项目方法的主要作用可概括为：

1. 从连续三维点流中滤除偶发穿透点与异常点
2. 提取最近若干帧中最稳定、最稠密的目标区域
3. 给出稳定的目标中心估计
4. 在多目标场景下保持轨迹连续性并独立输出每个目标的稳定中心

若将其放在果梗点识别场景中，可理解为：

> 从识别系统给出的连续果梗点坐标中，筛掉瞬时错误点，并输出对机械执行或定位更可靠的目标坐标。

## 9.2 优势

- 利用时间窗口增强鲁棒性
- 天然继承 DBSCAN 的噪声抑制能力
- 不依赖目标先验数量
- 可扩展到多目标
- 输出结果具有明确物理量解释

## 9.3 局限

- 参数依赖于场景尺度和噪声水平
- 当前 DBSCAN 为暴力实现，不适合超大窗口
- 主簇只取最大簇，可能忽略次主簇信息
- 多目标关联为贪心策略，不属于全局最优匹配
- 当目标间距离过近或交叉运动时，轻量级关联可能出错

### 9.3.1 持续误检可能形成伪目标

尽管常规 demo 中的错误点不会形成伪目标，但这并不意味着该系统在任何情况下都绝对不会产生伪目标。若误检同时满足“持续出现、空间上紧凑、与真实目标横向分离”三项条件，则当前工程实现可能把它当作一条新的稳定轨迹。

设某类误检在若干帧中形成观测序列：

\[
\mathcal{E}=\{\mathbf{e}^{(t_1)},\mathbf{e}^{(t_2)},\dots,\mathbf{e}^{(t_K)}\}
\]

若它满足以下条件：

1. 持续出现的次数足够多

\[
K \ge \mathrm{MinPts}
\]

2. 误检点之间在空间上足够紧凑

\[
\left\|\mathbf{e}^{(t_i)}-\mathbf{e}^{(t_j)}\right\|_2 \le \varepsilon,
\quad \text{对足够多的 } i,j
\]

3. 其横向位置与已有轨迹分离到足以触发新建轨迹

\[
\min_m
\left\|
\mathbf{e}_{xy}^{(t)}-\mathbf{x}_{m,xy}^{(t-1)}
\right\|_2
>
d_{\text{assoc}}
\]

则多目标层会把该误检序列视为新的检测来源并新建轨迹；随后，该新轨迹内部的滑动窗口 DBSCAN 又可能在这组误检点上形成主簇：

\[
\mathbf{P}_{\text{false}}=
\frac{1}{|C_{\text{false}}|}
\sum_{\mathbf{p}\in C_{\text{false}}}\mathbf{p}
\]

若其离散度同时满足：

\[
\sigma_{\text{false}} < \sigma_{\text{thresh}}
\]

则该误检轨迹将被系统标记为 `locked`，从而形成一个伪目标。

### 9.3.2 “错误点会被误识别成伪目标”的对照 demo

为展示上述局限，当前仓库额外提供了一个专门的对照 demo：

- [run_pseudo_target_demo.py](/home/kesl/ke/DBSCAN/run_pseudo_target_demo.py)

其对应的数据生成逻辑位于：

- [viz_utils.py](/home/kesl/ke/DBSCAN/viz_utils.py)

该 demo 与常规多目标 demo 的关键区别在于：从第 6 帧开始，它会在三条真实目标之外，持续注入一个额外的第四检测点，其设计中心为

\[
\mathbf{P}_{\text{pseudo}} = [222, 92, 446]^\top \text{ mm}
\]

于是每帧检测数从

\[
K_t=3
\]

变为

\[
K_t=4,\quad t\ge 6
\]

这意味着该误检不再只是“已有目标的测量偏差”，而是“持续存在的额外检测源”。在当前默认参数

\[
N=15,\quad \varepsilon=15,\quad \mathrm{MinPts}=8
\]

下，这组持续误检会逐步形成独立轨迹，并在窗口内累积出满足密度条件的主簇，最终可能被标记为稳定目标。

### 9.3.3 对论文局限性分析的含义

这一现象说明：本项目的鲁棒性主要针对的是偶发离群点，而不是长期稳定存在的系统性误检源。换言之，本方法抑制的是“短时噪声”，并不天然抑制“持续但错误的伪观测目标”。

因此，在论文中应明确指出：

- 当误检仅偶发出现且数量不足时，DBSCAN 会把它们视为噪声
- 当误检在时间上持续、空间上集中且与真实目标分离时，它可能被轨迹管理器与窗口 DBSCAN 联合放大为伪目标
- 若应用场景存在此类风险，需要进一步引入外观先验、运动模型、物理工作空间约束或更严格的多帧一致性验证

---

## 10. 论文写作建议

若将本项目写入毕业论文，建议将方法名称表述为：

**基于多帧滑动窗口 DBSCAN 的三维目标稳态估计方法**

若包含多目标部分，可进一步表述为：

**基于滑动窗口 DBSCAN 与最近邻关联的多目标三维坐标稳态跟踪方法**

论文中应明确区分：

- 哪些内容属于**标准 DBSCAN 理论**
- 哪些内容属于**本项目新增的工程化机制**

特别是以下内容不是标准 DBSCAN 原始理论的一部分：

- 滑动窗口
- 主簇均值中心 \(\mathbf{P}_{\text{final}}\)
- 离散度 \(\sigma\)
- `locked` 判据
- 多目标关联与轨迹管理
- 主轨迹选择规则

---

## 11. 结论

标准 DBSCAN 提供了一个基于局部密度的聚类理论框架，其优势在于无需预设簇数、可识别噪声并支持任意形状簇。本项目在保留 DBSCAN 核心密度聚类思想的基础上，通过滑动窗口、多帧主簇提取、离散度收敛判据以及多目标数据关联机制，将其改造为适用于在线三维点流稳定估计的工程系统。

因此，本项目不是对标准 DBSCAN 的简单调用，而是一个：

\[
\text{标准 DBSCAN} + \text{时间窗口建模} + \text{稳态判定} + \text{多目标关联}
\]

的复合方法。

---

## 12. 参考资料

### 标准 DBSCAN 理论

1. Ester, M., Kriegel, H.-P., Sander, J., Xu, X. *A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise*. KDD-96.  
   AAAI 页面：<https://aaai.org/papers/kdd96-037-a-density-based-algorithm-for-discovering-clusters-in-large-spatial-databases-with-noise/>

2. 同一论文元数据页：  
   OSTI 页面：<https://www.osti.gov/biblio/421283>

### 本项目实现

1. [multiframe_dbscan_filter.py](/home/kesl/ke/DBSCAN/multiframe_dbscan_filter.py)
2. [multi_target_dbscan_tracker.py](/home/kesl/ke/DBSCAN/multi_target_dbscan_tracker.py)
3. [runtime_interface.py](/home/kesl/ke/DBSCAN/runtime_interface.py)
4. [README.md](/home/kesl/ke/DBSCAN/README.md)
5. [viz_utils.py](/home/kesl/ke/DBSCAN/viz_utils.py)
6. [run_pseudo_target_demo.py](/home/kesl/ke/DBSCAN/run_pseudo_target_demo.py)
