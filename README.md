<p align="center">
  <img src="assets/logo.png" alt="paper-search" width="80" style="vertical-align:middle; margin-right:12px;" />
  <strong style="font-size:2em; vertical-align:middle;">Paper-Search Skill</strong>
</p>

<p align="center">面向生物医学工程的 AI 学术论文搜索助手 — PubMed 优先，医工交叉。</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v2.1.0-0f766e" />
  <img src="https://img.shields.io/badge/license-MIT-1f2937" />
  <img src="https://img.shields.io/github/stars/duxuan11/paper-search?style=social" />
</p>

<p align="center">🌐 <a href="README.en.md">English</a> | 简体中文</p>

---

## News

- `2026-06-16` **Git 历史清理**：移除所有上游原始仓库 commit，仅保留本仓库的「first commit / second commit」两条根记录
- `2026-06-16` **影响因子表大规模更新**：从 ~80 条扩展至 **372 条**（12 大类），通过 iikx.com API 实时查询 2024 IF 数据。新增细胞生物学、免疫学、遗传学、纳米医学、药物学等 7 个类别
- `2026-06-16` **项目重命名**：`academic-search` → `paper-search`，GitHub 地址迁移至 `duxuan11/paper-search`
- `2026-06-12` 新增 iikx.com IF 免费 API 程序化查询指南：`references/impact-factor/iikx-api-cookbook.md`
- `2026-06-09` SKILL.md 重写，完善多组学查询策略、S2 429 限流应对、Zotero 批量导入分级方案
- `2026-06-06` 影响因子速查表初版（5 大类 ~80 刊）
- `2026-05-08` 新增 OA PDF 下载 manifest 与开放 PDF 批量下载 helper

---

🚀 **生物医学工程优先**：PubMed 为默认检索入口，MeSH 受控词表扩展，辅以 Semantic Scholar、Europe PMC、Crossref 等。
📊 **IF 速查丰富**：覆盖 12 大类 372 本期刊的 2024 IF，支持程序化 iikx.com API 批量查询。
📑 **开放获取合规**：开放 PDF 级联获取，明确标注机构权限和反爬限制，不绕过付费墙。
🎯 **两遍搜索策略**：先摘要表后深拉元数据，筛出核心论文再完整获取。
🧾 **Zotero 导入**：按论文数量自动选择 MCP 串行 / Web API 批量 / BibTeX 文件导入。

> **Paper-Search：面向生物医学工程的知识发现助手。**

## Quick Start

```bash
git clone https://github.com/duxuan11/paper-search ~/.claude/skills/paper-search
bash ~/.claude/skills/paper-search/scripts/check-deps.sh
```

然后直接对 AI 助手说：

```
搜索近 3 年关于血管类器官的论文，按影响因子排序，输出前 10 篇
```

---

## 核心能力

**检索与筛选**
- PubMed 优先：生物医学工程文献检索黄金标准，MeSH 受控词表覆盖工程技术+临床医学两面
- 两遍策略：先输出轻量摘要表（含 IF、引用数、开放 PDF 状态），确认核心论文后再深拉完整元数据
- Query 扩展：同义词 / 子概念 / 缩写全称自动展开，MeSH 词表 + 自由文本双重匹配
- **IF 排序**：内建 12 大类 372 刊 IF 速查表，支持程序化 iikx.com API 批量查询
- 证据等级排序：系统综述 > RCT > 队列研究 > 病例报告；预印本单独标注
- 多平台结果以 DOI/PMID 为主键自动去重合并

**数据获取**
- PDF：开放获取 PDF 级联获取（PMC → Europe PMC → bioRxiv/medRxiv → S2 → OpenAlex → Unpaywall → 出版商直链兜底）
- 全文状态：标注 `open_pdf` / `needs_institution` / `no_open_pdf` / `anti_bot_blocked` / `html_not_pdf`
- OA PDF 下载：生成 manifest，只下载合法开放 PDF，不涉及 Sci-Hub/WebVPN/Tor
- BibTeX：一次性 efetch 拿到全量作者 + 卷期页码，无需逐个访问 Crossref
- 引用数：Semantic Scholar API，Google Scholar 补充

**Zotero 导入**
- 搜索完成后直接通过 MCP 或 Web API 将论文导入 Zotero 库
- 按数量分级：≤3 篇 MCP 串行 / 4–10 篇 Web API 批量 / >10 篇 BibTeX 文件导入

