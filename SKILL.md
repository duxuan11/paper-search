---
name: paper-search
description: |
  面向生物医学工程的学术论文搜索 Skill。PubMed (NCBI E-utilities) 为默认检索平台，辅以 Europe PMC、bioRxiv/medRxiv、ClinicalTrials.gov、Semantic Scholar、Crossref、Unpaywall。覆盖文献检索、引用分析、MeSH 受控词表扩展、开放获取 PDF 判定与结构化元数据提取。Use when the user asks to search/find biomedical engineering papers, do literature review/survey/systematic review/PRISMA work, get citation counts, export BibTeX/RIS-style references, find papers by author, inspect PDF/open-access availability, or work with PubMed, Europe PMC, bioRxiv, medRxiv, ClinicalTrials.gov, Semantic Scholar, Crossref, Unpaywall, OpenAlex, arXiv, Google Scholar, IEEE Xplore, ScienceDirect, Wiley, Springer, ACS, CNKI, MeSH.
metadata:
  version: "2.1.0"
---

# paper-search Skill

## 前置检查

在开始前，检查环境就绪状态：

```bash
# 获取 skill 目录（自动检测，兼容 Claude Code/Hermes Agent 环境）
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)/.."
bash "$SKILL_DIR/scripts/check-deps.sh"
```

- **Node.js 22+**：必需（用于 CDP 浏览器模式）。仅使用 API 平台时可不检查。
- **Chrome remote-debugging**：仅在访问 Google Scholar 或其他需要浏览器自动化的平台时必需。在 Chrome 地址栏打开 `chrome://inspect/#remote-debugging`，勾选 **Allow remote debugging for this browser instance**。
- **curl**：必需，用于 API 调用。

PubMed、Semantic Scholar、arXiv 等 API 平台无需 Chrome 远程调试即可使用。

**S2 API Key（强烈建议）**：无 Key 时 S2 速率上限极低，单 session 多次调用必触发 429。免费注册即可获得更高配额：https://www.semanticscholar.org/product/api#api-key-form。有 Key 时在请求头加 `x-api-key: {your_key}`。

**API Key 自动检测**：执行 PubMed 或 Semantic Scholar 调用前，先检查对应 .env 中的 key：

| 平台 | 环境变量 | .env 位置 | 说明 |
|------|---------|-----------|------|
| PubMed | `NCBI_API_KEY` 或 `EUTILS_API_KEY` | `~/.pubmed/.env` | Hermes pubmed skill 自动解析；有 Key 速率 10 req/s，无 Key 3 req/s |
| Semantic Scholar | `S2_API_KEY` | profile `.env`（如 `~/.hermes/profiles/research/.env`） | 写入 `S2_API_KEY=your_key`；有 Key 速率 1 req/s，无 Key ~100 req/5min |

```
# ~/.pubmed/.env 示例
NCBI_API_KEY=your_ncbi_key_here

# ~/.hermes/profiles/research/.env 示例
S2_API_KEY=your_s2_key_here
```

若 Key 缺失，仍可正常使用（受速率限制），但在结果中备注"无 API Key，速率受限"。Key 由用户自行配置。

## 搜索哲学

**PubMed 优先，按需扩展，完成即止。**

默认从 PubMed (NCBI E-utilities) 出发检索生物医学工程文献。仅当 PubMed 无法满足需求时（如工程类 conference paper、非生命科学领域），才扩展到其他平台。PubMed 覆盖 MEDLINE/PMC，提供 MeSH 受控词表、结构化摘要和临床试验关联，是生物医学工程文献检索的黄金标准。

**① 明确检索目标，定义成功标准**：执行前先明确什么算完成了。

- 关键词搜索？精确论文？某作者的全部论文？某 venue 的论文列表？
- 生物医学工程子领域：组织工程？医学影像？生物材料？神经工程？微流控？器官芯片？医疗机器人？可穿戴设备？AI 辅助诊断？
- 是否需要 MeSH 受控词表扩展？（生物医学工程交叉性强，MeSH 可同时覆盖工程技术+临床医学两面）
- 文献类型：临床试验、系统综述、期刊论文、预印本、会议论文？
- 需要什么字段：仅标题和引用数 / 完整元数据 / PDF / BibTeX / 代码链接？
- 年份范围？返回几篇？
- **成功标准**：用户要的是摘要表（第一遍）还是完整元数据（第二遍）？数量够了吗？字段都有了吗？这是后续所有决策的锚点。

**② 选对平台**：不同需求对应不同平台（见下方矩阵）。API 平台优先，CDP 用于无 API 的平台。

**③ 提取结构化数据，先筛后深**：搜索的时间瓶颈不在"搜"，在"筛"。默认采用两遍策略：

- **第一遍（轻量扫描）**：先拉 20-30 条结果，输出轻量摘要表——标题、作者、年份、venue、引用数、是否有开放 PDF/代码。不拉完整摘要。
- **用户或任务确认核心论文**（引用数高、venue 等级高、与目标最相关的 5-10 篇）后，**第二遍**再深入拉摘要、PDF、BibTeX 等完整信息。

所有结果输出为统一 schema（见 `references/metadata-schema.md`），不要输出原始 HTML 或非结构化文本。多平台结果用 DOI/PMID 去重合并。

**④ 过程校验，用失败信号更新方向**：每一步的结果都是信息，不只是成功或失败的二元信号。

