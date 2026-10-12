# Paper Card — UBEP: Re-architecting Expert Parallelism Communication Library for Production Superpods

> **证据状态**（Evidence status）
> Source coverage: Full paper（18 页 PDF 全文，含 Appendix A/B 与三张全页图；无补充材料声明）
> Extraction confidence: High（正文文本层；公式层为 cid 乱码、译文按语义重建为 medium）
> Locator mode: **page-grounded**（printed 页码与 PDF 页码一致）
> Primary analytical lens: **methods**（通信库/系统）
> Secondary analytical lens: None
> Context verification: **Paper-only**（领域脉络处标注 `[Paper-framed; external verification not performed]`）
> Card completeness: Complete relative to supplied source
>
> 关联产物：同论文 nature-reader 双语精读（`../nature-reader/paper.md`，行级零丢失校验）；姊妹篇 CM384 的 Paper Card（`../../CloudMatrix384_2025/nature-paper-card/paper-card.md`）。

---

## 01 基本信息

| 项 | 内容 |
|---|---|
| 标题 | UBEP: Re-architecting Expert Parallelism Communication Library for Production Superpods |
| 作者与机构 | Yipeng Liu, Chang Liu, Si Shen, Jiaqi Zheng（南京大学）, Mingfan Li, Yuyang Yang, Guanhua Li, Y. Liu 等；上海交通大学 & 华为（CM384 团队） |
| 发表 | arXiv:2607.06202，SIGCOMM '26（2026-08，Denver），预印本 |
| 论文类型 | methods（专家并行通信库）；领域：AI 基础设施 / 网络与系统 |
| 关键词 | MoE、expert parallelism、all-to-all、CM384、UB、kernel decomposition、Data-as-Flag、hierarchical token-level scheduling |
| 代码/数据 | 论文未声明开源（Not stated in paper） |
| 阅读日期 | 2026-10-12 |
| 与课题的关系 | [User] 本课题核心标的：CM384（华为对等超节点）上的生产级 EP 通信库——"超节点软件层如何吃满统一互连"的实证样本，与 CM384 论文（引文 [22]）构成硬件/软件配对 |

## 02 一句话总结

针对生产超节点（CM384，256 NPU die）上 MoE all-to-all 通信被 BSP 式全局屏障与粗粒度核所限的问题，UBEP 把单体 all-to-all 拆解为依赖驱动的细粒度任务（核分解）、用 512B 原子写实现"数据即标志"的无屏障同步、并以分层 token 级调度均衡 AIV 负载，在生产 superpod 上报告：相对 CANN EP 带宽提升 35.3%–40.8%、消融中 Data-as-Flag 变体降时延最高 31.0%–57.1%、端到端推理 P99 时延降最多 11.1%（vLLM-Ascend，Qwen3/GLM/DeepSeek 多模型）[Paper: PDF p. 9–11, Table 4, Fig. 7–11]。

## 03 研究问题

- **具体问题**：生产超节点上的 MoE 推理，all-to-all 分发/合并受制于 BSP 执行模型：全局屏障、粗粒度内核、跨 AIV 同步开销 [Paper: PDF p. 3, §2.3]。
- **为何重要**：MoE 通信约占每-token 时延的 50%、但只占实际硬件执行时间的 ~20%——大量时间耗在依赖停顿与运行时开销上 [Paper: PDF p. 11, §5.5]。
- **现有方案不足**：EPCL（DeepEP [51]、UCCL-EP [28]）面向 IB/NVLink 集群的粗粒度 BSP 核；Hybrid-EP [32] 处理单层超节点但不处理分层拓扑；FUSCO [56] 假设成对流量 [Paper: PDF p. 12, §7]。
- **精确研究问题（Can...?）**：Can a communication library exploit superpod-native primitives (512B atomics, UGAS, AIV-level parallelism) to dismantle the BSP execution model of MoE all-to-all without changing model semantics? [Analysis：由主张归纳]

## 04 研究背景与发展脉络

`[Paper-framed; external verification not performed]`

