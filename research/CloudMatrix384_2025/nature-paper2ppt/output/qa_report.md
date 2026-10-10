# QA 报告 — CloudMatrix384 组会 PPT

- 产物：`output/final_presentation_cn.pptx`（12 页，16:9，中文，含演讲者备注）
- 生成：python-pptx 1.0.2，`build_pptx.py`（本目录）
- 日期：2026-10-10

## 一、创建状态

| 项 | 结果 |
|---|---|
| 幻灯片数 | 12（要求 12 ✓） |
| 嵌入图片 | 6（fig01/02/05/09/10/19） |
| 演讲者备注 | 12/12 页 |
| 形状越界 | 0（重开后程序化校验） |
| 纸面类型 | methods（problem-to-solution 弧线） |

叙事结构：标题 → 背景压力 → 问题定位（层次式互连瓶颈）→ 超节点架构 → UB 平面 → PDC 分离 → EP320/融合算子 → 微批次+MTP → EMS 缓存 → 整体性能对比 → INT8 精度 → 总结与课题启示。

## 二、自审缺陷与修复（severity 分级）

| 级别 | 位置 | 缺陷 | 处置 |
|---|---|---|---|
| high | S3 | 图注 y 坐标单位混用（EMU 被当英寸数叠加），文本框越界 | 改为固定英寸坐标，重生成 |
| high | S4 | 全宽图 12.1in 高度 5.2in，正文条溢出页面底部 | 图缩至 10.4in 宽并居中，正文上收 |
| high（内容） | S4 备注 | 写入论文未提及的"16 个机柜"（16 实为每个子平面的 L2 交换芯片数） | 删除该说法；正确的交换机规格（7 子平面 × 16 芯片 × 48 端口、L2 无收敛）补入 S5 图注行 |
| medium | S9 | 右栏文本 164 字符判密 | 精简第 4 条为短句 |
| low ×12 | S5/S8/S10 等 | near-miss 对齐提示（2-7pt） | 多为 metric 组内"数字-标签"的设计性偏移，接受；组间主对齐线（标题下缘、图缘、来源条基线）一致 |

`audit_pptx_quality.py` 结果：修订前 high=2 / medium=1 → **修订后 high=0 / medium=0**（`output/pptx_audit.md`）。

## 三、图表资产 QA

- 6 张图全部复用 `../nature-reader/assets/` 的已核验裁片（视觉模型逐张确认过完整性），未重新提取；裁片保留轴/图例/子图标号。
- 图页均带来源标签（`Source: Fig. N, arXiv:2506.12708v3`）。
- 对比表（S10）用 PPT 原生表格重排自 Table 2/3/4 与 §5.2 文字，数值逐一与 paper.md 核对；decode 批大小差异（128 vs 96）在来源行注明。

## 四、数值溯源抽查（全部来自 nature-reader/paper.md）

6,688/1,943 tokens/s/NPU、4.45/1.29 tok/s/TFLOPS、538@sub-15ms、131 vs 46 GB/s（EP8 Combine）、149 vs 360 µs（EP256）、2,560s→320s、281s/12.5%、2.28×/−59%、MMLU 90.82 vs 91.05、65.4%/66.7%、77.4–82.7%、+5.8/9.4/6.9%、+6~49%（MTP）、−10% 逐层时延——均与原文一致，无编造数值。

## 五、验证方法与局限

- 重开 PPTX 校验：12 页 / 6 图 / 12 备注 / 0 越界 ✓
- `audit_pptx_quality.py` 无未解决 high 项 ✓
- **渲染预览不可用**（环境无 LibreOffice/soffice）：按 skill 政策以 XML 审计 + 对象级边界检查 + 资产 contact sheet（nature-reader 阶段已做）替代；建议用户在 PowerPoint/WPS 中快速翻检一遍字号观感。
- 字体使用 Microsoft YaHei（中文）+ Arial（数字/英文），Office 常见字体；Linux 环境未安装 YaHei，若在本机渲染预览会回退字体，不影响交付文件本身。

## 六、遗留事项

- 无 high/medium 遗留。low 级 near-miss 提示 12 条已评估为设计性偏移。
- 如需调整页数/详略或替换图表，改 `build_pptx.py` 后重跑即可（构建产物与脚本同目录）。