| 失败信号 | 含义 | 方向调整 |
|---------|------|---------|
| API 429 / Rate exceeded | 本次会话消耗超配额，不是暂时波动 | 等待 15s+ 或切换 CDP 模式；不要同一请求重试 |
| Jina/WebFetch 超时 | 该页面对静态抓取不友好 | 改用 curl 直接调 API 或切换 CDP |
| S2 返回结果为空 | query 措辞问题，或该平台无收录 | 换关键词组合，或换 PubMed/Europe PMC |
| 平台返回"内容不存在" | 未必真的不存在，可能是访问方式问题 | 检查 URL 参数是否完整，换平台验证 |
| S2 API 返回 404（DOI 已知有效） | 2025–2026 新论文尚未被 S2 索引 | 跳过 S2 引用数，用 Crossref 验证元数据；引用数标注"新论文，暂无 S2 数据" |
| 同一方式重试 3 次无改善 | 路径错了，不是还没找到方法 | 重新评估目标，换平台或换访问方式 |

**⑤ 完成判断**：对照①定义的成功标准确认任务完成后停止，不为"更完整"而过度操作。

## 平台选择矩阵

默认使用 PubMed，仅在以下场景扩展到其他平台。PubMed 覆盖 3,400+ 生物医学期刊，是生物医学工程文献的首选入口。

| 需求 | 首选平台 | 访问方式 | 备注 |
|------|---------|---------|------|
| **生物医学工程搜索（默认）** | **PubMed** | NCBI E-utilities API 或 Hermes pubmed skill | 🥇 完全开放，MeSH 扩展，结构化摘要 |
| **引用数、引用/被引、作者信息** | **Semantic Scholar** | REST API | 🥈 第二优先，补全引用网络和作者消歧 |
| 生物医学预印本 | **bioRxiv / medRxiv / engrXiv** | 各自 API / WebFetch | 最新成果，尚未同行评议 |
| 临床试验 | **ClinicalTrials.gov** | REST API | 注册试验、结果、干预措施 |
| PMC 全文 / 欧洲文献补全 | **Europe PMC** | REST API | 全文覆盖面更广（含资助信息） |
| 跨学科 DOI / 元数据核对 | **Crossref** | REST API | DOI、期刊、出版商、ISSN |
| 开放获取状态 / OA PDF | **Unpaywall** | REST API | gold/green/hybrid/closed OA 判定 |
| IEEE 期刊/会议论文（医工交叉） | **IEEE Xplore** | WebFetch / Jina | 医学影像、传感器、医疗机器人等 |
| 跨学科作者/机构/概念/引用 | **OpenAlex** | REST API | 跨学科补充，概念分类 |
| ML/AI 论文 + 代码（医疗 AI 方向） | **arXiv + Papers with Code** | REST API | 医学影像 AI、生物信息学 AI 等 |
| 广泛引用数 / 全平台覆盖 | **Google Scholar** | **CDP（必须）** | 无 API，反爬严重 |
| **中文文献**（期刊/学位论文） | **CNKI（知网）** | **CDP（必须）** | 机构登录后全文可得 |

**API 平台访问方式**：

- **WebSearch**：用于发现论文来源、查找 DOI/作者 ID 等信息入口
- **WebFetch / Jina**：URL 已知时从页面提取，Jina（`r.jina.ai/{url}`）节省 token，适合文章类页面
- **curl**：直接调用结构化 API，返回 JSON/XML
- **CDP**：仅 Google Scholar 必须；其他平台在 API/WebFetch 无效时作为兜底

详细 API 调用模板见 `references/api-cookbook.md`。

## 学科路由

默认按生物医学工程方向检索。若用户问题不涉及临床/生物，则按对应学科路由读取 `references/disciplines/*.md`。

| 学科 | 读取文件 | 首选方向 |
|------|----------|----------|
| **生物医学工程（默认）** | `references/disciplines/biomedical-engineering.md` | PubMed、Europe PMC、bioRxiv/medRxiv、ClinicalTrials.gov、IEEE Xplore（医工交叉） |
| 医学 / 生命科学 | `references/disciplines/biomedicine.md` | PubMed、PMC、Europe PMC、ClinicalTrials.gov |
| 计算机 / AI（医疗 AI 交叉） | `references/disciplines/computer-science.md` | arXiv、Semantic Scholar、IEEE、Papers with Code |
| 化学 / 材料（生物材料交叉） | `references/disciplines/chemistry-materials.md` | PubMed、Crossref、ACS、RSC、Springer |
| 物理 / 数学 | `references/disciplines/physics-math.md` | arXiv、NASA ADS、INSPIRE HEP |
| 经济 / 社科 | `references/disciplines/economics-social-science.md` | RePEc、NBER、SSRN |
| 人文 / 法律 | `references/disciplines/humanities-law.md` | Google Scholar、JSTOR、Project MUSE |

学科 profile 决定 query expansion、排序标准、输出字段和全文访问边界。生物医学工程特别关注：PubMed MeSH 扩展覆盖工程技术+临床医学两面，IEEE 补充医疗设备/传感器/影像工程文献。

## 核心能力

### 关键词搜索

1. **构造 PubMed 查询**：将用户自然语言输入（中英文均可）转为 PubMed/MeSH 查询语法：
   - 识别生物医学工程子领域：组织工程、医学影像、生物材料、神经工程、微流控、器官芯片、医疗机器人、可穿戴设备、AI 辅助诊断等
   - 使用 MeSH Terms 进行受控词表扩展（`"term"[MeSH]`），同时保留自由文本搜索（`"keyword"[Title/Abstract]`）
   - 交叉领域同时使用工程技术 MeSH 和临床医学 MeSH
   - 临床问题按 PICO 框架扩展：Population、Intervention、Comparator、Outcome
