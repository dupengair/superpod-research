# Paper Card — Serving Large Language Models on Huawei CloudMatrix384

> **证据状态**（Evidence status）
> Source coverage: Full paper（58 页 PDF 全文；p.2–3 为 arXiv 目录页，非正文）
> Extraction confidence: High（可选中文本层 + 既有 nature-reader 双语对照与视觉核验裁片）
> Locator mode: **page-grounded**（printed 页码与 PDF 页码一致，统一使用 `PDF p. N`）
> Primary analytical lens: **methods**（系统/基础设施贡献）
> Secondary analytical lens: None
> Context verification: **Paper-only**（除书目元数据外，未做外部独立核验；涉及领域脉络处标注 `[Paper-framed; external verification not performed]`）
> Card completeness: Complete relative to supplied source
>
> 输入说明：捆绑脚本对 nature-reader source_map.json 的解析失败（`no source block contains enough extractable text`，Pages=0，已按 skill 规则记录），改用原始 PDF 输入重新运行 `prepare_paper.py` 成功（58 页 / 14 sections / 4 equations，validation=valid）。脚本未检出 figures/tables（自动检测局限），本文图 1–24、表 1–10 的证据清单由 nature-reader 阶段的视觉核验裁片（F001–F024 / T001–T010 / C001–C034）补齐。

---

## 01 基本信息

| 项 | 内容 |
|---|---|
| 标题 | Serving Large Language Models on Huawei CloudMatrix384 |
| 作者与机构 | Pengfei Zuo 等 48 人；华为（CloudMatrix 团队）与 SiliconFlow；通信作者 Zhou Yu（华为）、Heng Liao（海思） |
| 发表 | arXiv:2506.12708v3，2025-06，预印本（CC BY 4.0）；无同行评审信息 |
| 论文类型 | methods（系统/基础设施）；领域：AI 基础设施 / 计算机系统体系结构 |
| 关键词 | supernode、Unified Bus（UB，灵衢）、Ascend 910、MoE serving、expert parallelism、KV cache、INT8 quantization |
| 代码/数据 | 论文未给出开源代码、数据集或制品声明（Not stated in paper） |
| 阅读日期 | 2026-10-10 |
| 与课题的关系 | [User] 本课题（超节点多节点设备管理统一性）的核心对标系统：UB 统一内存语义 + 对等架构是"多节点当单一节点管"路线目前最完整的生产级公开样本（research/CLAUDE.md 课题背景） |

## 02 一句话总结

针对万亿参数 MoE 模型服务中层次式互连的带宽断崖与调度局部性约束，论文用全对等 UB 超节点（384 昇腾 910 + 192 鲲鹏）承载 PDC 分离式推理架构 CloudMatrix-Infer，以 EP320 专家并行、融合通信算子、微批次流水线、UB 分布式缓存与 INT8 量化为手段，在 DeepSeek-R1 上报告了 prefill 4.45、decode 1.29 tokens/s/TFLOPS 的计算效率，高于 SGLang@H100（3.75/1.10）与 DeepSeek@H800（3.96/1.17）的已发表数字 [Paper: PDF p. 1 Abstract; PDF p. 39–41, Table 2–4]。

## 03 研究问题

- **具体问题**：如何在生产环境中高吞吐、低时延（TPOT/TTFT 双 SLO）地服务 671B 参数 MoE 模型，同时应对变长输入、突发负载、专家激活不均衡 [Paper: PDF p. 1, §1]。
- **为何重要**：KV 缓存随并发线性增长、all-to-all 通信密集、时延约束收紧，是当前 LLM 推理服务的普遍瓶颈 [Paper: PDF p. 6, §2.1]。
- **现有方案不足**：传统集群节点内（PCIe ≈256 GB/s）与节点间（≈25 GB/s）带宽相差一个量级，迫使 Dynamo、Mooncake 等 KVCache 中心化系统把请求绑定到缓存所在节点，带来调度复杂、负载易失衡、解码节点 DRAM 孤岛化三个代价 [Paper: PDF p. 18, §4.1]。
- **精确研究问题（Can...?）**：Can a fully peer-to-peer, high-bandwidth supernode eliminate the need for cache-locality-aware scheduling and make pooled, independently scaled prefill/decode/caching resources efficient enough to beat published per-TFLOPS serving efficiency on H100/H800? [Analysis：由论文主张归纳；论文本身未以假设形式陈述]

