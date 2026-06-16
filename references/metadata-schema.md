# 学术论文元数据规范

跨平台统一的论文元数据结构，用于合并多平台结果、去重、导出 BibTeX。

---

## 标准 Schema（JSON）

```json
{
  "title": "Organ-on-a-chip: a new paradigm for drug development",
  "authors": ["David E Ingber", "Donald E Ingber"],
  "year": 2022,
  "publication_date": "2022-03-15",
  "publication_type": "review",
  "venue": "Nature Reviews Drug Discovery",
  "doi": "10.1038/s41573-022-00410-w",
  "arxiv_id": null,
  "pubmed_id": "35312345",
  "pmcid": "PMC9012345",
  "orcid": [],
  "issn": "1474-1776",
  "isbn": null,
  "cnki_url": null,
  "abstract": "Organ-on-a-chip microdevices combine microfluidics with living human cells...",
  "keywords": ["organ-on-a-chip", "microfluidics", "drug screening", "3D culture"],
  "mesh_terms": ["Lab-On-A-Chip Devices", "Drug Development", "Microfluidics"],
  "jel_codes": [],
  "msc_codes": [],
  "acm_ccs": [],
  "study_type": "review",
  "sample_size": null,
  "population": null,
  "citation_count": 450,
  "download_count": null,
  "open_access_status": "gold",
  "license": "cc-by",
  "full_text_status": "open_pdf",
  "pdf_url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9012345/pdf/",
  "local_pdf_path": null,
  "download_status": "not_requested",
  "download_error": null,
  "download_source": null,
  "data_availability": null,
  "code_url": null,
  "bibtex": "@article{ingber2022organ,...}",
  "source_platforms": ["pubmed", "semanticscholar"],
  "fetched_at": "2026-06-06"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 论文标题，保留原始大小写 |
| `authors` | string[] | 是 | 作者列表。优先使用可直接展示的自然人姓名；若来源仅提供缩写且无法可靠还原，允许保留原格式（如 PubMed 的 `Smith JA`） |
| `year` | integer | 是 | 发表年份（4 位整数） |
| `publication_date` | string | 否 | 发表日期，ISO 8601 格式；预印本、医学文献优先保留到日 |
| `publication_type` | string | 否 | 文献类型，如 `journal-article`、`conference`、`preprint`、`review`、`clinical-trial`、`book-chapter`、`working-paper` |
| `venue` | string | 否 | 会议/期刊名称，包含年份（如 `NeurIPS 2017`） |
| `doi` | string | 否 | 全局唯一标识，格式 `10.xxx/xxx` |
| `arxiv_id` | string | 否 | arXiv ID，仅数字+点格式（如 `1706.03762`） |
| `pubmed_id` | string | 否 | PubMed PMID |
| `pmcid` | string | 否 | PubMed Central 全文 ID |
| `orcid` | string[] | 否 | 作者 ORCID 列表，用于作者消歧 |
| `issn` | string | 否 | 期刊 ISSN |
| `isbn` | string | 否 | 图书或章节 ISBN |
| `cnki_url` | string | 否 | CNKI 论文详情页 URL（知网特有，格式 `https://kns.cnki.net/kcms2/article/abstract?v=...`） |
| `abstract` | string | 否 | 摘要原文 |
| `keywords` | string[] | 否 | 关键词列表（知网、部分期刊平台提供） |
| `mesh_terms` | string[] | 否 | 医学主题词 |
| `jel_codes` | string[] | 否 | 经济学 JEL 分类 |
| `msc_codes` | string[] | 否 | 数学 MSC 分类 |
| `acm_ccs` | string[] | 否 | 计算机 ACM CCS 分类 |
| `study_type` | string | 否 | 医学/社科研究类型，如 RCT、cohort、case-control、survey、qualitative |
| `sample_size` | integer | 否 | 研究样本量 |
| `population` | string | 否 | 研究对象、人群或样本来源 |
| `citation_count` | integer | 否 | 引用数（来自 Scholar 或 Semantic Scholar） |
| `download_count` | integer | 否 | 下载次数（CNKI 特有字段，其他平台为 null） |
| `open_access_status` | string | 否 | 开放获取状态，如 `gold`、`green`、`hybrid`、`bronze`、`closed`、`unknown` |
| `license` | string | 否 | 开放许可，如 `cc-by`、`cc-by-nc` |
| `full_text_status` | string | 否 | 全文访问状态：`open_pdf`、`needs_institution`、`no_open_pdf`、`anti_bot_blocked`、`html_not_pdf`、`unknown` |
| `pdf_url` | string | 否 | 可公开访问的 PDF 直链 |
| `local_pdf_path` | string | 否 | 本地已下载 OA PDF 路径；仅当 `download_status=downloaded` 时填写 |
| `download_status` | string | 否 | OA PDF 下载状态：`not_requested`、`eligible`、`downloaded`、`skipped`、`failed`、`not_pdf` |
| `download_error` | string | 否 | 下载失败或跳过原因，成功时为 null |
| `download_source` | string | 否 | 实际下载来源，如 `arxiv`、`unpaywall`、`openalex`、`semantic_scholar`、`pubmed_central` |
| `data_availability` | string | 否 | 数据可得性说明或数据链接 |
| `code_url` | string | 否 | 代码仓库链接 |
| `bibtex` | string | 否 | BibTeX 格式引用 |
| `source_platforms` | string[] | 是 | 数据来源平台列表（含 `"cnki"` 时表示来自知网） |
| `fetched_at` | string | 是 | 抓取日期，ISO 8601 格式（YYYY-MM-DD） |