| 阶段 | 代表 | 优势 | 局限（论文口径） | 本文定位 |
|---|---|---|---|---|
| EPCL for IB/NVLink | DeepEP [51]、UCCL-EP [28] | 传统集群上的成熟 all-to-all | 粗粒度 BSP 式核，跨层拓扑不敏感 | 超节点原生重构 [Paper: PDF p. 12, §7] |
| 异步/单层超节点 | Hybrid-EP [32] | 异步并行 | 不处理分层拓扑 | 分层 token 级调度 |
| 应用层均衡 | EPLB [6]、LPLB [5] | 重塑流量模式 | 在应用层动态改 token 分配 | UBEP 在底层编排：接受不均衡流量、最大化有效带宽 [Paper: PDF p. 12, §7] |
| 硬件上下文 | CM384/UB（UGAS、512B 原子写）[22] | 对等互连 + 统一地址语义 | 软件栈（CANN EP）未吃满硬件 | 本文即"吃满"的软件层答案 |

## 05 论文识别的核心痛点

| 痛点 | 表现 | 成因（作者解释） | 论文证据 |
|---|---|---|---|
| BSP 全局屏障 | 阶段间插入 SyncAll，等待最慢者 | 传统执行模型 | [Paper: PDF p. 3, §2.3, Fig. 2] |
| 粗粒度内核 | 单体 all-to-all 无法与计算重叠 | EPCL 按阶段划分 | [Paper: PDF p. 8–9, §5.2–5.3, Fig. 8] |
| AIV 间负载不均 | token 分配倾斜 → 部分向量核闲置 | MoE 流量天然不均 | [Paper: PDF p. 6–7, §3.3] |
| 同步开销随规模增长 | rank 数增多、粒度增大时开销占比上升 | 跨 AIV 同步机制 | [Paper: PDF p. 10, §5.4] |
| 通信占比高但硬件利用率低 | 50% 时延 vs 20% 执行时间 | 依赖停顿 + 运行时开销 | [Paper: PDF p. 11, §5.5] |

## 06 核心思想

1. **表面方法**：核分解 + Data-as-Flag 同步 + 分层 token 级调度，约 1 万行 Ascend C 实现，构建于 CANN/UB 原语之上 [Paper: PDF p. 8, §4]。
2. **核心洞察**：当互连提供 UGAS + 细粒度原子写时，**同步可以从"显式屏障"降解为"数据自身的到达信号"**——把 flag 内嵌进 512B 数据块的原子写里，接收方靠轮询/验证数据就绪即完成同步，全局屏障随之消失 [Paper: PDF p. 7, §3.4]。
3. **一般性启示** [Analysis]：与 CM384 的"互连拉平→调度自由"配对后完整成形——**硬件给的原语粒度（原子写、统一地址）决定软件能删除哪类同步结构**；原语粒度越细，可删除的全局协调越多（本文 §6 进一步展望把 flag 也卸给专用硬件单元）。

## 07 方法总览

- **输入**：MoE 层的 token 分发/合并请求（EP 规模 16–256 rank）。
- **输出**：完成 all-to-all 的 token 流（分发给专家、合并回聚合）。
- **模块**：① **核分解**（Kernel Decomposition）：把单体 all-to-all 拆为 Init / Token-Sending / SendFlag & Verification / CalCumSum / Token-Reordering 五阶段依赖驱动任务，AIV 分组并行 [Paper: PDF p. 3, §3.2; p. 9, §5.3, Fig. 8]；② **Data-as-Flag 同步**：三变体（TFF=512B 原子写 flag+payload；DC=数据+校验和；SP=哨兵轮询），以 UB 原生 512B 原子写为基础 [Paper: PDF p. 7, §3.4, Fig. 6]；③ **分层 token 级调度**：硬件加速 mapper（NP-hard 分配的启发式：时延均质化 + 跳数分布均衡 + 每-跳容量上界），在 1 µs 内生成调度 [Paper: PDF p. 6, §3.3, Eq. 1; Algorithm 1 四叉搜索]；④ **生产集成**：CANN 栈内 ~10K 行 Ascend C，vLLM-Ascend v0.14.0 插件 [Paper: PDF p. 8, §4; p. 11, §5.5]。
- **数据流（文本）**：token 就绪 → mapper 给出 AIV 分配 → 发送 AIV 组装 512B 块（flag 内嵌）原子写远端 UBuf → 接收 AIV 轮询验证 → CalCumSum 累计 → 重排 → 专家计算 → 反向合并同理。
- **假设**：UB 提供 512B 原子写与 UGAS（Table 5 列出三假设与非 CM384 退化路径）[Paper: PDF p. 11, §6, Table 5]；静态 EP 映射（每 rank 专家数固定）。

