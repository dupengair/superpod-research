# 超节点硬件体系架构 -- arXiv 检索轻量摘要表

> **检索日期**：2026-08-31
> **检索范围**：arXiv 预印本，2022-01-01 至今，英文
> **检索方法**：因 `export.arxiv.org`（arXiv 官方 REST API 端点）在本环境 HTTPS 不可达（TCP 握手后 read 超时，已多轮验证），按 academic-search skill 失败降级规则，改用 **OpenAlex REST API**（HTTPS 可达、索引 arXiv 全量预印本、且提供引用数与 OA 状态--arXiv 原生 API 无引用数字段）。所有结果均过滤为**在 arXiv 上有收录的论文**（OpenAlex `locations.source.id == S4306400194`，即 arXiv 源），等价于“在 arXiv 检索”的目标范围。3 个已知 UB-优先 arXiv ID 额外通过 `arxiv.org/abs/<id>`（HTTPS 可达）直拉确认标题/年月/分类。
> **引用数来源**：OpenAlex `cited_by_count`；后续可由另一 Agent 用 Semantic Scholar / Google Scholar 补全对齐。
> **OA PDF**：arXiv 预印本均为开放获取，标“是”，直链 `https://arxiv.org/pdf/{arxiv_id}`。
> **优先级标记**：`[UB-优先]` = 涉及灵衢总线 UnifiedBus/UB、华为超节点体系（CloudMatrix、昇腾 SuperPOD）或显式以“supernode/superpod”硬件体系为主题的论文，按 CLAUDE.md 最高优先级规则入选；`[前次已收]` = 已在前次报告中的已知论文（本次增量检索保留并标注）。

---

## 检索方法说明

**平台**：OpenAlex REST API（`https://api.openalex.org/works`，`search` 关键词检索 + `filter=from_publication_date:2022-01-01,locations.source.id:S4306400194` 限定 arXiv 源）。

**降级原因**：`export.arxiv.org` HTTPS API 在本环境不可达。诊断：HTTP 80 端口 0.6s 返回 301->HTTPS；HTTPS 443 端口 TCP 可连但 read 操作超时（18s+）；对照 `arxiv.org/abs/*` HTTPS 可达、`api.openalex.org` HTTPS 可达、`api.semanticscholar.org` HTTPS 可达（429 限流），判定为 export 子域端点在该网络路径下不可用。

**关键词组合（实际执行的子查询，3 组共 34 个子查询，每个 25 条/页 ×2 页，合并去重）**：

- **E1（超节点本体 + 华为/统一内存/NVL/GB200）**：`CloudMatrix`、`UnifiedBus`、`Ascend SuperPOD`、`unified memory semantics`、`supernode interconnect`、`superpod AI`、`scale-up domain`、`rack-scale LLM`、`pod-scale AI`、`NVL72`、`GB200`、`unified memory GPU`、`rack-scale GPU`
- **E2（设备管理统一性 / 资源解耦 / 可组合基础设施）**：`resource disaggregation GPU`、`disaggregated memory GPU`、`composable infrastructure GPU`、`composable datacenter`、`single system image GPU`、`single-node abstraction`、`unified device abstraction`、`disaggregated LLM`、`disaggregated accelerator`
- **E3（互联互通 / 互连拓扑 / CXL / 集合通信）**：`scale-up fabric`、`scale-up network LLM`、`interconnect topology LLM`、`interconnect topology GPU cluster`、`CXL collective communication`、`CXL LLM`、`CXL training`、`CXL accelerator`、`collective communication LLM`、`collective communication training`、`AI cluster interconnect`、`GPU cluster topology`

**筛选规则**：
- OpenAlex `search` 为相关性排序（非布尔），原始召回 raw_hits = 1565 条；
- 对每条结果遍历全部子查询规则施加**精度过滤**：宽泛概念词（scale-up / disaggregation / composable / topology / fabric 等）要求主词出现在**标题**且带上下文（如 topology+cluster/gpu、fabric+scale/network），罕见专有词（CloudMatrix/UnifiedBus/NVL72/GB200/CXL/SuperPOD/supernode/superpod/unified memory）允许标题或摘要；叠加 **CS 系统类 concept 门槛**与**噪声领域排除**（图神经网络/天文学/区块链/分子物理/神经科学/量子/机器人/医学/CFD 等同名或无关方向）；过滤后 221 条；
- 去重（arXiv ID 优先，无 ID 则 title+year）后 174 条；
- 按匹配子查询重分配组（E1 优先，避免宽松 query 锚定到错误组）；组内按 UB-优先 -> 前次已收 -> 引用降序 -> 年月降序排序，每组 cap 30 条；
- 最终 E1=27、E2=30、E3=30，合计 **87** 条；其中 `[UB-优先]` **7** 条。