---

### OA PDF 下载状态

| 状态 | 含义 |
|------|------|
| `not_requested` | 未请求下载，仅完成元数据或 OA 状态判定 |
| `eligible` | `full_text_status=open_pdf` 且存在可公开访问的 `pdf_url`，可下载 |
| `downloaded` | 已下载到本地，`local_pdf_path` 有值 |
| `skipped` | 不满足下载条件，如需要机构权限、无开放 PDF、缺少 URL |
| `failed` | 网络错误、HTTP 错误或文件写入错误 |
| `not_pdf` | URL 返回内容不是 PDF 二进制 |

---

## Markdown 表格模板

单篇论文输出：

```markdown
| 字段 | 内容 |
|------|------|
| 标题 | Organ-on-a-chip: a new paradigm for drug development |
| 作者 | Ingber et al. (2022) |
| 期刊 | Nature Reviews Drug Discovery |
| PMID | 35312345 |
| DOI | 10.1038/s41573-022-00410-w |
| 引用数 | ~450 |
| PDF | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9012345/pdf/ |
| 摘要 | Organ-on-a-chip microdevices combine microfluidics with living human cells... |
```

多篇论文列表输出：

```markdown
| 标题 | 作者 | 年份 | 期刊 | PMID | 引用 | PDF |
|------|------|------|------|------|------|-----|
| Organ-on-a-chip... | Ingber et al. | 2022 | Nat Rev Drug Discov | 35312345 | 450 | [PDF](pmc_url) |
| Microfluidic BBB... | Park et al. | 2023 | Lab Chip [JCR Q1] | 38234567 | 320 | [PDF](pmc_url) |
```

---

## 多平台去重规则

多个子 Agent 并行查询同一目标时，结果需按以下优先级合并去重：

### 主键优先级

1. **DOI**（全局唯一，最可靠）：DOI 相同 → 同一篇论文
2. **PubMed ID**：PMID 相同 → 同一篇论文
3. **标题 + 年份 + 第一作者姓氏**：以上都没有时的模糊匹配

### 字段合并策略

同一篇论文来自多个平台时，字段按以下优先级填充：

