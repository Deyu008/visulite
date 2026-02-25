# Python vs Rust：VisuLite 内存/效率/稳健性评估与落地路线

> 适用项目：VisuLite（PySide6 Widgets + pandas/numpy + matplotlib + openpyxl）

## 摘要（结论先行）

在当前约束下（Windows 桌面、常见数据量 `<50MB`、主要是“理论担心”、Rust 工具链“视收益而定”）：

- 不建议全 Rust 重写：成本高、风险高、UI/生态迁移收益不成比例。
- “Python 会不会内存泄露”更常见的真相是：内存占用增长是“设计导致的保留”或“分配器不归还”，不是传统意义的泄露。
- 对本项目，最大内存风险点不是 Python 本身，而是 `AppState` 的 Undo/Redo 使用 `DataFrame.copy(deep=True)` 做快照（最多 30 份），会把内存放大到 `O(history_limit * 数据大小)`。
- 如果未来真的需要“Rust 的稳健/效率”，最现实的方式是保留 Python UI，局部引入 Rust 能力（优先考虑“换后端库/扩展模块”而非整栈重写）。

## 现状基线（来自代码事实）

- 技术栈：PySide6 Widgets + pandas/numpy + matplotlib + openpyxl。
- 内存放大点：`visulite/models/app_state.py` 的 `history_limit=30`，Undo/Redo 栈每次 `copy(deep=True)`；`original_frame` 也 deep copy。
- 图表侧：matplotlib figure/canvas 复用，`ChartManager` 有 heatmap colorbar 清理逻辑；这里更像“可控缓存”而非泄露源。

## 目标与成功标准（评估维度）

1. 稳健性
- 连续加载/预处理/撤销/重绘 200 次后不崩溃。
- 内存曲线可解释：无“无上限增长”，峰值与功能行为匹配（例如历史栈保留导致的增长）。
2. 效率
- `<50MB` CSV：加载 + 表格刷新 + 更新图表在可接受时间内（例如 1-3s 级别，具体阈值由实测设定）。
3. 工程成本
- 打包/分发流程复杂度可控（避免无收益引入 Rust 工具链）。

## 决策框架（选型矩阵）

### 方案 A：继续 Python（推荐默认）

- 收益：最快落地；生态最成熟；UI（Qt）本来就是 C++，Python 只是 glue；pandas/numpy 已是 C 优化。
- 风险：如果继续用“DataFrame 全量快照 Undo”，大数据下内存会被设计放大。
- 适用：当前数据规模和需求。

### 方案 B：Python UI + 局部 Rust 能力（按收益启用）

两条子路线（按推荐顺序）：

1. 优先考虑“Rust in wheels”：换更高效的数据后端库
- 例：引入 `polars`（底层 Rust），在 Python 中调用，不需要你自己维护 Rust 构建链（通常装 wheel 即可）。
- 适合：过滤/选择列/类型转换等数据处理要显著加速且更省内存的场景。
2. 真正写 Rust 扩展（pyo3/maturin）
- 只在明确存在 Python 侧瓶颈（纯 Python 循环、复杂自定义算法）时才值得。
- 打包复杂度会上升（PyInstaller + 二进制扩展 + hook/collect 处理）。

### 方案 C：全 Rust 重写（不推荐）

- UI 框架选型、图表生态（matplotlib 对等物）、数据处理生态（pandas 对等物）、打包发布链都会重新踩坑。
- “更稳健”不等于“更省内存”：如果仍要保存 30 份历史状态，Rust 一样会占用对应内存。

## 落地路线（无需再做决策的执行步骤）

### Phase 0：用事实消除“泄露 vs 占用增长”的不确定性（先测再改）

1. 定义 3 个可重复脚本化场景（用现有 `tests/test_ui_smoke.py` 风格即可）
- 场景 S1：加载一个典型 `<50MB` 文件，重复执行：slice/filter/fill/convert 100 次（含 Undo/Redo）。
- 场景 S2：只重复“更新图表”200 次（检测 matplotlib 对象是否累计）。
- 场景 S3：频繁切换数据集 50 次（检测旧数据是否被引用保留）。
2. 记录指标（Windows 进程指标即可）
- RSS/Working Set、Private Bytes、Python 堆（`tracemalloc`）、GC counts。
3. 形成结论模板
- “增长来自 history 栈/原始帧/图表缓存/分配器碎片/真正泄露”的哪一种，占比是多少。

### Phase 1：在 Python 侧先把“最大内存放大器”降下来（不改业务逻辑的优化）

1. 把 Undo/Redo 从“存 DataFrame 全量快照”改为“存操作/差量/可回放”
- 选型（按推荐顺序，默认用 1）：
  1) 存操作记录（例如：slice 参数、filter 条件、fill 方法、type convert 参数），Undo 就回退一步操作序列并重新计算视图。
  2) 存稀疏差量（仅对少数列/少数行改变的操作适用）。
  3) 继续存快照但加内存预算：按估算字节数裁剪历史，而不是固定 30 步。
2. 限制 `original_frame` 的驻留策略
- 默认继续保留（方便一键恢复），但允许大文件时选择“不保留原始帧，仅保留路径可重载”。
3. matplotlib 对象生命周期检查
- 确保每次重绘不创建额外 Figure；heatmap colorbar 已做清理，但要在 S2 中验证。

### Phase 2：如果 Phase 1 后仍不满意，再评估 Rust 介入点（小步试点）

1. 先试 `polars` 替换部分 DataProcessor 路径（不动 UI 模型）
- 仅对“筛选/数值范围/类型转换”等环节试点。
- 输出最终仍转回 pandas 供 `DataFrameModel`/matplotlib 使用（接受一次转换成本，先验证收益）。
2. 只有在确认“确实存在 Python 侧纯解释器瓶颈”时，才做 pyo3 扩展
- 明确函数边界、输入输出（Arrow/ndarray/pandas interchange），以及 PyInstaller 打包策略。

## 公共接口/API 变更（如果进入 Phase 1/2）

- Phase 0：无。
- Phase 1（建议的最小改动形态）：
  - `AppState`：新增 history 策略配置（例如 `history_mode = "ops" | "snapshots"`，`history_budget_mb`）。
  - `DataProcessor`：为每个操作输出可序列化的 operation descriptor（供回放）。
- Phase 2：
  - 可选新增 `visulite/services/df_backend.py` 抽象层（pandas/polars 适配）。

## 测试用例与验收

- 自动化：
  - 新增“内存回归测试”（允许用阈值或趋势断言，避免环境抖动造成 flaky）。
  - 现有 UI smoke 继续覆盖：加载、预处理、Undo/Redo、更新图表。
- 手动：
  - 打开 Windows 任务管理器/Process Explorer，跑 S1/S2/S3，确认曲线可解释且有上限。
  - 大文件（接近 50MB）在 Undo 多次后仍可用，不出现 OOM/卡死。

## 假设与默认值

- 目标平台以 Windows 为主。
- 典型数据量 `<50MB`，所以“全 Rust 重写”默认判定为收益不足。
- 当前担心为“理论风险”，因此以“测量+解释+定点优化”为优先路线。