## 08 核心模块拆解

| 模块 | 功能 | 为何需要 | 输入 → 输出 | 支持证据 | 移除/退化的影响 |
|---|---|---|---|---|---|
| 核分解 | 五阶段依赖驱动任务 | 打破 BSP 串行、暴露并行度 | 单体 all-to-all → AIV 任务图 | **隔离消融**：Fig. 8 逐阶段时延分解（64 NPU、每 NPU 一专家、3 档 batch）[Paper: PDF p. 9, §5.3] | 回到 CANN EP 五阶段串行 + 全局屏障（对照即此） |
| Data-as-Flag（TFF/DC/SP 三变体） | 无屏障同步 | 消除 stop-and-wait 与跨 AIV 同步 | flag 内嵌 512B 原子写 → 接收方就绪即知 | **隔离消融**：§5.4 各变体 vs CANN EP，降时延最高 31.0%–57.1% [Paper: PDF p. 10, §5.4, Fig. 6] | 回退全局屏障；无原子写时退化为 DC/显式 fence（Table 5 退化路径）[Paper: PDF p. 11, §6] |
| 分层 token 级调度 | 均衡 AIV 负载（时延均质化 + 跳数方差最小化 + 容量上界） | 流量不均导致部分 AIV 闲置 | token 集 → AIV 分配表 | Fig. 7：BS 8–64 平均 +46.4%（BS=128 降至 +35.9%）[Paper: PDF p. 9, §5.2, Fig. 7]；mapper 1 µs 内出调度 [Paper: PDF p. 6, §3.3] | 负载不均回归（未单独消融调度器，见 §13） |
| 生产集成（CANN/vLLM-Ascend） | 可部署性 | 生产库定位 | vLLM 插件 | E2E：P99 最多 −11.1%（多模型、≥100 解码步采样）[Paper: PDF p. 11, §5.5, Fig. 11] | 纯研究原型 |

## 09 关键公式与符号

本文核心形式化为 **§3.3 的 token→AIV 分配优化**（Eq. 1, 1a–1c）[Paper: PDF p. 6]：

- 目标：minimize max_ℓ max_{i∈M_j} RTT(i)——最小化"最慢 AIV 上最慢 token"的完成时间（RTT = 传输时延 ℓ_i + 网络时延）。
- 约束 (1a) 每 token 恰配一个 AIV；(1b) 负载均衡（无 AIV 超过公平份额）；(1c) 二元变量。
- 论文证明该程序 **NP-hard**（证明在 Appendix B），启发式 = 时延均质化（传输项近似为常数）+ 跳数分布方差最小化（等价于最小化 tr Σ，Σ 为 AIV 跳数分布的协方差）+ 每-跳容量上界 v_{j,h} ≤ ⌈V_h/n⌉ [Paper: PDF p. 6–7]。
- **微例**（手算演示跳数均衡）[Analysis]：设 2 个 AIV、8 个 token，其中 6 个为 1-跳（1µs/个）、2 个为 2-跳（3µs/个），容量上界 ⌈V_h/n⌉：1-跳每 AIV ⌈6/2⌉=3、2-跳 ⌈2/2⌉=1。均衡分配 A1={3×1跳, 1×2跳}=3+3=6µs，A2 同=6µs → max=6µs。不均衡分配 A1={4×1跳,0}=4µs、A2={2×1跳,2×2跳}=2+6=8µs → max=8µs。均衡策略把 max 从 8 降到 6——这正是"时延均质化"目标 min-max 的直接效果；公式的两个可加项（传输 + 网络）分别由 token 同尺寸与跳数均衡两个观察近似消解。
- NP-hard 证明在附录 B，正文仅引用结论；式 (2)–(14)（附录推导）的 PDF 数学层为 cid 乱码，本卡未逐式核对（Not assessable from supplied material at character level）。