## 04 研究背景与发展脉络

`[Paper-framed; external verification not performed]`

| 阶段 | 代表工作 | 优势 | 局限（论文口径） | 本文定位 |
|---|---|---|---|---|
| 分层集群 + KVCache 中心化调度 | NVIDIA Dynamo [41]、Mooncake [48] | 缓存感知调度规避远程 KV 访问惩罚 | 带宽断崖（256 vs 25 GB/s）导致调度迁就局部性；DRAM 孤岛 | 用对等超节点取消局部性约束 [Paper: PDF p. 18, §4.1] |
| GPU 大规模训练/推理集群 | TopoOpt 类拓扑优化、HPN 等组网 [Paper: PDF p. 6–7, §2 引文群] | 以交换机/链路冗余换带宽 | 面向训练为主；层次式跨节点语义 | 全对等 UB 两跳直达、无收敛 L2 |
| MoE 推理通信 | DeepEP [56]、SGLang [53] | RDMA all-to-all 优化 | 大 EP 度下时延/带宽受限（论文对比数据口径） | 融合算子 + AIV 直连替代 all-to-all [Paper: PDF p. 22, Fig. 11–12] |

[Analysis] 论文把自身定位为"首个生产级超节点实现"（CloudMatrix384）；该历史定位仅来自论文叙述与厂商发布口径，本卡未做独立外部核验。

## 05 论文识别的核心痛点

| 痛点 | 表现 | 成因（作者解释） | 论文证据 |
|---|---|---|---|
| 节点间带宽断崖 | 节点内 256 GB/s vs 节点间 25 GB/s | 层次式组网的物理与成本约束 | [Paper: PDF p. 18, §4.1] |
| 调度迁就 KV 局部性 | 请求绑定缓存节点，动态负载下失衡 | 远程 KV 访问代价过高 | [Paper: PDF p. 18, §4.1] |
| all-to-all 通信开销 | 3 次 all-to-all、动态形状、顺序依赖 | MoE 计算范式固有 | [Paper: PDF p. 20–21, §4.2.1] |
| KV 缓存线性增长 | 并发×上下文乘积放大存储与带宽需求 | 注意力机制固有 | [Paper: PDF p. 6, §2.1] |
| 模型加载/切换慢 | 8 实例抢 2.5 GB/s OBS，冷启动 2,560 s | 本地缓存各自囤全量副本 | [Paper: PDF p. 37, Table 1] |
| 量化精度-效率矛盾 | INT8 提效但长尾激活伤精度 | 权重/激活分布离群 | [Paper: PDF p. 37–38, §4.5] |

[Analysis] 注意：以上均为论文识别并论证的痛点，其"成因"列多为作者解释而非被独立验证的根因。

## 06 核心思想

1. **表面方法**：造一个全对等超节点（CM384），并在其上写一套配套推理栈（CloudMatrix-Infer：PDC 分离 + EP320 + 融合算子/微批次/MTP + EMS 缓存 + INT8）。
2. **核心洞察**：当互连把"任意芯粒间"的访问带宽与语义拉平后，**数据局部性不再需要成为调度的第一约束**——缓存、专家、算力都可以当成全局可寻址资源池化 [Paper: PDF p. 8, §3.1 "everything can be pooled, treated equally, and combined freely"]。
3. **一般性启示** [Analysis]：系统设计中"互连质量决定调度自由度"——互连每上一个台阶，就有一类为规避远程访问而生的复杂度（affinity 调度、副本放置、局部性哈希）可以被简化掉；反之互连不足时，软件复杂度只是被转移到调度层。

## 07 方法总览