**可靠性与扩展**
- 失败信号处理：429 / 超时 / 空结果各有对应调整策略
- CDP 浏览器模式：直连用户日常 Chrome，用于 Google Scholar 和 CNKI
- 并行分治：多目标分发子 Agent 并行执行
- 站点经验预置：arXiv、Semantic Scholar、PubMed、IEEE、CNKI 等平台操作经验已预置

## 影响因子速查

Paper-Search 内建覆盖 **12 大类、372 本**期刊的 2024 JCR IF 速查表：

| 类别 | 期刊数 | 代表期刊 |
|------|--------|---------|
| 综合顶刊与方法学 | 59 | Nature/Science/Cell 系列、Adv Mater、PNAS 等（IF 6.4–101.8） |
| 类器官/器官芯片/生物材料 | 41 | Biomaterials, Bioactive Materials, Lab Chip, Tissue Eng 等 |
| 细胞生物学与发育生物学 | 26 | Cell Death & Diff, Autophagy, Apoptosis, Development 等 |
| 医学影像/AI/生物信息学 | 30 | Med Image Anal, IEEE TMI, Nature Mach Intell, Radiology 等 |
| 生物工程与应用微生物 | 25 | Trends Biotechnol, Bioresource Technol 等 |
| 生化与分子生物学 | 31 | Mol Cancer, Nucleic Acids Res, Mol Cell, Redox Biol 等 |
| 免疫学 | 33 | Immunity, Nat Rev Immunol, J Immunother Cancer 等 |
| 纳米科学与纳米医学 | 20 | ACS Nano, J Nanobiotechnol 等 |
| 遗传学与基因组学 | 34 | Nat Rev Genet, Genome Biol, Am J Hum Genet 等 |
| 药物学与治疗学 | 24 | Signal Transduct Target Ther, Pharmacol Rev, Gene Ther 等 |
| 皮肤生物学与皮肤病学 | 19 | JAAD, Br J Dermatol, Wound Repair 等 |
| 高频发文大刊 | 30 | Sci Rep, PLOS One, Sensors 等 |