| 字段 | 优先来源 |
|------|---------|
| `citation_count` | Google Scholar > Semantic Scholar > 其他 |
| `open_access_status` | PMC ID 检测 > Unpaywall > 出版商页面 > OpenAlex |
| `full_text_status` | 实际下载/访问验证结果 > PMC ID > Unpaywall > 其他 |
| `pdf_url` | PMC > Europe PMC > bioRxiv/medRxiv > arXiv > Unpaywall |
| `abstract` | PubMed efetch > Semantic Scholar > 其他 |
| `venue` | PubMed (MEDLINE) > Crossref > Semantic Scholar |
| `doi` | PubMed > Crossref > Semantic Scholar |
| `bibtex` | metadata-schema 拼装 > arXiv BibTeX 端点 > 平台导出 |
| `keywords` | PubMed MeSH > 出版商页面 > 其他平台 |
| `mesh_terms` | PubMed / Europe PMC |
| `code_url` | Papers with Code > 论文官方页面 > GitHub 链接 |
| `download_count` | 仅 CNKI 提供，无需合并 |

### 合并示例

```
arXiv 结果：  { title: "BERT...", arxiv_id: "1810.04805", pdf_url: "https://arxiv.org/pdf/1810.04805" }
S2 结果：     { title: "BERT...", arxiv_id: "1810.04805", citation_count: 65000, doi: "10.18653/..." }
→ 合并后：   { title: "BERT...", arxiv_id: "1810.04805", doi: "10.18653/...",
               pdf_url: "https://arxiv.org/pdf/1810.04805", citation_count: 65000 }
```

---

## BibTeX 拼装模板

当平台无法直接导出 BibTeX 时，根据 schema 字段拼装：

### 会议论文（@inproceedings）

```bibtex
@inproceedings{[citation_key],
  title     = {[title]},
  author    = {[authors, joined by " and "]},
  booktitle = {[venue]},
  year      = {[year]},
  doi       = {[doi]},
  url       = {[pdf_url]}
}
```

### 期刊论文（@article）

```bibtex
@article{[citation_key],
  title   = {[title]},
  author  = {[authors, joined by " and "]},
  journal = {[venue]},
  year    = {[year]},
  doi     = {[doi]},
  url     = {[pdf_url]}
}
```

### 预印本（@misc，用于无正式 venue 的 arXiv 论文）

```bibtex
@misc{[citation_key],
  title         = {[title]},
  author        = {[authors, joined by " and "]},
  year          = {[year]},
  eprint        = {[arxiv_id]},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/[arxiv_id]}
}
```

**citation_key 生成规则**：`{作者姓氏小写}{年份}{标题第一个实词小写}`。若首位作者是 PubMed 风格的 `LastName Initials`，姓氏取第一个空格前的片段。  
示例：`vaswani2017attention`、`devlin2019bert`

---

## 平台字段名对照表

| 标准字段 | arXiv XML | Semantic Scholar | PubMed esummary docsum | ACM JSON-LD | IEEE API | CNKI CDP |
|---------|-----------|-----------------|---------------|-------------|---------|---------|
| title | `<title>` | `title` | `title` | `name` | `title` | `td.name a` / `h1.title` |
| authors | `<author><name>` | `authors[].name` | `authors[].name`（常为 `LastName Initials`） | `author[].name` | `authors.authors[].full_name` | `td.author` / `.author a` |
| year | `<published>`[0:4] | `year` | `pubdate`[0:4] | `datePublished`[0:4] | `publication_year` | `td.date`[0:4] |
| doi | `<arxiv:doi>` | `externalIds.DOI` | `articleids[doi].value` | `@id`（DOI URL） | `doi` | `.doi a` |
| arxiv_id | `<id>`（末段） | `externalIds.ArXiv` | - | - | - | - |
| abstract | `<summary>` | `abstract` | （需 efetch） | `description` | `abstract` | `#ChDivSummary` |
| citation_count | - | `citationCount` | - | - | `citing_paper_count` | `td.quote a` |
| download_count | - | - | - | - | - | `td.download a` |
| keywords | - | - | - | - | - | `.keyword a` |
| cnki_url | - | - | - | - | - | `location.href`（详情页） |
| pdf_url | `<link type=pdf>` | `openAccessPdf.url` | - | - | `pdf_url` | `.btn-dlcaj` / `.btn-pdfdown`（需登录） |