- **输入**：DeepSeek-R1（671B MoE，256 路由专家 + 共享专家）推理请求（变长 prompt / 输出）。
- **输出**：生成 token 流，满足 TPOT/TTFT SLO。
- **硬件模块**：384×Ascend 910（双芯粒，768 die）+ 192×鲲鹏 CPU；UB 两级交换（L1 板载 + L2 机柜级，7 子平面×16 芯片×48 端口，L2 无收敛）[Paper: PDF p. 10–13, Fig. 2–5]。
- **软件模块**：CANN 算子层 → CloudMatrix-Infer 运行时（PDC 调度、FusedDispatch/FusedCombine、MLA 算子、微批次流水线、MTP 支持、EMS 弹性内存服务）→ 云部署层 [Paper: PDF p. 12–15, Fig. 6–7]。
- **数据流（文本）**：请求 → 全局调度器按负载分发到 prefill 池 → KV 经 UB 写入缓存池/decode 池（非局部性路由）→ decode 池以 EP320 执行 MoE（token 经 FusedDispatch 直写专家所在芯粒 UBuffer，INT8 消息 7.5 KB/token）→ FusedCombine 汇聚 → 输出 [Paper: PDF p. 19–23, Fig. 9–12]。
- **假设**：负载可被池化资源独立伸缩吸收；专家负载可均衡（EPLB）；量化误差可被五步方案控住；UB 带宽足以支撑非局部性 KV 访问 [Paper: PDF p. 19–37]。
- **训练需求**：无（推理服务系统；量化缩放因子离线搜索 [Paper: PDF p. 37, Eq. 3]）。

## 08 核心模块拆解

| 模块 | 功能 | 为何需要 | 输入 → 输出 | 支持证据 | 移除/退化的影响 |
|---|---|---|---|---|---|
| UB 两级交换 | 任意芯粒对等互连，L2 无收敛 | 消除带宽断崖（§05 痛点 1） | 芯粒间消息 → 两跳直达 | [Paper: PDF p. 13, Fig. 5]；Combine 131 vs 46 GB/s@EP8 [Paper: PDF p. 47, Table 6] | 退化为层次式：调度须重新引入局部性（预期） |
| PDC 分离架构 | prefill/decode/缓存三池独立伸缩 | 免除缓存亲和调度，提高利用率 | 请求流 → 三池任务分布 | [Paper: PDF p. 19, Fig. 9]（设计）；**无同硬件对照消融** | 需回到 KVCache 中心化调度（预期，未实测） |
| FusedDispatch/FusedCombine + AIV 直连 | 以点对点直写替代 3 次 all-to-all，消息先行 INT8（7.5 KB/token） | 消除动态形状与同步开销 | token → 直写专家 UBuffer | 微基准 [Paper: PDF p. 47, Table 6]；预分配缓冲 Eq.1–2 [Paper: PDF p. 22] | 回退 all-to-all：时延↑（论文口径，未给同栈对照数） |
| EP320 部署 | 每芯粒恰一个专家 | 最小化 expert 间干扰、解码时延 | 256 路由专家+冗余 → 320 槽位 | 设计论证 [Paper: PDF p. 20]；端到端 decode 结果 [Paper: PDF p. 41, Table 3–4] | 更小 EP：时延↑（预期） |
| 微批次解码流水线 | 注意力流与 MoE 流按微批重叠 | 隐藏剩余通信/访存时延 | 解码迭代 → 双流重叠 | **隔离消融** [Paper: PDF p. 43, Fig. 20a]：+5.8/9.4/6.9%（batch 64/96/128）；逐层时延 −10% [Paper: PDF p. 44] | 无此优化吞吐下降上述幅度（实测） |
| MTP 支持 | 单投机 token（接受率≈70%）流水化 | DeepSeek-R1 原生多 token 预测 | draft token → 并行验证 | **隔离消融** [Paper: PDF p. 45, Fig. 22a]：+6%~49%（batch 越小越显著） | 无 MTP 吞吐下降（实测） |
| EMS 弹性内存服务 | 模型块/上下文 KV 池化缓存 | 免除全量副本囤积与冷启动争用 | 模型/KV → 内存池键值块 | **消融** [Paper: PDF p. 37, Table 1]：2,560s→320s；切换 ~5s vs 281s；[Paper: PDF p. 46, Fig. 23]：90% 复用 prefill 2.28×、TTFT −59% | 冷启动回到 2,560s（实测对照） |
| INT8 五步量化 | 权重/激活 INT8 化 | 吃满整数算力、压消息体积 | FP 模型 → INT8 部署 | 精度 [Paper: PDF p. 42, Table 5]（16 基准）；算子利用率 [Paper: PDF p. 47–49, Table 7–9] | 回 BF16：算力减半量级（预期） |