## 10 实验设计与证据链

**评测设置** [Paper: PDF p. 8, §5.1]：生产级 CM384 superpod 中分配 16 台昇腾服务器（256 NPU die）、统一互连 fabric；训练/推理均 MindSpore 生态；推理基于 vLLM-Ascend v0.14.0；对照为同硬件同拓扑的 CANN EP（基线）与 DeepEP（H800 上作协议能力参照）。

**证据清单**（全量，含未进入证据链的配图）：Figure 1（传统集群 vs UB 超节点对比动机）、Figure 2（MoE dispatch 工作流：逻辑 SyncAll 视图 vs CM384 物理视图）、Figure 3（运行时驱动预取时间线）、Figure 4（执行序三情形：过晚/过早/最优）、Figure 5（分层内存三种使用模式）、Figure 6（Data-as-Flag 三变体与 512B 原子写）、Figure 7（BS/规模/专家数敏感性）、Figure 8（dispatch 时延分解）、Figure 9（合并算子分解）、Figure 10（Data-as-Flag 消融）、Figure 11（E2E TPOT 分布）、Figure 12（消融补充）、Figure 13（Top-k 可扩展性）、Figure 14（rank×粒度热力图）；Table 1（MoE 通信库对比）、Table 2（CM384 内存访问时延层级：Intra-NPU/一跳/两跳）、Table 3（MoE 模型配置）、Table 4（EPCL 性能对比）、Table 5（可移植性清单）；Equation 1（token→AIV 分配主程序）、Equation 2、Equation 3、Equation 4（约束 1a–1c）、Equation 5、Equation 6、Equation 7、Equation 8、Equation 9、Equation 10、Equation 11、Equation 12、Equation 13、Equation 14、Equation 15（附录 B 推导式，PDF 数学层为 cid 乱码，字符级 Not assessable）。

| 实验 | 验证主张 | 对比与条件 | 结果 | 支持的结论 | 不支持的更强结论 | 来源 |
|---|---|---|---|---|---|---|
| E1 EP 性能对比（Table 4） | UBEP 通信带宽优于 CANN EP | 同硬件同拓扑，大规模集群 | 带宽 +35.3%–40.8% | 核分解+Data-as-Flag+调度组合在同硬件上取得"算法性"增益 | 优于 DeepEP/H800（该列仅为协议能力参照） | [Paper: PDF p. 9, §5.2, Table 4] |
| E2 batch 敏感性（Fig. 7a） | 细粒度 token 级流水线的增益 | BS 8–64 vs 128 | BS 8–64 平均 +46.4%；BS=128 降至 +35.9%（通信量占比上升） | 调度在常规 batch 下增益稳定，大 batch 被通信量稀释 | 大 batch 下无收益退化 | [Paper: PDF p. 9, §5.2, Fig. 7a] |
| E3 核分解时延分解（Fig. 8） | 核分解消除阶段间屏障 | 64 NPU、每 NPU 一专家、3 档 batch；CANN EP 五阶段 vs UBEP | UBEP 消除全局屏障的阶段间等待（论文以 Fig. 8 分解图展示；未给单一汇总百分比） | 核分解改变了执行结构并消除屏障等待 | 屏障消除 = 全部收益来源 | [Paper: PDF p. 9, §5.3, Fig. 8] |
| E4 Data-as-Flag 消融（§5.4） | 无屏障同步优于 CANN EP 同步 | TFF/DC/SP 三变体 × 粒度 × rank 数 | 全变体降时延最高 31.0%–57.1%；收益随粒度增大递减（10 KB 典型分发粒度下约 1 µs） | Data-as-Flag 机制本身贡献显著且机理清楚（去 stop-and-wait + 降跨 AIV 同步） | 粒度增大时收益不衰减（作者明示衰减） | [Paper: PDF p. 10, §5.4, Fig. 6/9] |
| E5 端到端推理（Fig. 11） | 算子级增益传导到 E2E | vLLM-Ascend，Qwen3-30B（16 rank）/GLM（128、160 rank）/DeepSeek-R1 & V3.2（128 rank），每模型 ≥100 解码步 | P99 端到端时延最多 −11.1%；分布整体下移 | 算子级增益传导到 E2E（幅度受 MoE 通信占比 ~50% 限制） | E2E 降幅与算子级降幅同量级 | [Paper: PDF p. 11, §5.5, Fig. 11] |
| E6 剖面分析 | 通信是时延主因之一但非全部 | profiling | MoE 通信 ≈50% 每-token 时延、≈20% 硬件执行时间 | 依赖停顿与运行时开销是主要残余 | 通信优化可消除全部 50% | [Paper: PDF p. 11, §5.5] |

