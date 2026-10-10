# CloudMatrix384 论文翻译规范（所有分块翻译共用）

## 任务格式
- 输入文件每行：`ID\t类型\t英文原文`（tab 分隔）。
- 输出文件每行：`ID\t中文译文`（tab 分隔），**行数与顺序与输入完全一致**，不增删行、不改 ID。
- 类型为 heading 的行：保留编号，标题译为中文，如 `4.2 Tightly-Coupled Decode ...` → `4.2 紧耦合解码与大规模专家并行`。

## 硬性规则
1. 保留 `$...$` 数学表达式原样（不翻译变量）、`**粗体**` 标记、引用编号 `[56]`、章节引用 `§4.2.1`、图表引用 `Fig. 10`/`Table 2`。
2. 数字、单位、百分比、吞吐量**精确保留**：`6,688 tokens/s`、`<50 ms`、`4.45 tokens/s/TFLOPS`、`EP320`、`2.5GB/s`。
3. 人名、Benchmark 名（MMLU/GSM8K 等）、型号（H800/H100/B200/NVL72/DeepSeek-R1/DeepSeek V3）不译。
4. 列表项编号 `(1)(2)(3)` 保留；段落不合并、不拆分、不省略，内容完整翻译。
5. 意译优先于直译，但技术细节（内存大小、时延数值、拓扑结构描述）必须逐项落实，不得泛化。
6. 英文长句可按中文习惯断句，但不得改变逻辑顺序与因果。

## 术语表（锁定，全文统一）
| 英文 | 译法 | 备注 |
|---|---|---|
| CloudMatrix / CloudMatrix384 / CloudMatrix-Infer | 不译 | 系统名，可用缩写 CM384 |
| Unified Bus (UB) | 统一总线（UB，灵衢） | 首次出现后一律用 UB |
| UB plane | UB 平面 | |
| supernode | 超节点 | |
| Ascend 910 | 昇腾 910（Ascend 910） | 首次后用 Ascend 910；die 译"芯粒" |
| Kunpeng | 鲲鹏（Kunpeng） | |
| prefill | prefill（预填充） | 首次标注后保留 prefill |
| decode | 解码 | |
| PDC disaggregation | prefill-解码-缓存分离（PDC 分离） | |
| disaggregation / disaggregated | 分离式 | 如 disaggregated memory pool→分离式内存池 |
| pooling | 池化 | |
| MoE | MoE（混合专家） | |
| expert parallelism (EP) | 专家并行（EP） | large-scale→大规模专家并行（LEP） |
| KV cache | KV 缓存 | |
| MLA | 多头潜在注意力（MLA） | |
| MTP | 多 token 预测（MTP） | |
| TPOT | 每 token 输出时间（TPOT） | |
| TTFT | 首 token 时间（TTFT） | |
| SLO | 服务级目标（SLO） | |
| microbatch | 微批次 | |
| INT8 quantization | INT8 量化 | BF16/FP16/FP32 不译 |
| SDMA | SDMA（系统 DMA） | |
| AIV-direct communication | AIV 直连通信 | |
| UBuffer | 不译 | |
| FusedDispatch / FusedCombine | 不译 | 首次可括注"融合分发/融合合并" |
| token dispatch / combine | token 分发 / token 合并 | |
| EMS (elastic memory service) | 弹性内存服务（EMS） | |
| Context Caching | 上下文缓存 | |
| Model Caching | 模型缓存 | |
| CANN / HCCL / RDMA / VPC | 不译 | VPC plane→VPC 平面 |
| scale-up | scale-up（纵向扩展） | 首次标注后用 scale-up |
| peer-to-peer | 对等 | |
| all-to-all | all-to-all 通信 | 不译 |
| GEMM | GEMM（通用矩阵乘） | |
| operator | 算子 | |
| TP / DP / SP | 张量并行（TP）/ 数据并行（DP）/ 序列并行（SP） | 首次标注后用缩写 |
| throughput | 吞吐量 | per NPU→每 NPU |
| die | 芯粒 | dual-die→双芯粒 |
| serving | 推理服务 / 服务 | LLM serving→LLM 推理服务 |
| observation/OBS | 对象存储（OBS） | |

## 输出质量基准
- 读起来像熟练系统方向研究者写的中文技术报告，不是机器翻译。
- 同一术语全文只用一种译法。
- 不确定的缩写保留英文原文，不要猜。