## 09 关键公式与符号

| 公式 | 含义与符号 | 作用/直觉 | 来源 |
|---|---|---|---|
| `buffer_size = rank_num × max_tokens × msg_size` (Eq. 1) | rank_num=通信域 rank 数（320）；msg_size=量化后单 token 消息长（7.5 KB） | 预分配直写缓冲，消除动态分配/同步 | [Paper: PDF p. 22, Eq. 1] |
| `max_tokens = local_batch × min(topK, experts_per_die)` (Eq. 2) | local_batch≤96；topK=8；experts_per_die=1 | 最坏情况下单对端 token 数上界 | [Paper: PDF p. 22, Eq. 2] |
| `s* = argmin_s L(s), L(s)=‖Q(W·s)(s⁻¹·X) − WX‖` (Eq. 3) | W 权重、X 激活、Q(·) 量化函数、s 缩放因子 | 离线搜索最优缩放，使量化前后输出对齐 | [Paper: PDF p. 37, Eq. 3] |
| `argmin_α ‖Block(X;W) − Block(X;Q(W;α))‖` (Eq. 4) | α 块级裁剪因子 | 逐块求解裁剪范围，控长尾离群 | [Paper: PDF p. 38, Eq. 4] |

## 10 实验设计与证据链

**评测设置** [Paper: PDF p. 39, §5.1]：模型 DeepSeek-R1（671B，INT8）；负载生成器按 4K prompt / 4K KV 缓存配置；对比对象为**已发表数字**（SGLang@H100、DeepSeek Blog/Profile@H800），非同环境复跑；CM384 侧 batch 96 vs 对比系统 128。

**证据清单**：Fig.1–24、Table 1–10、Eq.1–4 全部在册（裁片与双语定位见 nature-reader `source_map.json` C001–C034/F001–F024/T001–T010/E001–E004）；主证据：Table 2/3/4（整体性能）、Table 5（精度）、Table 6（通信算子）、Table 7–9（算子利用率）、Fig. 20–23（消融）、Table 1（模型加载）、Fig. 24 + Table 10（更大规模外推）。