## 11 结论的正确解读

- **基线性质**：核心对照是**同硬件的 CANN EP**——这是"把自家软件栈吃满硬件"的对照，不是与 DeepEP/H800 的跨平台竞赛（DeepEP 列仅作协议能力参照）[Paper: PDF p. 9, Table 4] [Analysis]。
- **口径**：算子级（Table 4/Fig. 7/8/9）与端到端（Fig. 11，P99 归一化）分开报告；E2E 增益（≤11.1%）小于算子级（35–57%）的原因论文自己给出：MoE 通信只占解码步的一部分 [Paper: PDF p. 11, §5.5]。
- **平台绑定**：三假设（512B 原子写、AIV 级并行、分层 fabric）当前调优到 CM384；论文逐条给出非 CM384 硬件上的退化路径（Table 5）——这是少见的诚实处理 [Paper: PDF p. 11, §6]。
- **调度器的独立贡献**：§5.2 的对照是"baseline 机制 vs 细粒度 token 级流水线"（即含调度器），**没有"无调度器的 Data-as-Flag+核分解"臂**——调度器贡献与 Data-as-Flag 贡献未完全隔离 [Analysis]。
- **有界重述**：论文证明了——在 CM384 生产 superpod 上，UBEP 相对 CANN EP 把 all-to-all 带宽提升 35.3–40.8%，三个机制各自的消融/分解证据方向一致，且以 vLLM-Ascend 插件形态在四个 MoE 模型上取得最高 11.1% 的 P99 端到端改善；它没有证明——相对 DeepEP 等外部 EPCL 的优越性、在非 UB 硬件上的等效性，以及调度器本身的隔离贡献。

## 12 作者明确承认的局限

| 局限 | 具体表现 | 作者提出的未来方向 | 来源 |
|---|---|---|---|
| 大粒度下同步收益递减 | 10 KB 典型分发粒度下增益仅约 1 µs | ——（解释为通信时间占比上升） | [Paper: PDF p. 10, §5.4] |
| 软件级 Data-as-Flag 限制细粒度扩展 | 进入微秒域后软件 flag 处理成为瓶颈 | 把控制信号卸载到专用硬件单元（引 TPU SparseCore Scatter-Gather、AWS Trainium CC-Core 为例）；UB 增加 Write-with-Notify/Remote-Sync-Write 类接收端序语义 | [Paper: PDF p. 11, §6] |
| E2E 增益小于算子级 | P99 最多 −11.1% vs 算子级 35–57% | 把细粒度依赖驱动机制扩展到其他集合通信与计算 | [Paper: PDF p. 11, §5.5] |

**Related constraints noted by the authors**：三假设的跨平台退化路径（Table 5：更小原子粒度、GPU-like 架构映射、更平 fabric 退化为一般负载均衡）[Paper: PDF p. 11, §6, Table 5]。

## 13 批判性分析