**局限**：
- 本次未直接调用 `export.arxiv.org` API（环境网络不通），改走 OpenAlex 同源（arXiv 源过滤）等价检索并补充引用数；arXiv 原生 category 字段未取全（仅 3 个已知 ID 经 `arxiv.org/abs` 解析了 primary category），其余论文的 arXiv 分类待后续深拉元数据时补；
- 引用数取自 OpenAlex（与 Semantic Scholar / Google Scholar 数值会不一致，属正常）；
- Semantic Scholar 未使用（无 API Key，避免 429）；Google Scholar / 知网未使用（CDP 未开启，且本任务为 arXiv 英文检索，知网为另一并行任务的范围）；
- 本表为第一遍轻量摘要，未在正文中展开完整摘要（完整摘要保存于中间 JSON，供第二遍深拉调用）。

---

## 一、[UB-优先] 论文清单（灵衢/华为超节点体系，固定首组）

| # | 标题 | arXiv ID | 年月 | 引用数 | OA PDF | 优先级标记 |
|---|------|----------|------|--------|--------|------------|
| 1 | Serving Large Language Models on Huawei CloudMatrix384 | [2506.12708](https://arxiv.org/abs/2506.12708) | 2025-06 | 1 | 是 | [UB-优先] [前次已收] |
| 2 | SLAI T-Rex: Full-Parameter Post-training of the DeepSeek-V4 Family on Ascend SuperPOD | [2607.20145](https://arxiv.org/abs/2607.20145) | 2026-07 | 0 | 是 | [UB-优先] [前次已收] |
| 3 | Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperPod | [2508.02520](https://arxiv.org/abs/2508.02520) | 2025-08 | 0 | 是 | [UB-优先] [前次已收] |
| 4 | UBEP: Re-architecting Expert Parallelism Communication Library for Production Superpods | [2607.06202](https://arxiv.org/abs/2607.06202) | 2026-07 | 0 | 是 | [UB-优先] |
| 5 | StrataCL: Fabric-Native Communication Library for Production Supernodes | [2607.26444](https://arxiv.org/abs/2607.26444) | 2026-07 | 0 | 是 | [UB-优先] |
| 6 | HyperParallel: A Supernode-Affinity AI Framework | [2603.03731](https://arxiv.org/abs/2603.03731) | 2026-03 | 0 | 是 | [UB-优先] |
| 7 | HyperOffload: Graph-Driven Hierarchical Memory Management for Large Language Models on SuperNode Architectures | [2602.00748](https://arxiv.org/abs/2602.00748) | 2026-02 | 0 | 是 | [UB-优先] |

## 二、E1 检索结果（超节点本体 + 华为/统一内存/NVL/GB200）

| # | 标题 | arXiv ID | 年月 | 引用数 | OA PDF | 优先级标记 |
|---|------|----------|------|--------|--------|------------|
| 1 | Serving Large Language Models on Huawei CloudMatrix384 | [2506.12708](https://arxiv.org/abs/2506.12708) | 2025-06 | 1 | 是 | [UB-优先] [前次已收] |
| 2 | SLAI T-Rex: Full-Parameter Post-training of the DeepSeek-V4 Family on Ascend SuperPOD | [2607.20145](https://arxiv.org/abs/2607.20145) | 2026-07 | 0 | 是 | [UB-优先] [前次已收] |
| 3 | Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperPod | [2508.02520](https://arxiv.org/abs/2508.02520) | 2025-08 | 0 | 是 | [UB-优先] [前次已收] |
| 4 | UBEP: Re-architecting Expert Parallelism Communication Library for Production Superpods | [2607.06202](https://arxiv.org/abs/2607.06202) | 2026-07 | 0 | 是 | [UB-优先] |
| 5 | StrataCL: Fabric-Native Communication Library for Production Supernodes | [2607.26444](https://arxiv.org/abs/2607.26444) | 2026-07 | 0 | 是 | [UB-优先] |
| 6 | HyperParallel: A Supernode-Affinity AI Framework | [2603.03731](https://arxiv.org/abs/2603.03731) | 2026-03 | 0 | 是 | [UB-优先] |
| 7 | HyperOffload: Graph-Driven Hierarchical Memory Management for Large Language Models on SuperNode Architectures | [2602.00748](https://arxiv.org/abs/2602.00748) | 2026-02 | 0 | 是 | [UB-优先] |
| 8 | IANUS: Integrated Accelerator based on NPU-PIM Unified Memory System | [2410.15008](https://arxiv.org/abs/2410.15008) | 2024-10 | 56 | 是 | - |
| 9 | Shared Virtual Memory: Its Design and Performance Implications for Diverse Applications | [2405.06811](https://arxiv.org/abs/2405.06811) | 2024-05 | 7 | 是 | - |
| 10 | An Intelligent Framework for Oversubscription Management in CPU-GPU Unified Memory | [2204.02974](https://arxiv.org/abs/2204.02974) | 2022-04 | 3 | 是 | - |
| 11 | Massive-scale simulations of 2D Ising and Blume-Capel models on rack-scale multi-GPU systems | [2502.18624](https://arxiv.org/abs/2502.18624) | 2025-02 | 2 | 是 | - |
| 12 | Dissecting CPU-GPU Unified Physical Memory on AMD MI300A APUs | [2508.12743](https://arxiv.org/abs/2508.12743) | 2025-08 | 1 | 是 | - |
| 13 | GPUVM: GPU-driven Unified Virtual Memory | [2411.05309](https://arxiv.org/abs/2411.05309) | 2024-11 | 1 | 是 | - |
| 14 | Understanding the Synchronization Tax in GPU Scale-Up Domains | [2608.22503](https://arxiv.org/abs/2608.22503) | 2026-08 | 0 | 是 | - |
| 15 | FlashBoot: Sub-Second Weight Loading for Large Models at Rack Scale | [2608.08482](https://arxiv.org/abs/2608.08482) | 2026-08 | 0 | 是 | - |
| 16 | Completion-Path Credits: Multi-Resource Control for Scale-Up Fabrics | [2608.17523](https://arxiv.org/abs/2608.17523) | 2026-08 | 0 | 是 | - |
| 17 | Cooling Channel Design Optimization for High Power Multi-Chip Packages | [2605.20657](https://arxiv.org/abs/2605.20657) | 2026-05 | 0 | 是 | - |
| 18 | Provisioning to Runtime Optimization of a 100 MW-Scale AI Cluster | [2605.24461](https://arxiv.org/abs/2605.24461) | 2026-05 | 0 | 是 | - |
| 19 | Instant GPU Efficiency Visibility at Fleet Scale | [2605.20799](https://arxiv.org/abs/2605.20799) | 2026-05 | 0 | 是 | - |
| 20 | C2CServe: Leveraging NVLink-C2C for Elastic Serverless LLM Serving on MIG | [2605.19481](https://arxiv.org/abs/2605.19481) | 2026-05 | 0 | 是 | - |
| 21 | DWDP: Distributed Weight Data Parallelism for High-Performance LLM Inference on NVL72 | [2604.01621](https://arxiv.org/abs/2604.01621) | 2026-04 | 0 | 是 | - |
| 22 | Generative Design for Direct-to-Chip Liquid Cooling for Data Centers | [2604.10941](https://arxiv.org/abs/2604.10941) | 2026-04 | 0 | 是 | - |
| 23 | FlashAttention-4: Algorithm and Kernel Pipelining Co-Design for Asymmetric Hardware Scaling | [2603.05451](https://arxiv.org/abs/2603.05451) | 2026-03 | 0 | 是 | - |
| 24 | Scalable Training of Mixture-of-Experts Models with Megatron Core | [2603.07685](https://arxiv.org/abs/2603.07685) | 2026-03 | 0 | 是 | - |
| 25 | Revealing the Challenges of Attention-FFN Disaggregation for Modern MoE Models and Hardware Systems | [2602.09721](https://arxiv.org/abs/2602.09721) | 2026-02 | 0 | 是 | - |
| 26 | TraCT: Disaggregated LLM Serving with CXL Shared Memory KV Cache at Rack-Scale | [2512.18194](https://arxiv.org/abs/2512.18194) | 2025-12 | 0 | 是 | - |
| 27 | CXL and the Return of Scale-Up Database Engines | [2401.01150](https://arxiv.org/abs/2401.01150) | 2024-01 | 0 | 是 | - |

## 三、E2 检索结果（设备管理统一性 / 资源解耦 / 可组合基础设施）

| # | 标题 | arXiv ID | 年月 | 引用数 | OA PDF | 优先级标记 |
|---|------|----------|------|--------|--------|------------|
| 1 | Allo: A Programming Model for Composable Accelerator Design | [2404.04815](https://arxiv.org/abs/2404.04815) | 2024-04 | 40 | 是 | - |
| 2 | Ditto: An Elastic and Adaptive Memory-Disaggregated Caching System | [2309.10239](https://arxiv.org/abs/2309.10239) | 2023-09 | 20 | 是 | - |
| 3 | DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving | [2401.09670](https://arxiv.org/abs/2401.09670) | 2024-01 | 15 | 是 | - |
| 4 | Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving | [2407.00079](https://arxiv.org/abs/2407.00079) | 2024-07 | 13 | 是 | - |
| 5 | BurstGPT: A Real-world Workload Dataset to Optimize LLM Serving Systems | [2401.17644](https://arxiv.org/abs/2401.17644) | 2024-01 | 9 | 是 | - |
| 6 | DxPU: Large-scale Disaggregated GPU Pools in the Datacenter | [2310.04648](https://arxiv.org/abs/2310.04648) | 2023-10 | 8 | 是 | - |
| 7 | Infinite-LLM: Efficient LLM Service for Long Context with DistAttention and Distributed KVCache | [2401.02669](https://arxiv.org/abs/2401.02669) | 2024-01 | 6 | 是 | - |
| 8 | Inference without Interference: Disaggregate LLM Inference for Mixed Downstream Workloads | [2401.11181](https://arxiv.org/abs/2401.11181) | 2024-01 | 6 | 是 | - |
| 9 | Data Processing with FPGAs on Modern Architectures | [2304.03044](https://arxiv.org/abs/2304.03044) | 2023-04 | 6 | 是 | - |
| 10 | DisaggRec: Architecting Disaggregated Systems for Large-Scale Personalized Recommendation | [2212.00939](https://arxiv.org/abs/2212.00939) | 2022-12 | 5 | 是 | - |
| 11 | Characterizing Off-path SmartNIC for Accelerating Distributed Systems | [2212.07868](https://arxiv.org/abs/2212.07868) | 2022-12 | 5 | 是 | - |
| 12 | SparseTIR: Composable Abstractions for Sparse Compilation in Deep Learning | [2207.04606](https://arxiv.org/abs/2207.04606) | 2022-07 | 5 | 是 | - |
| 13 | Outback: Fast and Communication-Efficient Index for Key-Value Store on Disaggregated Memory | [2502.08982](https://arxiv.org/abs/2502.08982) | 2025-02 | 3 | 是 | - |
| 14 | A Programming Model for Disaggregated Memory over CXL | [2407.16300](https://arxiv.org/abs/2407.16300) | 2024-07 | 3 | 是 | - |
| 15 | Relax: Composable Abstractions for End-to-End Dynamic Machine Learning | [2311.02103](https://arxiv.org/abs/2311.02103) | 2023-11 | 3 | 是 | - |
| 16 | CXLMemSim: A pure software simulated CXL.mem for performance characterization | [2303.06153](https://arxiv.org/abs/2303.06153) | 2023-03 | 3 | 是 | - |
| 17 | ALCOP: Automatic Load-Compute Pipelining in Deep Learning Compiler for AI-GPUs | [2210.16691](https://arxiv.org/abs/2210.16691) | 2022-10 | 3 | 是 | - |
| 18 | Tropical: Enhancing SLO Attainment in Disaggregated LLM Serving via SLO-Aware Multiplexing | [2606.16264](https://arxiv.org/abs/2606.16264) | 2026-06 | 2 | 是 | - |
| 19 | CXL-DMSim: A Full-System CXL Disaggregated Memory Simulator With Comprehensive Silicon Validation | [2411.02282](https://arxiv.org/abs/2411.02282) | 2024-11 | 2 | 是 | - |
| 20 | MemServe: Context Caching for Disaggregated LLM Serving with Elastic Memory Pool | [2406.17565](https://arxiv.org/abs/2406.17565) | 2024-06 | 2 | 是 | - |
| 21 | LoongServe: Efficiently Serving Long-Context Large Language Models with Elastic Sequence Parallelism | [2404.09526](https://arxiv.org/abs/2404.09526) | 2024-04 | 2 | 是 | - |
| 22 | In-Storage Domain-Specific Acceleration for Serverless Computing | [2303.03483](https://arxiv.org/abs/2303.03483) | 2023-03 | 2 | 是 | - |
| 23 | FUSEE: A Fully Memory-Disaggregated Key-Value Store (Extended Version) | [2301.09839](https://arxiv.org/abs/2301.09839) | 2023-01 | 2 | 是 | - |
| 24 | TokenScale: Timely and Accurate Autoscaling for Disaggregated LLM Serving with Token Velocity | [2512.03416](https://arxiv.org/abs/2512.03416) | 2025-12 | 1 | 是 | - |
| 25 | HydraInfer: Hybrid Disaggregated Scheduling for Multimodal Large Language Model Serving | [2505.12658](https://arxiv.org/abs/2505.12658) | 2025-05 | 1 | 是 | - |
| 26 | MIST: A Co-Design Framework for Heterogeneous, Multi-Stage LLM Inference | [2504.09775](https://arxiv.org/abs/2504.09775) | 2025-04 | 1 | 是 | - |
| 27 | Efficiently Serving Large Multimodal Models Using EPD Disaggregation | [2501.05460](https://arxiv.org/abs/2501.05460) | 2025-01 | 1 | 是 | - |
| 28 | KVDirect: Distributed Disaggregated LLM Inference | [2501.14743](https://arxiv.org/abs/2501.14743) | 2025-01 | 1 | 是 | - |
| 29 | Accelerating Retrieval-Augmented Generation | [2412.15246](https://arxiv.org/abs/2412.15246) | 2024-12 | 1 | 是 | - |
| 30 | Disdp: Disaggregating Compute, Network, and Storage for Model-Sharded Data-Parallel Training | [2409.00918](https://arxiv.org/abs/2409.00918) | 2024-09 | 1 | 是 | - |

## 四、E3 检索结果（互联互通 / 互连拓扑 / CXL / 集合通信）

| # | 标题 | arXiv ID | 年月 | 引用数 | OA PDF | 优先级标记 |
|---|------|----------|------|--------|--------|------------|
| 1 | PIM Is All You Need: A CXL-Enabled GPU-Free System for Large Language Model Inference | [2502.07578](https://arxiv.org/abs/2502.07578) | 2025-02 | 42 | 是 | - |
| 2 | Exploring GPU-to-GPU Communication: Insights into Supercomputer Interconnects | [2408.14090](https://arxiv.org/abs/2408.14090) | 2024-08 | 21 | 是 | - |
| 3 | TopoOpt: Co-optimizing Network Topology and Parallelization Strategy for Distributed Training Jobs | [2202.00433](https://arxiv.org/abs/2202.00433) | 2022-02 | 17 | 是 | - |
| 4 | ZeRO++: Extremely Efficient Collective Communication for Giant Model Training | [2306.10209](https://arxiv.org/abs/2306.10209) | 2023-06 | 15 | 是 | - |
| 5 | Pond: CXL-Based Memory Pooling Systems for Cloud Platforms | [2203.00241](https://arxiv.org/abs/2203.00241) | 2022-03 | 14 | 是 | - |
| 6 | GPU Graph Processing on CXL-Based Microsecond-Latency External Memory | [2312.03113](https://arxiv.org/abs/2312.03113) | 2023-12 | 7 | 是 | - |
| 7 | Cosmos: A CXL-Based Full In-Memory System for Approximate Nearest Neighbor Search | [2505.16096](https://arxiv.org/abs/2505.16096) | 2025-05 | 6 | 是 | - |
| 8 | An Introduction to the Compute Express Link (CXL) Interconnect | [2306.11227](https://arxiv.org/abs/2306.11227) | 2023-06 | 5 | 是 | - |
| 9 | A Homogeneous Processing Fabric for Matrix-Vector Multiplication and Associative Search Using Ferroelectric Time-Domain Compute-in-Memory | [2209.11971](https://arxiv.org/abs/2209.11971) | 2022-09 | 5 | 是 | - |
| 10 | cMPI: Using CXL Memory Sharing for MPI One-Sided and Two-Sided Inter-Node Communications | [2510.05476](https://arxiv.org/abs/2510.05476) | 2025-10 | 4 | 是 | - |
| 11 | My CXL Pool Obviates Your PCIe Switch | [2503.23611](https://arxiv.org/abs/2503.23611) | 2025-03 | 4 | 是 | - |
| 12 | Telepathic Datacenters: Fast RPCs using Shared CXL Memory | [2408.11325](https://arxiv.org/abs/2408.11325) | 2024-08 | 3 | 是 | - |
| 13 | Memory Sharing with CXL: Hardware and Software Design Approaches | [2404.03245](https://arxiv.org/abs/2404.03245) | 2024-04 | 3 | 是 | - |
| 14 | GC3: An Optimizing Compiler for GPU Collective Communication | [2201.11840](https://arxiv.org/abs/2201.11840) | 2022-01 | 3 | 是 | - |
| 15 | A Novel Extensible Simulation Framework for CXL-Enabled Systems | [2411.08312](https://arxiv.org/abs/2411.08312) | 2024-11 | 2 | 是 | - |
| 16 | Rethinking Machine Learning Collective Communication as a Multi-Commodity Flow Problem | [2305.13479](https://arxiv.org/abs/2305.13479) | 2023-05 | 2 | 是 | - |
| 17 | Bandwidth Optimal Pipeline Schedule for Collective Communication | [2305.18461](https://arxiv.org/abs/2305.18461) | 2023-05 | 2 | 是 | - |
| 18 | Non-destructive Fault Diagnosis of Electronic Interconnects by Learning Signal Patterns of Reflection Coefficient in the Frequency Domain | [2304.10207](https://arxiv.org/abs/2304.10207) | 2023-04 | 2 | 是 | - |
| 19 | Comprehensive Deadlock Prevention for GPU Collective Communication | [2303.06324](https://arxiv.org/abs/2303.06324) | 2023-03 | 2 | 是 | - |
| 20 | Efficient Direct-Connect Topologies for Collective Communications | [2202.03356](https://arxiv.org/abs/2202.03356) | 2022-02 | 2 | 是 | - |
| 21 | Dissecting CXL Memory Performance at Scale: Analysis, Modeling, and Optimization | [2409.14317](https://arxiv.org/abs/2409.14317) | 2024-09 | 1 | 是 | - |
| 22 | DeepOps & SLURM: Your GPU Cluster Guide | [2405.00030](https://arxiv.org/abs/2405.00030) | 2024-05 | 1 | 是 | - |
| 23 | Exploring and Evaluating Real-world CXL: Use Cases and System Adoption | [2405.14209](https://arxiv.org/abs/2405.14209) | 2024-05 | 1 | 是 | - |
| 24 | GPU Cluster Scheduling for Network-Sensitive Deep Learning | [2401.16492](https://arxiv.org/abs/2401.16492) | 2024-01 | 1 | 是 | - |
| 25 | HybridTier: an Adaptive and Lightweight CXL-Memory Tiering System | [2312.04789](https://arxiv.org/abs/2312.04789) | 2023-12 | 1 | 是 | - |
| 26 | Isolated Scheduling for Distributed Training Tasks in GPU Clusters | [2308.05692](https://arxiv.org/abs/2308.05692) | 2023-08 | 1 | 是 | - |
| 27 | A Case for CXL-Centric Server Processors | [2305.05033](https://arxiv.org/abs/2305.05033) | 2023-05 | 1 | 是 | - |
| 28 | Optimization of Topology-Aware Job Allocation on a High-Performance Computing Cluster by Neural Simulated Annealing | [2302.03517](https://arxiv.org/abs/2302.03517) | 2023-02 | 1 | 是 | - |
| 29 | Elixir: Train a Large Language Model on a Small GPU Cluster | [2212.05339](https://arxiv.org/abs/2212.05339) | 2022-12 | 1 | 是 | - |
| 30 | End-to-End Learning for VCSEL-based Optical Interconnects: State-of-the-Art, Challenges, and Opportunities | [2211.14481](https://arxiv.org/abs/2211.14481) | 2022-11 | 1 | 是 | - |

---

## 中间产物

- `arxiv_raw.json`：OpenAlex 原始召回（含完整摘要、作者、concepts、query 来源、OA 状态）
- `arxiv_final.json`：严格过滤+去重+分组 cap 30 后的最终 90 条结构化结果（供第二遍深拉）
- `openalex_search.py` / `refine.py` / `verify_ub.py` / `gen_md.py`：检索/重筛/核对/生成脚本（可复现）