| 实验 | 验证主张 | 对比与条件 | 结果 | 支持的结论 | 不支持的更强结论 | 来源 |
|---|---|---|---|---|---|---|
| E1 整体 prefill | CM384 服务效率超过 H100/H800 已发表值 | CM384(默认/Perfect EPLB) vs SGLang@H100、DeepSeek@H800（文献值） | 5,655 默认(3.76) / 6,688 Perfect(4.45) vs 3.75/3.96 tok/s/TFLOPS | 同口径效率指标上更高 | CM384 绝对吞吐/时延全面占优（绝对值低于 batch128 的两个系统） | [Paper: PDF p. 40, Table 2; S206] |
| E2 整体 decode | 同上（decode） | batch 96 vs 对比系统 128 | 1,943 tok/s/NPU，TPOT 49.4 ms；效率 1.29 最高（vs 1.10/1.17/0.93） | 每 TFLOPS 利用率更高；sub-15ms SLO 下仍 538 | 吞吐绝对值占优（1,943 < 2,172/2,325，但批更小） | [Paper: PDF p. 41, Table 3–4; S208] |
| E3 通信算子微基准 | UB 融合算子优于 RDMA all-to-all | CANN EP vs DeepEP@H800，EP8–320 | Combine：118 vs 318 µs@EP8，131 vs 46 GB/s；Dispatch 大 EP 度带宽退化 | 点对点语义在小-中 EP 度显著占优；Combine 全域占优 | 全 EP 域全指标占优（Dispatch 大 EP 带宽退化，作者自认） | [Paper: PDF p. 47, Table 6] |
| E4 微批次消融 | 流水线隐藏时延有效 | 开/关微批次，batch 64/96/128 | decode +5.8/9.4/6.9%；逐层时延 −10% | 该优化在 CM384 上有效但上限低于 H100 集群（SGLang 称 35%），作者归因 UB 通信停顿本就更低 | UB 互连优越性的因果证明（为反向解释，无独立操纵实验） | [Paper: PDF p. 43–44, Fig. 20–21] |
| E5 MTP 消融 | MTP 提升解码吞吐 | 开/关 MTP，单投机 token | +6%~49%，小 batch 更显著（接受率≈70%） | MTP 支持有效且与 batch 负相关 | 接受率与负载偏斜的因果关系（未测） | [Paper: PDF p. 45, Fig. 22] |
| E6 模型加载消融 | EMS 降低冷启动/切换 | 无缓存/本地 DRAM/EMS，8×671B INT8 | 2,560s→320s；切换 281s（12.5% 命中）→~5s；1× 副本 | 池化共享加载显著优于独立缓存 | 大规模多模型场景等比例外推 | [Paper: PDF p. 37, Table 1] |
| E7 上下文缓存消融 | 复用率→吞吐/TTFT | EMS@UB vs @VPC vs 无缓存，复用率 12.5–90% | 50%：1.42×、TTFT −34%；90%：2.28×、−59%；UB 一致优于 VPC | 高复用+高带宽平面收益显著 | 对真实生产流量分布的直接外推（合成复用率） | [Paper: PDF p. 46, Fig. 23] |
| E8 精度验证 | INT8 不伤精度 | 16 基准 vs 官方 API vs 论文报告值 | MMLU 90.82 vs 91.05 等，整体持平 | 该模型该方案精度可接受 | 所有模型/所有任务通用（单模型族） | [Paper: PDF p. 42, Table 5] |
| E9 算子利用率 | INT8/MLA 内核吃满硬件 | FlashMLA@H800 vs CANN MLA；INT8 GEMM | MLA 65.4% vs 66.7%；GEMM 77.4–82.7% | 内核实现质量相当、计算受限 | 端到端差距全由互连解释 | [Paper: PDF p. 47–49, Table 7–9] |
| E10 规模外推（§6 前瞻） | 更大规模超节点缓解分配碎片 | 384/768/1536/3072 NPU 分配率、交换机利用率 | 规模↑分配率↑；384 时交换机利用率 100% | 紧耦合块随规模扩大更易 placement | 已实现/已部署（属设计推演，非实测部署） | [Paper: PDF p. 50–51, Fig. 24; Table 10] |

## 11 结论的正确解读

- **任务范围**：结论限定于 DeepSeek-V3/R1 一族 MoE 模型的推理服务 [Paper: PDF p. 39, §5.1]；未测 dense 模型、其他 MoE 结构、训练负载。
- **对比性质**：核心优势声明基于**每 TFLOPS 归一化的效率指标**与**文献已发表数字**，不是同硬件同环境的受控复跑；批大小不对等（96 vs 128）[Paper: PDF p. 41, S208]。
- **效率指标的口径效应** [Analysis]：tokens/s/TFLOPS 天然有利于低峰值算力芯片；CM384 芯粒 FP16 算力低于 H100/H800，效率优势与绝对吞吐劣势并存，两者不矛盾且都真实。
- **端到端 vs 组件**：E4–E7 是合格的组件级消融；E1–E2 是端到端结果；但**架构级主张（PDC 对 vs KVCache 中心化）没有受控对照实验**，靠设计论证 + 组件证据间接支撑。
- **成本维度缺失**：全文无功耗、价格、TCO 数据；"384 NPU 规模"的服务成本语境未给出。
- **可复现性**：未声明开源代码/配置；CM384 为华为云专有硬件，外部复现受限。
- **有界重述**：论文证明了——在 CM384 上，用 PDC+EP320+融合算子+微批次/MTP+EMS+INT8 这套栈服务 DeepSeek-R1，可以达到 prefill 4.45 / decode 1.29 tokens/s/TFLOPS、TPOT 49.4 ms（batch 96），且各组件的隔离消融方向与设计预期一致；它没有证明——该优势在绝对吞吐、成本、通用模型覆盖上同样成立，也没有用受控实验证明对等架构优于 KVCache 中心化架构。