| `[Analysis]` 观察 | 潜在问题/替代解释 | 为何重要 | 如何检验 | 依据 |
|---|---|---|---|---|
| 调度器无隔离消融 | Fig. 7 的增益可能部分来自流水线化而非调度算法本身 | 分层调度是三设计之一 | 加"固定 round-robin 分配 + 其余不变"臂 | [Paper: PDF p. 9, §5.2] |
| 基线为自家 CANN EP | DeepEP/UCCL-EP 在 H800/IB 上的绝对水平未比（仅"协议能力参照"） | 跨平台竞争力未证 | 在 H800 上以同拓扑模拟 CM384 分层时延跑 DeepEP 对照 | [Paper: PDF p. 9, Table 4] |
| 512B 原子写假设强绑定 UB | 换硬件即触发 Table 5 退化路径（低 payload 效率或退化为 DC/fence） | 通用性主张受硬件原语约束 | 在具备/不具备原子写的两种 fabric 上复测三变体 | [Paper: PDF p. 11, Table 5] |
| LLaMA 基线缺失（无 dense 对照） | 全部负载为 MoE；dense 模型不受 EP 影响，属范围选择而非缺陷 | 界定适用面即可 | ——（范围声明已足够） | [Paper: PDF p. 11, §5.5] |
| 附录公式为 cid 乱码 | NP-hard 证明与式 (2)–(14) 无法逐字符核对 | 证明正确性未独立验证 | 联系作者获取证明源文件或依赖出版版 | [Paper: PDF p. 6, 16–18] |

## 14 收获知识

**Agent-derived knowledge candidates**：

1. **Data-as-Flag 同步范式**：flag 不再是独立控制消息，而是内嵌进数据块的原子写——数据到达即同步完成。三变体（原子写/校验和/哨兵）对应硬件原子粒度的三种能力档 [Paper: PDF p. 7, §3.4]。
2. **微秒域的 BSP 消除论**：当内核进入 µs 量级，全局屏障（几十 µs 级）成为主导项——BSP 模型的废除不是优化而是必选项 [Paper: PDF p. 11, §6]。
3. **min-max 调度的两项分解**：传输项（token 同尺寸→近似常数）+ 网络项（跳数分布方差）——把 NP-hard 分配问题降解为"时延均质化 + 每-跳容量上界"的可解启发式 [Paper: PDF p. 6, §3.3]。
4. **"应用层均衡 vs 底层编排"的分工论**：EPLB/LPLB 在应用层重塑流量，UBEP 接受不均衡流量在底层最大化有效带宽——两层正交，不必互相等待 [Paper: PDF p. 12, §7]。
5. **硬件原语粒度 ↔ 软件同步结构的因果链**：512B 原子写（硬件）→ 无屏障同步（软件结构删除）→ AIV 级重叠（收益）——与 CM384 的"互连带宽→调度自由"构成同族论证 [Analysis，基于两文互引]。

## 15 与已有知识的联系

- **[User]** 本课题直接标的：UBEP 是 CM384 超节点软件层的生产实现，与 CM384 论文（其引文 [22]）构成"硬件层/软件层"配对；其 §6 的硬件 flag 卸载展望恰与 CM384 §6 的 UB 演进方向呼应（课题背景 research/CLAUDE.md）。
- `[Paper-framed; external verification not performed]` 谱系：DeepEP/UCCL-EP（IB/NVLink EPCL）→ Hybrid-EP（单层超节点异步）→ FUSCO → UBEP（分层超节点原生）；EPLB/LPLB（应用层）与本文（编排层）正交。
- `[Analysis]` 候选联系（未核验）：接收端驱动的数据信号与 RMA 完成语义（网络 RDMA 的 immediate data）同族；"把屏障降解为数据到达信号"与无锁队列/发布-订阅的内存序论证同构。

## 16 研究想法

**Agent-derived research candidates**（均为假设/候选，未做 novelty 核验）

### 想法 1：调度器隔离消融（补证三设计分账）

- **来源局限**：§5.2 的增益来自"细粒度 token 级流水线"整体，调度算法本身未隔离（§13 观察一）。
- **核心假设** [Hypothesis]：在固定核分解+Data-as-Flag 的条件下，分层调度相对 round-robin 分配贡献 ≥50% 的带宽增益。
- **Delta**：评测——加消融臂。
- **初始方法**：固定其余组件，替换分配策略为 round-robin / 随机 / 静态 EPLB 三臂，扫 BS 8–128 与 rank 数。
- **验证**：各臂 Table 4 口径带宽；证伪条件——round-robin 臂达到分层调度臂收益的 90%（调度算法非主要贡献）。
- **可能的失败**：组件耦合难以干净开关；负载场景需覆盖天然均衡与极端偏斜两档；平台访问受限。
- **创新状态**：`unverified`（补证实验）。

### 想法 2：flag 处理的硬件卸载原型（对齐作者展望）