2. **扩展 query**：生成 2-3 个互补 PubMed query 覆盖不同命名习惯和子领域
3. **执行 PubMed 搜索**：调用 Hermes pubmed skill（`skill_view(name='pubmed')` → `python3 scripts/pubmed.py`），传入构造好的 query。**Sort 策略**：搜索时间范围限定的主题时（如"近3年"），`--sort date` 优先返回最新索引的论文但可能漏掉高引经典；`--sort relevance`（默认）配合 date 过滤词（如 `AND "last 3 years"[Date - Publication]`）更易命中高影响力的核心论文。一般原则：综述性/探索性搜索用 `relevance`；追踪最新进展用 `date`。

   **关键坑（此会话中曾触发的教训）**：不要先跑 `--sort date` 的查询发现结果不含高影响论文后再补跑 `relevance` 查询。这相当于为同一主题执行了 2–3 次冗余搜索，浪费时间和 API 配额。第一次查询就应该用 `--sort relevance` + `"last N years"[Date - Publication]` 日期过滤器。仅在用户明确要求"最近几个月的最新论文"时才切换到 `--sort date`。

   **关键坑（pubmed.py 不可用时的 fallback）**：Hermes pubmed skill 的 scripts/pubmed.py 可能未安装到本地（hermes skills install pubmed 未执行，或该脚本不在 $PATH 中）。此时不要停止——NCBI E-utilities 直接通过 curl 访问同样可用，且更灵活。推荐工作流（在 execute_code 中串联）：

   1. **esearch 获取 PMID**：curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=25&sort=relevance&term={query_encoded}&retmode=json" → 解析 JSON 得 idlist
   2. **efetch 获取完整元数据**：一次性传入全部 PMID（逗号分隔）：curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid_str}&retmode=xml" → 用 xml.etree.ElementTree 解析
   3. **XML 关键字段路径**：ArticleTitle（标题）、Author/LastName + ForeName（作者）、Journal/Title（期刊名）、Journal/JournalIssue/Volume（卷）、Issue（期）、Pagination/MedlinePgn（页码）、ArticleId[@IdType="doi"]（DOI）、AbstractText（摘要）
   4. **IF 匹配**：从 IF 速查表中按期刊名模糊匹配，未收录的标注 --
   5. 若还需引用数：curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=citationCount" 逐篇获取

   关键细节：
   - query 必须用 urllib.parse.quote(query, safe='') 编码，否则 NCBI 返回空响应
   - 一次 efetch 可传入最多 100 个 PMID，不要逐个请求
   - ncbi 无 Key 限速 3 req/s，但 esearch + 一次 efetch 只消耗 2 次请求，通常不受限
   - 首次 curl 可能略慢（DNS/SSL 协商 1-3s），加 --connect-timeout 15 --max-time 30

**关键坑（多组学查询策略：先窄后扩）**：检索跨领域主题（如器官芯片+多组学）时，初期 query **不应**直接包含 proteomics/metabolomics/transcriptomics 等个别组学术语来扩展。这会引入大量只涉及单一组学（如仅测了蛋白组）而非多组学整合理念的论文，噪声率极高。正确策略：
  1. **先窄**：只用精确多组学术语（`multi-omics`/`multiomics`/`multi-omic`）匹配 Title/Abstract
  2. **结果不足时再扩**：精确匹配结果太少（<10 篇）时，才逐步加入个别组学术语，每次加一个并评估噪声增量
  3. **输出时区分两类论文**：清晰的"多组学方法论文" vs. "在模型中用了某单一组学的论文"——用户通常想要前者，需在摘要表中分别标注
4. **Semantic Scholar 补全引用**：PubMed 拿到 PMID/DOI 列表后，用 S2 batch API 批量获取 `citationCount`、`referenceCount`、`influentialCitationCount`
5. **第一遍输出轻量摘要表**（必含：标题、年份、期刊、PMID、引用数、是否有开放 PDF），**不默认拉完整摘要**
6. **意图判断**：用户明确说"只要前 N 篇"或"摘要表即可"时，直接输出第一遍结果
7. 用户需要第二遍时，再深拉完整元数据（摘要、MeSH Terms、参考文献）
8. 若 PubMed 结果不足 → 扩展到 Europe PMC、bioRxiv、Semantic Scholar 补充

多平台并行查询时，用子 Agent 分治（见"并行分治策略"一节）。

**轻量摘要表输出格式示例**：

| 标题 | 年份 | 期刊 | PMID | 引用 | PDF |
|------|------|------|------|------|-----|
| Organ-on-a-chip: a new paradigm for drug development | 2024 | Trends Pharmacol Sci | 39123456 | 450+ | ✓ PMC |
| Microfluidic models of the blood-brain barrier | 2023 | Lab Chip [JCR Q1] | 38234567 | 320+ | ✓ PMC |
| 3D bioprinting of vascularized tissue constructs | 2025 | Adv Mater | 39345678 | 80+ [新] | ✗ |

期刊 JCR 分区来源标注：通过 Crossref/OpenAlex 补全，必须标明 `[JCR Qx]` 来源。

### 结果筛选

搜索后用以下维度缩小范围，**优先帮用户筛出值得读的论文，而不是把所有结果都呈现**：

| 筛选维度 | 数据来源 | 说明 |
|---------|---------|------|
| 研究类型 + 证据等级 | PubMed publication type + `references/rankings/biomed-evidence-ranking.md` | 系统综述 > RCT > 队列研究 > 病例报告；预印本单独标注 |
| 引用数阈值 | Semantic Scholar `citationCount` | 经典论文通常引用数高；新兴方向适当放低 |
| 发表年份 | PubMed `dp` 过滤 | 综述需要覆盖历史；最新进展限定近 2-3 年 |
| 期刊等级 | JCR 分区 / 影响因子 | 优先匹配 `references/impact-factor/impact-factor.md` 速查表；未收录则通过 Crossref/OpenAlex 补全，标注来源 |
| 开放 PDF | PubMed Central (PMC) ID 检测 + Unpaywall | PMC ID 存在 → free full text；补充 Unpaywall OA 检查 |
| 临床试验注册 | ClinicalTrials.gov NCT ID | 临床试验必需信息 |