## 12 作者明确承认的局限

| 局限 | 具体表现 | 作者提出的未来方向 | 来源 |
|---|---|---|---|
| EPLB 未达理想 | 默认 3.76 vs Perfect EPLB 4.45 tok/s/TFLOPS 的差距 | 改进负载均衡算法 | [Paper: PDF p. 40, S206] |
| 大 EP 度 Dispatch 带宽退化 | CANN EP 有效带宽在大 EP 度显著下降 | 明示为"future optimization 方向" | [Paper: PDF p. 47, §5.5.1] |
| 微批次收益上限受限 | CM384 上 +6.9~9.4%，低于 H100 集群 35%（作者归因 UB 停顿更低） | —（解释性说明） | [Paper: PDF p. 43, §5.4.1] |

**Related constraints noted by the authors**（作者以后续方向形式给出的未竟事项，非正式局限表述）：VPC 与 RDMA 平面尚未统一 [Paper: PDF p. 49, §6.1.1]；希望扩展更大规模超节点 [Paper: PDF p. 49–51, §6.1.2]；CPU 物理分离池化 [Paper: PDF p. 51, §6.1.3]；组件级分离与混合自适应部署 [Paper: PDF p. 52, §6.2]。

## 13 批判性分析

| `[Analysis]` 观察 | 潜在问题/替代解释 | 为何重要 | 如何检验 | 依据 |
|---|---|---|---|---|
| 效率对比基于文献值而非复跑 | 对比系统数字来自 Blog/Profile，硬件调优、kernel 版本、评测脚本不可对齐 | 主张"超过 H100/H800"的可靠性依赖对方数字的口径 | 同栈复现 SGLang@H100（batch 96、同 SLO）并按论文口径重测 | [Paper: PDF p. 40–41, Table 2–4] |
| PDC 架构无受控对照 | "对等优于 KVCache 中心化"可能部分来自实现质量差异而非架构 | 架构主张是论文第一创新点 | 在 CM384 上实现缓存亲和路由变体，与默认 PDC 对比调度开销/均衡度/命中 | [Paper: PDF p. 19, Fig. 9; §4.1] |
| tokens/s/TFLOPS 指标选择 | 归一化口径天然利于低算力芯片；未同时给 perf/瓦特或成本效率 | 影响跨硬件采购/选型解读 | 补充 tokens/s/瓦特、tokens/s/元 口径重述同一数据 | [Paper: PDF p. 39–41, §5.2] |
| 微批次收益小被解释为"UB 更好" | 存在替代解释：实现未达最优、重叠策略次优 | 该解释被用于反向论证互连优越性 | 通信-计算 timeline 剖析，量化剩余可隐藏停顿 | [Paper: PDF p. 43, §5.4.1] |
| 合成复用率外推 | Fig.23 的复用率梯度为受控合成，非生产流量 | 生产收益可能低于 2.28× | 用真实多轮会话 trace 回放测 TTFT 分布 | [Paper: PDF p. 46, Fig. 23] |
| 单模型族验证 | 量化方案与 EP320 部署强绑定 DeepSeek 结构 | 泛化性未知 | 换 1–2 个不同粒度 MoE（如 Qwen-MoE、Mixtral）复测精度与吞吐 | [Paper: PDF p. 42, Table 5] |

## 14 收获知识

**Agent-derived knowledge candidates**：

1. **互连质量 ⇄ 调度自由度的替换律** [Analysis]：互连每提升一档，就有一层为规避远程访问而设的调度复杂度可以被删除（本例：KV 亲和调度）；反之互连不足时复杂度只是转移到软件层。可迁移到任何资源池化系统设计。
2. **点对点直写替代集合通信**：把 all-to-all 拆成预分配缓冲上的单边直写（Eq.1–2 定容量、双缓冲防竞态、地址计算与传输流水化），是一套可移植的 MoE 通信模式 [Paper: PDF p. 22–23]。
3. **"消息先行量化"**：在 token 进入网络前完成 INT8 量化（7.5 KB/token），把量化从计算优化升维成通信优化 [Paper: PDF p. 22]。
4. **消融结果的互连反证读法**：某优化（微批次）在新平台收益变小，可以是互连更好的旁证（可隐藏开销更少）——消融差异本身携带平台信息 [Paper: PDF p. 43]。
5. **效率 vs 吞吐的双指标报告法**：tokens/s/TFLOPS（硬件效率）与 tokens/s/NPU（绝对性能）必须成对报告，否则跨硬件对比产生系统性误读 [Paper: PDF p. 40–41]。

