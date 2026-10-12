# UBEP 论文翻译规范（所有分块翻译共用）

论文：《UBEP: Re-architecting Expert Parallelism Communication Library for Production Superpods》(arXiv:2607.06202, SIGCOMM'26, 上海交大 & 华为)。

## 任务格式
- 输入每行 `ID\t类型\t英文`；输出每行 `ID\t中文译文`；**行数与顺序与输入完全一致**。
- heading 行保留编号译中文（如 `3.2 Kernel Decomposition` → `3.2 核算子分解`（Kernel 按上下文，若指 MoE 核算子用"核算子"，通用的用"内核"））。
- 注意：本文为**双栏排版提取**，个别段落可能有断行错位或粗体引导词位置异常（如 `**xxx.**` 出现在句中），按语义正常翻译，不要放大乱码。

## 硬性规则
1. 保留 `$...$`、`**粗体**`、引用 `[N]`、`§N`、`Figure N`/`Table N`/`Algorithm N`。
2. 数值/单位精确保留：`400 GB/s`、`~2 µs`、`1.73×`、`P99`、`25.47%`、`512B`、`Top-k`。
3. 专名不译：UBEP、CM384、Ascend、CANN、MindSpore、MindIR、AIC、AIV、UBuf、UB、RoCE、NVLink、InfiniBand、DeepSeek、LLaMA、NSA、Mixtral、SyncAll、CalCumsum、BSP、EP、TP、DP、GBS、HBM、NoC。
4. 算法伪代码（Require/Ensure/for/while/emit）关键字保留英文，说明译中文。
5. 段落不合并拆分；技术细节逐项落实；意译优先。

## 术语表（锁定）
| 英文 | 译法 |
|---|---|
| UBEP | 不译（系统名，Expert Parallelism Communication Library） |
| expert parallelism (EP) | 专家并行（EP） |
| expert parallelism communication library | 专家并行通信库 |
| all-to-all / dispatch / combine | all-to-all / 分发（dispatch）/ 合并（combine） |
| kernel decomposition | 核分解（MoE FFN 的 gate/up/down 核算子拆解） |
| hierarchical token-level scheduling | 分层 token 级调度 |
| data-as-flag synchronization | 数据即标志（Data-as-Flag）同步 |
| kernel fusion / fusing | 算子融合 / 融合 |
| token sending / token combine | token 发送 / token 合并 |
| superpod / supernode | 超节点（superpod 首次标注） |
| UB (Unified Bus) | 统一总线（UB，灵衢） |
| unified global address space (UGAS) | 统一全局地址空间（UGAS） |
| remote memory / remote direct access | 远端内存 / 远端直接访问 |
| HBM / DDR / SSR | 不译 |
| rank / source rank / destination rank | rank / 源 rank / 目的 rank |
| SyncAll / flag polling / sentinel | SyncAll / 标志轮询 / 哨兵值 |
| one-hop / two-hop | 一跳 / 两跳 |
| intra-NPU / inter-NPU | NPU 内 / NPU 间 |
| token-level ordering | token 级排序 |
| production / production-scale | 生产环境 / 生产规模 |
| barrier / serialization | 屏障 / 串行化 |
| memory footprint | 内存占用 |
| reordering | 重排 |
| end-to-end latency | 端到端时延 |
| throughput | 吞吐量 |
| correctness / safety assumption | 正确性 / 安全性假设 |
| atomic (512B atomicity) | 原子（512B 原子性） |

## 输出质量基准
熟练系统方向研究者的中文技术文风；同一术语全文一种译法；不确定的保留英文。