**排序建议**：先读取 `references/disciplines/biomedical-engineering.md` 的二维排序规则。BME 论文按双维度评估：

1. **临床证据（治疗/干预类优先）**：系统综述/meta 分析 > RCT > 队列研究 > 病例报告
2. **工程验证（设备/材料类优先）**：已验证设备/系统 > 体内验证原型 > 体外验证原型 > 计算模型 > 概念论文
3. **交叉话题**：两维度同时存在时，临床证据权重更高
4. **时效性**：近 6 个月内发表的标注 `[新]` 并置顶
5. **引用数（参考项）**：同一证据等级内按引用数降序
6. **期刊等级（参考项）**：JCR Q1 期刊同引用数时优先

**实操分组示例**：
- 第一组：近 2 年系统综述和 RCT，按引用数降序
- 第二组：近 6 个月新论文（含 `[新]` 标注），按期刊等级排列
- 第三组：更早的高引论文

**筛选后的典型结论格式**：

> 共找到 28 篇，按引用数 + 研究类型筛选后，推荐优先阅读以下 6 篇：[列表]
> 其余 22 篇可按需查阅。

### 影响因子 / JCR 分区查询

用户要求标注影响因子或按 JCR 分区筛选时，加载 `references/impact-factor/impact-factor.md`。该表覆盖 5 大类 BME 核心期刊的最新 IF：

**关键坑（S2 API 429 限流 — 影响 IF-引用数工作流）**：无 S2 API Key 时，单个 session 内仅约 100 次 S2 请求配额。首次搜索 + 25 篇元数据查询 + 25 篇引用数查询，足以在 2-3 个工具调用内触发 429。之后整个 session 所有 S2 调用立即失败，直到配额在 ~5 分钟后重置。

  **应对策略**：
  1. 发现 429 后立即停止 retry，不要重试同一请求
  2. 改为**纯 IF 排序**（跳过引用数列）：NCBI efetch 拿到所有元数据后，直接用 IF 速查表按期刊名匹配 IF，按 IF 降序输出
  3. 在摘要表中引用数列标注 `[S2 429]` 说明原因，不自创引用数
  该表覆盖 **12 大类、372 篇** BME 核心及交叉领域期刊的最新 IF：

  | 类别 | 期刊数 | 范围 |
  |------|--------|------|
  | 综合顶刊与方法学 | 59 | Nature 系列、Cell、Science、Adv Mater、PNAS 等（IF 6.4–101.8） |
  | 类器官/器官芯片/生物材料 | 41 | Biomaterials, Bioactive Materials, Lab Chip, Stem Cells, Tissue Eng 等 |
  | 细胞生物学与发育生物学 | 26 | Cell Death & Diff, Autophagy, Apoptosis, Development 等 |
  | 医学影像/AI/生物信息学 | 30 | Med Image Anal, IEEE TMI, Nature Mach Intell, Radiology 等 |
  | 生物工程与应用微生物 | 25 | Trends Biotechnol, Bioresource Technol, Microb Biotechnol 等 |
  | 生化与分子生物学 | 31 | Mol Cancer, Nucleic Acids Res, Mol Cell, Redox Biol 等 |
  | 免疫学 | 33 | Immunity, Nat Rev Immunol, Front Immunol, J Immunother Cancer 等 |
  | 纳米科学与纳米医学 | 20 | ACS Nano, J Nanobiotechnol, Nanomedicine 等 |
  | 遗传学与基因组学 | 34 | Nat Rev Genet, Genome Biol, Am J Hum Genet, BMC Genomics 等 |
  | 药物学与治疗学 | 24 | Signal Transduct Target Ther, Pharmacol Rev, Gene Ther 等 |
  | 皮肤生物学与皮肤病学 | 19 | JAAD, Br J Dermatol, J Invest Dermatol, Wound Repair 等 |
  | 高频发文大刊 | 30 | Sci Rep, PLOS One, Int J Mol Sci, Cancers, Sensors 等 |

使用方式：
- 摘要表增加 `IF` 列，从速查表匹配期刊名
- 表中未收录的期刊标注 `[—]`，提示可手动查询 JCR/LetPub
- 用户要求按 IF 筛选时：Q1 优先，同分区内按 IF 降序
- 排序中 JCR 分区作为期刊等级维度的数据来源，覆盖 `references/rankings/biomed-evidence-ranking.md` 中的期刊等级项
- 数据更新于 2026-06-16（通过 iikx.com API 批量更新，覆盖 12 大类、372 篇期刊）

**IF 核实限制**：JCR 影响因子为 Clarivate 专有数据，无公开 API。网络受限（如透明代理/FlyingBird 阻断浏览器）时无法从 LetPub、JCR 等站点实时核实 IF。⚠️ **iikx.com 可作为免费程序化数据源使用**（详见 `references/impact-factor/iikx-api-cookbook.md`），但覆盖不完全（顶级期刊缺失约 18 本）。应对策略：
  1. 优先依赖 IF 速查表中已收录的期刊
  2. 对未收录期刊标注 `[—]`，不编造 IF
  3. 如需扩展速查表，依据对公开 JCR 数据的认识记录 IF，**同时在 `references/journal-if-verification-needed.md` 中登记需核实的条目**
  4. 在用户交付结果中注明"IF 为近似值，尚未经官方源实时验证"
  5. **iikx.com API** 批量查询（详见 `references/impact-factor/iikx-api-cookbook.md`）——最快路径，免费、JSON 返回、覆盖绝大多数 SCI 期刊。注意约 18 本顶级期刊不在其数据库中。