## 15 与已有知识的联系

- **[User]** 与本课题"多节点设备管理统一性"直接对表：CM384 的 UB 统一内存语义 + 全对等拓扑，是"软件视角把 768 个芯粒当单一节点调度"的生产级实现样本；其 §6.1–6.2 演进方向（更大规模、CPU 池化、组件级分离）与本课题关注的统一性边界推进节奏直接相关（repo 课题背景，research/CLAUDE.md）。
- `[Paper-framed; external verification not performed]` 论文自述的谱系：KVCache 中心化（Dynamo、Mooncake）→ 对等架构；RDMA all-to-all（DeepEP）→ 融合直写算子；SGLang 微批次 → 本栈微批次。这些对照均来自论文叙述与引文 [41][48][53][56]，本卡未逐一外部核验。
- `[Analysis]` 与公开知识的候选联系（未做 prior-art 检索）：TPOT 约束下动态调 batch 的做法与通用 SLO-aware serving 文献一致；块级量化裁剪/误差补偿思路与 GPTQ 类后训练量化家族方向相近，具体关系需查证。

## 16 研究想法

**Agent-derived research candidates**（以下均为假设/候选，未做 novelty 声明；除想法 3 可外部复现外，其余验证依赖 CM384 或同类 UB 平台访问）

> 字段本地化说明：每个想法均含「核心假设 / Delta / 初始方法 / **验证**（comparison、证伪条件）/ **可能的失败**（≥2 条）/ 创新状态」八个字段，对应 schema 的 hypothesis/delta/method/validation/failure/status；audit 的 idea_validation/idea_failure 两条 warning 系检索英文字段名所致的误报。

### 想法 1：运行时专家迁移式 EPLB（贴着 UB 带宽做负载均衡）

- **来源局限**：默认 3.76 vs Perfect EPLB 4.45 的差距是作者明认的第一改进点 [Paper: PDF p. 40, S206]。
- **核心假设** [Hypothesis]：UB 的 Combine 每 rank 131 GB/s 带宽使专家状态（权重页）跨芯粒迁移的代价足够低，运行时把最热专家迁到轻载芯粒可收复默认-理想差距的一半以上。
- **Delta**：机制——从静态/周期性 EPLB 变为基于实时专家负载的迁移式均衡。
- **初始方法**：以 token→expert 计数做滑动窗口热度估计；热度超阈专家在迭代边界迁移（UB 直写权重页 + 路由表原子切换）；与静态 EPLB、Perfect EPLB 上界对比。
- **验证**：指标 prefill tok/s/TFLOPS 与专家负载方差；对照 Table 2 口径；证伪条件——迁移流量使吞吐净收益 ≤0 或时延尾部恶化 >5%。
- **可能的失败**：突发负载下迁移风暴（抖动）；权重页迁移带宽挤占 Combine 带宽；热度估计滞后于负载变化。
- **创新状态**：`partially checked`（DeepSeek 官方 EPLB 已存在静态/启发式均衡；运行时迁移式在 UB 平面上的可行性未检索到先例，prior-art search required）。

### 想法 2：大 EP 度 Dispatch 带宽恢复的两级树式分发