- **来源局限**：作者明示软件级 Data-as-Flag 限制微秒域细粒度扩展，展望硬件卸载 [Paper: PDF p. 11, §6]。
- **核心假设** [Hypothesis]：把 flag 轮询/验证卸载到可编程网络/内存单元后，小粒度（≤4 KB）同步开销可降至软件路径的 1/3 以下。
- **Delta**：机制——控制信号从 CPU/AIV 软件路径移到专用单元。
- **初始方法**：在支持可编程 offload 的互连上实现 flag 比较与就绪通知的原型；与软件 Data-as-Flag 对照扫粒度。
- **验证**：小粒度同步时延分布与 CPU 占用；证伪条件——卸载路径时延 ≥ 软件路径的 70%（含单元间往返）。
- **可能的失败**：专用单元编程模型受限；flag 语义（比较+通知）无法完整下推；收益被端到端其他开销稀释。
- **创新状态**：`unverified`；作者已指明方向。

### 想法 3：跨 EPCL 的同台评测（DeepEP/UCCL-EP/Hybrid-EP on CM384）

- **来源局限**：外部 EPCL 未在 CM384 上对照（仅 DeepEP@H800 作协议参照）[Paper: PDF p. 9, Table 4]。
- **核心假设** [Hypothesis]：在同硬件上，DeepEP 类 BSP 设计与 UBEP 的差距大于其在原生集群上相对自家基线的差距（超节点原语放大了 BSP 劣势）。
- **Delta**：评测方法学——同台三臂。
- **初始方法**：移植 DeepEP 的 dispatch/combine 到 CM384/UB（或以参数化时延模型外推），扫 EP 规模与粒度。
- **验证**：同口径带宽/时延表；证伪条件——DeepEP 在 CM384 上达到 UBEP 带宽的 85% 以上（硬件原语差异不构成结构性优势）。
- **可能的失败**：移植保真度存疑（UB 与 RDMA 语义差异）；厂商库调优不对称；仅能覆盖部分算子。
- **创新状态**：`unverified`；直接检验"超节点原生重构"主张。

### 想法 4：Data-as-Flag 在 AFD（Attention-FFN 分离）拓扑上的扩展

- **来源局限**：§6 指出 AFD 把 all-to-all 变为 M2N 二部图模式，并声称 UBEP 设计哲学在该变换下不变但未实验 [Paper: PDF p. 11, §6]。
- **核心假设** [Hypothesis]：Data-as-Flag 的收发解耦在 M2N 非对称流量下仍维持无屏障语义，且时延隐藏效果不劣于对称 all-to-all 场景的 80%。
- **Delta**：部署拓扑——对称 all-to-all → 二部 M2N。
- **初始方法**：在 AFD 原型（Attention 集群 ↔ FFN 专家集群）上部署 UBEP 收发角色分离版，扫流量不对称比。
- **验证**：M2N 时延/带宽 vs 对称基线；证伪条件——非对称比 >4 时吞吐坍塌或正确性回退。
- **可能的失败**：收发角色固定导致 flag 验证资源倾斜；AFD 集群间互连带宽远低于 superpod 内部；调度器假设的"分层均匀带宽"被打破。
- **创新状态**：`unverified`。

### 想法 5：原子粒度梯度上的三变体决策模型

- **来源局限**：Table 5 给出三种硬件退化路径，但未量化"在原子粒度 X 时选哪个变体" [Paper: PDF p. 11, Table 5]。
- **核心假设** [Hypothesis]：三变体（TFF/DC/SP）存在可预测的最优区间，由原子粒度、消息大小、带宽三参数的解析模型给出。
- **Delta**：机制——变体选择从固定配置变为解析决策。
- **初始方法**：扫原子粒度（512B/128B/32B/无）× 消息大小 × 带宽，拟合三变体的时延曲面，导出分段选择规则。
- **验证**：留出硬件配置上验证规则预测的最优变体；证伪条件——规则预测错误率 >20%。
- **可能的失败**：时延曲面受实现细节支配而非三参数；不同 fabric 的原子语义差异超出粒度维度。
- **创新状态**：`unverified`；直接消费 Table 5 的假设清单。