**IF + 引用数批量查询工作流**：当任务要求输出按 IF 排序的摘要表时：
  1. PubMed 搜索 → 提取 DOIs（pubmed.py 输出自带 DOI 字段）
  2. 用 S2 API 批量查询 citationCount（`api.semanticscholar.org/graph/v1/paper/DOI:{doi}`）
  3. 从 IF 速查表按期刊名匹配 IF；未收录的标注 `—`
  4. 按 IF 降序排列，IF 相同或为 `—` 的按引用数降序
  5. 输出摘要表：标题、第一作者、年份、期刊、IF、引用数
  6. 全程无需用户干预 — 多步查询用 `execute_code` 串联

### 精确论文查找

已知 PMID 或 DOI 时，直接用 PubMed efetch / Semantic Scholar 精确查询：
```bash
# PMID 查询（PubMed efetch XML，含完整摘要和 MeSH）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=36517592&rettype=abstract&retmode=xml&email=your@email.com"

# DOI 查询（Semantic Scholar）
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors,year,abstract,citationCount,openAccessPdf"
```

### 元数据提取

所有提取结果必须转换为 `references/metadata-schema.md` 定义的标准 JSON schema。输出时：

- **单篇**：Markdown 表格格式，字段清晰
- **多篇**：Markdown 列表表格（标题、作者、年份、Venue、引用数、PDF 链接）
- **批量导出**：JSON 数组

### PDF / 全文获取

只获取合法可公开访问的全文。按以下优先级尝试，**每步失败后才进入下一步**，并在结果中记录 `full_text_status`：

1. **PubMed Central (PMC) 全文**：`pmcid` 存在时，直接构造 `https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/`（PMC 是 NIH 授权免费全文仓储，优先级最高）。⚠️ PMC 可能对 curl 返回 Google reCAPTCHA 而非 PDF；此时通过 PMC 页面 meta 标签 `citation_pdf_url` 获取实际 PDF URL 作为参考，转而尝试出版商直链。

2. **Europe PMC**：`https://europepmc.org/articles/{pmcid}` — 覆盖范围更广，含资助信息和数据链接

3. **arXiv / bioRxiv / medRxiv 预印本**：arXiv ID 或 bioRxiv/medRxiv DOI 存在时，直接构造 PDF 直链

4. **Semantic Scholar openAccessPdf**：读取 API 响应 `openAccessPdf.url`

5. **OpenAlex OA 检查**（有 DOI 时执行）：
   ```bash
   curl -s "https://api.openalex.org/works?filter=doi:{doi}&select=id,open_access,best_oa_location" \
     -H "User-Agent: 
arch-skill/2.x (mailto:your@email.com)"
   ```

6. **Unpaywall**（有 DOI 时执行）：
   ```bash
   curl -s "https://api.unpaywall.org/v2/{doi}?email=your@email.com"
   ```

7. **出版商直链兜底**（上述均失败时）：若通过 Europe PMC API 确认论文为 OA (`isOpenAccess: Y`)，尝试出版商 PDF 直链。Nature 系列期刊可用标准 `User-Agent` + `Accept: application/pdf` 头绕过认证重定向。详情及已验证模式见 `references/publisher-pdf-patterns.md`。

8. **告知用户**：如以上均无法获取，明确说明该论文无公开 OA 版本，建议通过机构图书馆、作者邮件或 ILL（馆际互借）获取

**Springer HTML 全文的特殊处理**：若 PDF 路由返回 HTML 而非 PDF 二进制（Content-Type 检查），说明该论文为"HTML 全文"形式（常见于 2024+ online-first 文章）。此时：
- 记录为"HTML 全文可读，无独立 PDF"，不算获取失败
- 返回文章 HTML 页面 URL 供用户在浏览器中阅读

**Cloudflare/403 拦截处理**：Wiley、AGU/Wiley 等出版商对自动请求有强 bot 防护，CDP 浏览器模式也可能被 Cloudflare 拦截。遇到此情况：
- 不要反复重试（会触发更严格封锁）
- 直接跳到步骤 5（OpenAlex）和步骤 6（Unpaywall）检查是否有合法 OA 版本
- 步骤 7 告知用户原因

`full_text_status` 枚举：

| 状态 | 含义 |
|------|------|
| `open_pdf` | 找到可公开访问 PDF |
| `needs_institution` | 论文页可访问，但全文需要机构权限 |
| `no_open_pdf` | 没有发现合法开放全文 |
| `anti_bot_blocked` | 被 Cloudflare、验证码或反爬限制拦截 |
| `html_not_pdf` | PDF 路由返回 HTML 页面而不是 PDF |
| `unknown` | 当前证据不足，无法可靠判断 |

### 开放 PDF 下载与 manifest 导出

Paper-Search 可以下载合法开放访问 PDF，但边界必须清楚：

- 只下载 `full_text_status="open_pdf"` 且存在 `pdf_url` 的论文。
- 不得调用 Sci-Hub、LibGen、shadow library、WebVPN、CARSI、Tor 或 Cloudflare 绕过工具。
- 遇到 `needs_institution`、`no_open_pdf`、`anti_bot_blocked`、`html_not_pdf`、`unknown` 时，不下载，只写入 manifest 并说明原因。
- 批量任务先生成 manifest，再由用户确认是否下载，除非用户明确要求“下载所有开放 PDF”。

推荐流程：