- **来源局限**：作者明认 CANN EP 在大 EP 度下 Dispatch 有效带宽显著退化，留作 future work [Paper: PDF p. 47, §5.5.1]。
- **核心假设** [Hypothesis]：把扁平 Dispatch 改为 L1（机柜内）聚合 + L2（跨子平面）树式两级分发，可在 EP320 保持近 flat 的每 rank 带宽。
- **Delta**：机制——通信拓扑结构改变（树式分层 vs 全扁平直写）。
- **初始方法**：按目的专家的子平面分组聚合消息（降低 L2 消息数），L1 内 AIV 直写、L2 间 SDMA 树广播；微基准测 EP8–320 时延/带宽曲线。
- **验证**：对比 Table 6 口径的 flat Dispatch；证伪条件——EP≥256 时每 rank 带宽仍低于 flat 方案或时延超线性增长。
- **可能的失败**：两级聚合引入额外拷贝时延，小 batch 下反而更慢；L2 聚合点成为新热点；与 FusedCombine 共享缓冲的兼容性。
- **创新状态**：`unverified`（hierarchical all-to-all 在 GPU 互连文献中方向存在，UB/AIV 语境未检索，prior-art search required）。

### 想法 3：跨硬件效率归一化审计（可外部复现）

- **来源局限**：E1/E2 的对比基于文献值、批大小不对等（96 vs 128）、指标为 tokens/s/TFLOPS [Paper: PDF p. 40–41]。
- **核心假设** [Hypothesis]：论文报告的效率优势中，存在可量化的指标口径成分；在 batch=96、同 TPOT SLO 对齐后，SGLang@H100 的 per-TFLOPS 效率将显著高于 Table 2 中的 3.75。
- **Delta**：评测方法学——补一组受控对照。
- **初始方法**：在 H100 集群以 batch 96 / TPOT≤50ms 约束复跑 SGLang+DeepEP 的 prefill/decode，按论文公式换算效率；对 CM384 侧引用其公开数字做同口径对齐表。
- **验证**：输出对齐后的三方对比表；证伪条件——batch/SLO 对齐后 CM384 效率优势扩大（则原结论更稳）。
- **可能的失败**：无 CM384 访问权限，只能单侧复现；SGLang 版本演进使"已发表数字"不可复现；供应商 kernel 差异无法对齐。
- **创新状态**：`unverified`；本想法即一次可执行的 prior-art 级核验，成本低（单侧 GPU 实验）。

### 想法 4：CM384 上的 KVCache 中心化对照基线（架构级消融）

- **来源局限**：PDC 对等架构 vs KVCache 中心化缺少同硬件受控对照 [Paper: PDF p. 19, §4.1；第 13 节观察 2]。
- **核心假设** [Hypothesis]：在 UB 带宽下，缓存亲和路由带来的调度约束收益（若有）不足以抵偿其复杂度成本——即论文架构主张可被正面检验。
- **Delta**：评测——为 CloudMatrix-Infer 增设 locality-aware 路由变体作为消融臂。
- **初始方法**：实现按 KV 所在节点亲和的路由策略，固定其余组件，比较调度开销、负载方差、缓存命中与端到端 TPOT/吞吐。
- **验证**：证伪条件——亲和路由在动态负载下显著提升吞吐或降低 TPOT（说明局部性在 CM384 上仍有价值，PDC 的"免除局部性"收益被高估）。
- **可能的失败**：需要华为内部平台访问（外部不可复现）；两臂差异被 EPLB 效应混杂；亲和路由实现质量影响公平性。
- **创新状态**：`unverified`。

### 想法 5：MTP 接受率 × 专家负载偏斜的联合调度

- **来源局限**：MTP 增益 6%–49% 强烈依赖 batch，机理归因于固定开销摊销 [Paper: PDF p. 45, §5.4.2]；但专家偏斜会改变逐 token 时延与投机接受路径。
- **核心假设** [Hypothesis]：MTP 接受率与专家负载偏斜负相关；把接受率信号反馈给 EPLB（接受率低的请求迁移到轻载专家域）可获得超过各自独立优化的联合收益。
- **Delta**：反馈回路——接受率作为调度/EPLB 的输入信号（论文中两者独立）。
- **初始方法**：在模拟器或小规模 Ascend/GPU EP 环境注入可控偏斜，测接受率-偏斜曲线；再用接受率加权的热度做 EPLB 决策。
- **验证**：联合策略 vs 独立 MTP vs 独立 EPLB 的吞吐/TPOT；证伪条件——接受率与偏斜无显著相关（相关系数≈0）。
- **可能的失败**：接受率主要由内容决定而非负载；反馈回路时滞导致振荡；跨平台可迁移性差。
- **创新状态**：`unverified`。