IF 数据来源：[iikx.com](https://www.iikx.com/sci/) 免费 API，支持程序化批量查询（参见 `references/impact-factor/iikx-api-cookbook.md`）。

## 学科路由

默认按 **生物医学工程** 方向检索，支持 7 大学科路由：

| 学科 | 首选方向 |
|------|----------|
| **生物医学工程（默认）** | PubMed、Europe PMC、bioRxiv/medRxiv、IEEE Xplore（医工交叉） |
| 医学 / 生命科学 | PubMed、PMC、Europe PMC、ClinicalTrials.gov |
| 计算机 / AI（医疗 AI 交叉） | arXiv、Semantic Scholar、IEEE、Papers with Code |
| 化学 / 材料（生物材料交叉） | PubMed、Crossref、ACS、RSC、Springer |
| 物理 / 数学 | arXiv、NASA ADS、INSPIRE HEP |
| 经济 / 社科 | RePEc、NBER、SSRN |
| 人文 / 法律 | Google Scholar、JSTOR、Project MUSE |

---

## 安装

```bash
# 方式一：手动安装
git clone https://github.com/duxuan11/paper-search ~/.claude/skills/paper-search

# 方式二：让 AI 安装
# 帮我安装这个 skill：https://github.com/duxuan11/paper-search

# 方式三：本地开发软链接（在项目目录内执行）
ln -sfn "$(pwd)" ~/.claude/skills/paper-search
```

**前置要求（仅 CDP 模式需要）**：arXiv / PubMed / Semantic Scholar 等 API 平台直接可用。如需访问 Google Scholar 或 CNKI，需开启 Chrome 远程调试：

1. 打开 `chrome://inspect/#remote-debugging`
2. 勾选 **Allow remote debugging for this browser instance**

---

## 平台访问策略

Open API 优先，Google Scholar 与 CNKI 等需要 Chrome 远程调试：

| 平台 | 访问方式 |
|------|---------|
| **PubMed** | **NCBI E-utilities（首选）** |
| Semantic Scholar | REST API |
| Crossref | REST API |
| OpenAlex | REST API |
| Unpaywall | REST API |
| Europe PMC | REST API |
| bioRxiv / medRxiv | REST API |
| ClinicalTrials.gov | REST API |
| arXiv | REST API |
| Papers with Code | REST API |
| ACM DL | WebFetch + Jina |
| IEEE Xplore | WebFetch / Jina / 官方 API |
| ScienceDirect / Wiley / Springer / ACS | 开放获取判定 + 机构访问提示 |
| **Google Scholar** | **CDP 浏览器（需 Chrome 调试）** |
| **CNKI（知网）** | **CDP 浏览器（需 Chrome 调试）** |

全文获取只针对合法开放访问来源。

---

## 使用示例

```
搜索近 3 年关于血管类器官的论文，按影响因子排序
```

```
帮我找 Yann LeCun 在 Semantic Scholar 上的所有论文，按引用数排序
```

```
这篇论文的 BibTeX：10.1038/s41586-023-06436-1
```

```
同时调研 BERT、GPT-3、T5 的元数据和引用数，做对比表格
```

```
搜索 time series agent 近两年的论文，生成开放 PDF 下载清单
```

```
帮我查一下 Biomaterials 期刊的最新影响因子
```

### 开放 PDF 下载清单

Paper-Search 可以把检索结果转换成开放 PDF 下载清单：

```bash
node scripts/oa-pdf-download.mjs \
  --input results.json \
  --manifest download-manifest.json
```

确认后只下载 `open_pdf` 记录：

```bash
node scripts/oa-pdf-download.mjs \
  --input results.json \
  --manifest download-manifest.json \
  --download \
  --out-dir ./papers
```

### 与 scansci-pdf 的分工

Paper-Search 负责检索、筛选、元数据、影响因子查询和开放 PDF 清单生成。
如果任务是"尽可能下载论文 PDF"（涉及 WebVPN、机构代理、多源竞速），应交给 scansci-pdf 处理。

---

## CDP Proxy API

```bash
curl -s "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/new?url=URL"                              # 新建 tab
curl -s -X POST "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/eval?target=ID" -d 'JS 表达式'    # 执行 JS
curl -s -X POST "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/click?target=ID" -d 'CSS 选择器'  # 点击元素
curl -s "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/close?target=ID"                          # 关闭 tab
```

完整参考见 [`references/cdp-api.md`](references/cdp-api.md)。

---

## 项目结构

```
paper-search/
├── Makefile                    # 标准测试入口（make test / make test-release）
├── SKILL.md                    # 主指令文件（搜索哲学、平台矩阵、核心能力）
├── scripts/
│   ├── cdp-proxy.mjs           # CDP Proxy（直连用户 Chrome）
│   ├── check-deps.sh           # 环境检查 + 自动启动 Proxy
│   ├── oa-pdf-download.mjs     # OA PDF manifest 生成与开放 PDF 下载
│   ├── bibtex-export.py        # BibTeX 导出脚本
│   ├── self-test.sh            # 本地回归测试
│   └── release-test.sh         # 发布前测试
├── references/
│   ├── api-cookbook.md         # 多平台 API 调用速查
│   ├── metadata-schema.md      # 跨平台统一元数据 schema
│   ├── venue-rankings.md       # 学术期刊/会议等级速查
│   ├── cdp-api.md              # CDP Proxy HTTP API 完整参考
│   ├── disciplines/            # 多学科学科路由与 query expansion
│   ├── rankings/               # 证据等级 / 期刊排序参考
│   ├── impact-factor/          # 影响因子速查表（372 刊 12 大类）+ iikx API cookbook
│   ├── workflows/              # 系统综述等工作流
│   ├── site-patterns/          # 平台与出版商操作经验
│   └── publisher-pdf-patterns.md
└── docs/
    ├── skill-usage-comparison.md
    └── multidisciplinary-improvement-analysis.md
```

测试：`make test` / `make test-release`

---

## 设计理念

> Skill = 哲学 + 技术事实，不是操作手册。讲清 tradeoff 让 AI 自己选，不替它推理。

搜索的瓶颈不在"搜"，在"筛"。核心策略是先输出轻量摘要表，让用户确认核心论文后再深拉，避免无效的完整元数据抓取。

排序策略：**临床证据等级优先**（系统综述 > RCT > 队列研究 > 病例报告）+ **工程验证维度**（已验证系统 > 体内原型 > 体外原型 > 计算模型）。近 6 个月论文标注 `[新]` 置顶。

API 优先、CDP 作为兜底，结果统一结构化输出。影响因子通过 iikx.com API 程序化查询，支持按 IF 降序排列。

---

## License

MIT