1. 搜索/精确查询论文，生成标准 metadata schema。
2. 通过 PubMed Central、Europe PMC、bioRxiv/medRxiv、Semantic Scholar、Unpaywall 判断 `full_text_status` 和 `pdf_url`。
3. 调用 `scripts/oa-pdf-download.mjs --input <metadata.json> --manifest <manifest.json>` 生成下载清单。
4. 用户确认后，调用 `scripts/oa-pdf-download.mjs --input <metadata.json> --manifest <manifest.json> --download --out-dir <dir>` 下载开放 PDF。
5. 输出下载结果表：标题、PMID/DOI、状态、本地路径、跳过原因。

CLI 示例：

```bash
node scripts/oa-pdf-download.mjs \
  --input /tmp/paper-search-results.json \
  --manifest /tmp/paper-search-download-manifest.json

node scripts/oa-pdf-download.mjs \
  --input /tmp/paper-search-results.json \
  --manifest /tmp/paper-search-download-manifest.json \
  --download \
  --out-dir /tmp/paper-search-pdfs
```

输出 JSON 计数字段：

```json
{"total":3,"eligible":2,"downloaded":1,"skipped":1,"failed":0,"not_pdf":1}
```

`download_status` 枚举：`not_requested`、`eligible`、`downloaded`、`skipped`、`failed`、`not_pdf`。详细字段定义见 `references/metadata-schema.md`。

分工规则：

- 用户要"找论文 / 筛论文 / 查引用 / 生成开放 PDF 清单" → 使用 Paper-Search。
- 用户要"尽可能下载这些 DOI 的 PDF / 用 WebVPN / 多源下载 / Sci-Hub / LibGen" → 明确说明这超出 Paper-Search 边界，并建议切换 scansci-pdf。

如果用户需要下载非开放获取论文，应建议使用机构图书馆、作者邮件、馆际互借，或切换到 scansci-pdf 这类专门的论文获取工具；Paper-Search 不负责绕过访问限制。

不要尝试访问任何需要绕过付费墙的第三方服务。遇到 Elsevier、Wiley、Springer、ACS、Taylor & Francis、JSTOR 等商业出版平台时，先判定开放获取状态；若需要机构访问，停止自动下载并报告 `needs_institution`。

### 批量摘要 + BibTeX 导出工作流

当用户要求「所有文章的摘要和 BibTeX」时，执行以下三遍策略（在既定摘要表基础上增加第三遍）：

**第一遍**：PubMed 搜索 + 引用数补全 → 输出按 IF 排序的摘要表（已有流程）
**第二遍**：用户确认 Top 10 列表
**第三遍**：批量拉取摘要 + 生成 BibTeX

第三遍的具体步骤：

```bash
# 1. 一次性 efetch 所有 PMID（XML 含摘要 + 全量作者 + 元数据）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=PMID1,PMID2,...&retmode=xml" \
  | python3 -c "
import sys, xml.etree.ElementTree as ET
tree = ET.parse(sys.stdin)
for article in tree.findall('.//PubmedArticle'):
    pmid = article.find('.//PMID').text
    title = article.find('.//ArticleTitle').text
    # 摘要
    abstract_parts = article.findall('.//AbstractText')
    abstract = ' '.join([a.text or '' for a in abstract_parts])
    # 全量作者 (BibTeX 格式)
    authors = []
    for author in article.findall('.//Author'):
        last = author.find('LastName')
        fore = author.find('ForeName')
        if last is not None and fore is not None:
            authors.append(f'{last.text}, {fore.text}')
    authors_str = ' and '.join(authors)
    # 期刊 / 卷 / 期 / 页
    journal = article.find('.//Journal/Title').text or ''
    volume = article.find('.//Journal/JournalIssue/Volume')
    volume = volume.text if volume is not None else ''
    issue = article.find('.//Journal/JournalIssue/Issue')
    issue = issue.text if issue is not None else ''
    pages = article.find('.//Pagination/MedlinePgn')
    pages = pages.text if pages is not None else ''
    year = article.find('.//PubDate/Year')
    year = year.text if year is not None else ''
    # DOI
    doi_el = article.find('.//ArticleId[@IdType=\\\"doi\\\"]')
    doi = doi_el.text if doi_el is not None else ''
    
    # 输出摘要 + BibTeX @article
    print(f'PMID: {pmid}')
    print(f'ABSTRACT: {abstract[:500]}')
    print()
    print('@article{Key,')
    print(f'  author    = {{{authors_str}}},')
    print(f'  title     = {{{title}}},')
    print(f'  journal   = {{{journal}}},')
    print(f'  year      = {{{year}}},')
    print(f'  volume    = {{{volume}}},')
    print(f'  number    = {{{issue}}},')
    print(f'  pages     = {{{pages}}},')
    print(f'  doi       = {{{doi}}}')
    print('}')
    print()
"
```

**BibTeX key 生成规则**：`第一作者姓氏年份期刊缩写`（如 `Li2023Nature`）。注意 `&`、`%` 等特殊字符在摘要中需转义。

**关键要点**：
- 一次 efetch 请求可传入最多 100 个 PMID，比逐个请求快 100 倍
- 从 `<Author>` 节点提取的是全量作者列表（PubMed 官方数据），不会截断
- 卷/期/页码均来自 PubMed 标准字段，无需额外访问 Crossref
- 摘要超过 ~500 字符宜截断（终端可读性），完整摘要通过 PMID 链接获取

### Zotero MCP 导入

搜索完成且用户确认论文列表后，可通过 Zotero MCP 工具直接将论文导入用户 Zotero 库：

```python
# 逐篇通过 DOI 导入（推荐）
mcp_zotero_zotero_add_by_doi(
    doi="10.1016/j.cell.2025.03.037",
    tags=["血管类器官", "vascular-organoid"],    # 可选，方便后续分类
    collections=["collection_key"],               # 可选，指定集合
    attach_mode="auto"                            # auto / none / required
)
```

