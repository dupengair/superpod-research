# HyperOffload 论文翻译规范（所有分块翻译共用）

## 任务格式
- 输入文件每行：`ID\t类型\t英文原文`（tab 分隔）。
- 输出文件每行：`ID\t中文译文`（tab 分隔），**行数与顺序与输入完全一致**，不增删行、不改 ID。
- heading 行保留编号译中文（如 `4.2.1 Cache Operators as First-Class Graph Nodes` → `4.2.1 缓存算子作为一等图节点`）；`Algorithm 1 ...` 同理。

## 硬性规则
1. 保留 `$...$` 数学、`**粗体**`、引用 `[N]`、`§N`、图表引用 `Figure 3`/`Table 2`。
2. 数字/单位/百分比精确保留：`1.73×`、`−13.78%`、`123k tokens`、`GB/s`、`µs`。
3. 型号/框架/基准名不译：LLaMA-8B、DeepSeek-V3、MindIR、CANN、PyTorch、CUDA、MindSpore。
4. 列表编号 `(1)(2)(3)` 保留；段落不合并不拆分；技术细节逐项落实。
5. 意译优先，长句可断句但不改逻辑顺序。

## 术语表（锁定）
| 英文 | 译法 |
|---|---|
| HyperOffload | 不译（系统名） |
| SuperNode / supernode | 超节点 |
| hierarchical memory | 分层内存 |
| offloading / offload | 卸载 |
| prefetch(ing) | 预取 |
| cache operator | 缓存算子 |
| operatorization | 算子化 |
| graph-driven | 图驱动 |
| runtime-driven | 运行时驱动 |
| execution order | 执行序 |
| first-class (graph) node | 一等（图）节点 |
| KV cache | KV 缓存 |
| activation recomputation | 激活重计算 |
| sparse block | 稀疏块 |
| memory pool | 内存池 |
| DDR / DRAM / HBM / SSD | 不译 |
| D2H communication | D2H 通信（设备到主机） |
| unified memory / shared memory pool | 统一内存 / 共享内存池 |
| Ascend | 昇腾（首次标注 Ascend） |
| CPU/NPU/GPU | 不译 |
| DP / TP / PP / EP | 数据/张量/流水线/专家并行（首次标注后用缩写） |
| GBS (global batch size) | 全局批大小（GBS） |
| peak memory usage | 峰值内存占用 |
| memory footprint | 内存占用 |
| defragmentation | 碎片整理 |
| tile-based | 基于核块（tile）的 |
| SIMT | SIMT（单指令多线程） |
| critical path | 关键路径 |
| latency hiding | 时延隐藏 |
| overlap（通信与计算） | 重叠 |
| training / inference | 训练 / 推理 |
| workload | 负载 |

## 输出质量基准
- 熟练系统方向研究者的中文技术文风；同一术语全文一种译法；不确定的缩写保留英文。
