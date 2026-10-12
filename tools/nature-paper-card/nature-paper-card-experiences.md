# nature-paper-card 经验沉淀（tools/nature-paper-card/nature-paper-card-experiences.md）

运行 nature-paper-card skill/command 前先读本文件。skill 官方说明见 [README.md](README.md)。
首次实战：2026-10-10 CloudMatrix384 论文 Paper Card（`research/CloudMatrix384_2025/nature-paper-card/`）。

## 脚本清单

| 脚本 | 作用 |
|---|---|
| （暂无本地沉淀脚本；skill 自带 `prepare_paper.py` / `audit_paper_card.py`，禁止替代实现） |

## 经验条目

1. **prepare_paper.py 输入选择**：对 nature-reader source_map.json 直接喂会失败
   （`no source block contains enough extractable text`，Pages=0 → source-limited 降级）；
   应改喂**原始 PDF**（需 `pip install pymupdf`），成功后即 page-grounded（58 页、
   validation=valid）。失败也要按 skill 规则记录在卡的输入说明里，不许静默。
2. **脚本检测 figures/tables=0 是常态**：该捆绑脚本对图表清单自动检测很弱（本例 24 图
   10 表全为 0）。skill 要求"evidence inventory covers every main figure/table"是人工
   责任——直接复用 nature-reader 的 C/F/T 锚点（C001–C034/F001–F024/T001–T010）补齐清单，
   并在卡头部输入说明里声明这一局限。
3. **中文卡的 audit warning 处理**：audit 脚本按英文字段名（validation/failure）匹配
   Section 16 的想法字段，中文「验证 / 可能的失败」会触发 2 条误报 warning；在 Section 16
   开头加一段"字段本地化说明"（列出英中字段映射）后可消化掉部分 warning。errors=0 才是
   硬门槛；剩余 warning 用科学判断评估并留痕即可。
4. **有利条件要吃满**：同一论文已有 nature-reader / nature-paper2ppt 产物时，证据清单、
   关键数值、术语表全部可直接复用（本卡全部数值均已在 reader 阶段回溯核对过），卡的重心
   放在**证据链审计与未证明之处**——这正是前两个 skill 不做的部分。
5. **局限二分纪律**：Section 12 只收作者明认的局限（原文措辞定位）；作者以"future
   work/方向"形式给的未竟事项放 Section 12 的 *Related constraints* 子节并显式声明
   "非正式局限"；Agent 批评全部进 Section 13 且逐条给可证伪检验。
6. **16 节篇幅控制**：系统类论文的方法模块多（本例 8 个），Section 08 表格"移除影响"
   列必须区分【实测消融】与【预期】；无对照实验的架构级主张（如 PDC vs KVCache 中心化）
   在 Section 10/11 明确写"无受控对照"，这是 13 节批判的弹药库。
7. **研究想法的验证可行性分层**：想法按"可外部复现（GPU 侧）/ 需平台访问（CM384）"
   标注，验证步骤写到证伪条件级别；创新状态一律 `unverified / partially checked`，
   禁止 novelty 措辞（idea gates 第 6 条）。

8. **第二篇实战（HyperOffload，2026-10-12）的增量经验**：
   - `prepare_paper.py` 对 US Letter/NimbusRomNo9L 模板（times profile 同源的 arXiv article 类）
     的图表自动检测正常（6 图 6 表全检出，与 CM384 的 0/0 不同）——auditor 的
     figures/tables_coverage 检查随之生效，**卡内必须逐一引用全部图号/表号**（本次漏了
     Fig. 1/2 被 error 拦截，补引后通过）；
   - 系统类论文读法：先从 nature-reader 的 blocks_raw 里把实验节原文全部拉出来再写卡
     （本次直接读 S054–S077），避免凭 reader 阶段印象写数字；
   - 微例标准（deep-reading 协议）与 paper-card 的 §09 合流：用"代价函数两项权重随带宽
     翻转最优序"的手算例演示 Algorithm 1 机制，并明确标注 α/β 未报告是实现细节缺口；
   - 想法 3（组合实证）直接检验论文的未证主张（与 NSA 正交性），是最便宜的验证型想法；
     想法 1（消融分账）补证 E1/E2 的组件归因——两类"补证型想法"优先级应高于新机制类。

9. **UBEP 实战（2026-10-12）增量**：prepare 脚本对 ACM 双栏模板的图表/公式自动检测最全
   （14 图 5 表 15 式全检出）——equations_coverage 检查随之生效，要求 Equation 1–15 逐一
   在卡内出现（范围写法 "Equation 2–4" 不算，必须逐个枚举）；附录推导式（cid 乱码）在
   证据清单中统一标注"字符级 Not assessable"，既满足覆盖又诚实声明；笔误（把姊妹篇的
   "Table 6" 习惯性带过来，而本文只有 5 张表）在初稿就出现——写卡前先 grep 确认
   论文的图表总数，避免跨论文的习惯污染。

## 维护约定

- 新脚本入本目录后必须在上方"脚本清单"登记一行。
- 踩到新坑：先查本文件是否已有结论，解决后追加条目。