**工作流位置**：此为搜索交付的可选第三通道（在 BibTeX 导出和 PDF 下载之后），在用户确认论文列表后执行，而非自动执行。

**前置条件**：Zotero MCP 需运行在 hybrid 模式（local-only 模式无法写入）。配置方法：
1. 在 https://www.zotero.org/settings/keys 创建 API Key（勾选 Allow library access）
2. 在 Zotero MCP 的 env 中配置 `ZOTERO_API_KEY` 和 `ZOTERO_LIBRARY_ID`
3. 在 Hermes 配置的 `mcp_servers.zotero.env` 中添加对应环境变量

**常见失败模式**：
- `Cannot perform write operations in local-only mode` → 未配置 API Key，需用户补充
- 写入成功但附件因 300MB 云配额失败 → 元数据仍成功入库，PDF 附件失败不影响记录
- DOI 已在库中 → Zotero 自动去重（基于 DOI 匹配），不会创建重复条目
- **批量 MCP 导入 >3 篇时第 4+ 篇超时**：MCP 的 `zotero_add_by_doi` 在单个 turn 中并发调用 ≥4 次时，Zotero 本地 API 的写入锁可能导致后续调用挂起直至超时（120s），进而阻塞整个 MCP 连接。**对策**：(a) ≤3 篇用 MCP 逐个导入（串行调用，每个独立 tool call）；(b) ≥4 篇直接用 Web API fallback（`references/zotero-web-api-import.md`，CrossRef → Zotero Web API POST），跳过 MCP 批量导入路径；(c) 若 MCP 已卡死，等待约 60s 或重启 Zotero MCP server 恢复

**批量导入策略（按数量分级）**：
| 数量 | 方式 | 理由 |
|------|------|------|
| ≤3 篇 | MCP `zotero_add_by_doi` 串行（独立 tool call） | MCP 写入锁在并发≥4时挂起 |
| 4–10 篇 | **并发 CrossRef → 单次 Web API 批量 POST**（`execute_code` 中实现，见 `references/zotero-web-api-import.md`） | 避免 MCP 锁；单次网络往返完成 |
| >10 篇 | 生成 .bib 文件 → 用户手动 Zotero `File → Import` | 避让 MCP 超时和 Web API 速率限制；最快路径 |

**≥4 篇的核心思路**：用 `execute_code` 并发查询 CrossRef（10 篇一起查，网络延迟重叠），组装成 Zotero item 数组后**一次 POST** 到 `api.zotero.org/users/{userID}/items`。总耗时约 5–8s，无需等待 MCP 120s 超时。

**MCP 断开时的 fallback（Zotero Web API + CrossRef）**：若 Zotero MCP 连接丢失（ClosedResourceError 或 MCP 进程被 kill），改用 Zotero Web API 直接通过 curl 导入。全程有三步：
  1. **CrossRef 解析元数据**：`curl -sL "https://api.crossref.org/works/{doi}"` 获取标题、作者、卷期页码
  2. **组装 Zotero item JSON**：将 CrossRef `message` 字段映射到 Zotero item schema（itemType, title, creators, DOI, date, publicationTitle, volume, issue, pages, tags）
  3. **POST 到 Zotero Web API**：`curl -X POST "https://api.zotero.org/users/{userID}/items" -H "Zotero-API-Key: {key}" -H "Content-Type: application/json" -d '[{item}]'`
  完整的 Python 工作流见 `references/zotero-web-api-import.md`。

**常见失败模式**（补全）：
  - MCP 连接断开（ClosedResourceError）：无法在会话中恢复，改走 Web API fallback
  - Zotero API 返回 "Too many authentication failures"（HTTP 429）：因短时间多次认证失败触发，需等待数分钟（通常 3-10 分钟）才能恢复。不要在冷却期内重复请求
  - **API Key 在 terminal 命令中被截断**：Hermes 的安全过滤器可能将终端命令中明文 API Key 替换为 `***` 或截断为 `Key...suffix`，导致认证始终失败。解决方法：将 Key 写入脚本文件再执行，或在 `execute_code` 中通过变量传参
  - 写入成功但附件因 300MB 云配额失败 → 元数据仍成功入库，PDF 附件失败不影响记录
  - DOI 已在库中 → Zotero 自动去重（基于 DOI 匹配），不会创建重复条目

### 作者主页解析

```bash
# Semantic Scholar 作者搜索
curl -s "https://api.semanticscholar.org/graph/v1/author/search?query={author_name}&fields=name,affiliations,paperCount,citationCount"

# 获取作者全部论文（分页）
curl -s "https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?fields=title,year,citationCount,externalIds&limit=100&offset=0"
```

Google Scholar 作者页需 CDP，见 `references/site-patterns/scholar.google.com.md`。

## CDP 模式（Google Scholar 及其他需要浏览器自动化的平台）

通过 CDP Proxy 直连用户日常 Chrome，天然携带登录态。

所有操作在自己创建的后台 tab 中进行，不干扰用户已有 tab，完成后关闭。

### 启动

```bash
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)/.."
bash "$SKILL_DIR/scripts/check-deps.sh"
```

脚本自动检查并启动 CDP Proxy（默认 `127.0.0.1:3456`，可通过 `CDP_PROXY_PORT` 覆盖）。

### 操作方式

进入浏览器层后，用 HTTP API 操控页面：

```bash
# 创建新 tab，导航到目标页
TARGET=$(curl -s "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/new?url=https://scholar.google.com" | node -p "JSON.parse(require('fs').readFileSync(0, 'utf8')).targetId")

# 执行 JS 提取数据
curl -s -X POST "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/eval?target=$TARGET" -d 'document.title'

# 点击元素（CSS 选择器）
curl -s -X POST "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/click?target=$TARGET" -d 'button[type=submit]'

# 完成后关闭 tab
curl -s "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/close?target=$TARGET"
```

完整 API 参考见 `references/cdp-api.md`。

**三种点击方式**：

| 方式 | 端点 | 适用场景 |
|------|------|---------|
| JS click | `/click` | 通用，速度快 |
| 真实鼠标 | `/clickAt` | 需要触发文件对话框或绕过反自动化检测 |
| 文件上传 | `/setFiles` | 直接设置 file input，绕过对话框 |

**先了解页面结构，再决定动作**：用 `/eval document.body.innerText.slice(0, 500)` 或截图快速了解当前页面状态。

## 并行分治策略

任务包含多个**独立**目标时（如同时查询 N 篇论文、N 个来源），分发子 Agent 并行执行。

**好处**：速度 = 单子任务时长；抓取内容不进入主 Agent context，节省 token。

**子 Agent Prompt 写法**：
- 必须写：`必须加载 paper-search skill 并遵循指引`
- 描述**目标**（获取/提取/查找），不要指定具体步骤
- 说明需要哪些字段（标题/引用数/PDF 等）
- **注意用词**：「搜索 BERT 的引用数」会把子 Agent 锚定到 WebSearch；应写「获取 BERT 的引用数」——描述目标，不暗示手段

**典型分治场景**：

| 适合分治 | 不适合分治 |
|---------|-----------|
| 多平台并发查同一论文（arXiv + S2 + PubMed） | 查询有依赖关系（先搜索再按结果查详情） |
| 批量查询 N 篇不相关论文 | 简单单平台单次 API 查询 |
| 多个作者主页并行抓取 | 几次 curl 就能完成的轻量任务 |

**多平台并发查同一论文时的去重**：

子 Agent 返回结果后，主 Agent 按 `references/metadata-schema.md` 中的去重规则合并：DOI 为主键 → PMID 次之 → 标题+年份模糊匹配。

## 信息核实

学术搜索的一手来源是**论文本身**和**数据库官方记录**，不是二手报道。

| 核实目标 | 一手来源 |
|---------|---------|
| 论文元数据（标题、作者、PMID、DOI）| PubMed (MEDLINE) 官方记录 > Crossref > OpenAlex |
| 摘要 / MeSH Terms | PubMed efetch XML |
| 引用数 | Google Scholar（最全）> Semantic Scholar |
| 开放获取状态 | PMC ID 存在 → 确认免费全文；Unpaywall > 出版商页面 |
| 临床试验注册 | ClinicalTrials.gov NCT 记录 |
| 期刊/会议信息 | NLM Catalog > 出版商官网 |

多平台引用数不一致时正常——PubMed 本身不提供引用数，需从 Semantic Scholar/Google Scholar 获取。

## 站点经验

操作中积累的特定网站经验，按域名存储在 `references/site-patterns/` 下。

已预置经验的平台：PubMed、Semantic Scholar、Google Scholar、arXiv、IEEE Xplore、CNKI（知网），以及 ScienceDirect、Wiley、Springer、ACS 等主要出版商访问限制。

确定目标平台后，**必须**读取对应文件获取先验知识（平台特征、有效模式、已知陷阱）。经验内容标注发现日期，当作**可能有效的提示，不是保证正确的事实**——按经验操作失败时，回退通用模式，并**更新经验文件**（记录失败原因和发现日期）。操作成功后若发现了新模式或陷阱，同样主动写入。

## References 索引

| 文件 | 何时加载 |
|------|---------|
| `references/disciplines/biomedical-engineering.md` | 默认加载：所有 BME 检索的 query expansion、平台路由、排序规则 |
| `references/api-cookbook.md` | 需要 API 调用示例、参数说明、响应字段映射时 |
| `references/metadata-schema.md` | 整理提取结果、多平台去重合并、生成 BibTeX 时 |
| `references/cdp-api.md` | 需要 CDP 浏览器操作时（Google Scholar、CNKI 等） |
| `references/disciplines/*.md` | 需要其他学科平台选择、扩展 query 时 |
| `references/rankings/biomed-evidence-ranking.md` | 生物医学证据等级排序时 |
| `references/impact-factor/impact-factor.md` | 用户明确要求影响因子/JCR 分区时加载，覆盖 12 大类 372 刊 IF 速查 |
| `references/impact-factor/iikx-api-cookbook.md` | 程序化查询 iikx.com 免费 IF 数据 API 的参数、子类名称和 Python 示例 |
| `references/impact-factor/journal-if-verification-needed.md` | IF 速查表中未经验证的期刊清单及核实指南 |
| `references/workflows/*.md` | 需要执行系统综述、PRISMA 等研究工作流时 |
| `references/site-patterns/{domain}.md` | 确定目标平台后，读取对应站点经验 |
| `references/site-patterns/pubmed.ncbi.nlm.nih.gov.md` | PubMed 检索必读：E-utilities 流程、字段映射、已知陷阱 |
| `references/site-patterns/cnki.net.md` | 知网检索时必读 |
| `references/zotero-web-api-import.md` | Zotero MCP 不可用时，通过 CrossRef + Zotero Web API 直接导入论文到 Zotero 的 curl/execute_code 工作流（含 MCP fallback、速率限制处理和 API Key 截断陷阱） |
| `references/publisher-pdf-patterns.md` | 标准 OA 管线失败时，各出版商（Nature、Elsevier 等）的直接 PDF 下载模式、User-Agent 要求、PMC reCAPTCHA 坑位及绕过方法 |
