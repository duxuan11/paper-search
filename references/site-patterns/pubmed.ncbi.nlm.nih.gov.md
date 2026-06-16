---
domain: pubmed.ncbi.nlm.nih.gov
aliases: [PubMed, NCBI, MEDLINE]
updated: 2026-04-01
---

## 平台特征

- NIH（美国国立卫生研究院）维护，覆盖生命科学、医学、生物信息学
- 完全公开的 E-utilities API，无需鉴权（有 API Key 可提升速率）
- API Key 免费申请：`https://www.ncbi.nlm.nih.gov/account/`
- 速率：无 Key 3 req/s；有 Key 10 req/s；请求加 `&email=your@email.com` 有助于联系配额
- PMC（PubMed Central）子集论文有全文免费访问

## 有效模式

### E-utilities 推荐流程

**Step 1：esearch — 获取 PMID 列表**

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=CRISPR+gene+editing&retmax=20&retmode=json&email=your@email.com"
```

- `retmax` 上限：10000（单次）
- 时间范围：`term=cancer[Title]&datetype=pdat&mindate=2023&maxdate=2024`
- 期刊过滤：`term=Nature[Journal]+AND+machine+learning`

**Step 2：esummary — 获取 DocSum JSON 元数据**

```bash
# JSON 元数据（DocSum，易解析）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=36517592,37112345&retmode=json&email=your@email.com"
```

**Step 3：efetch — 获取 XML 详情 / 完整摘要**

```bash
# XML 全量格式（含完整摘要）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=36517592&rettype=abstract&retmode=xml&email=your@email.com"
```

**Step 4（可选）：elink — 获取相关文献**

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pubmed&id=36517592&linkname=pubmed_pubmed&retmode=json&email=your@email.com"
```

### 字段映射（`esummary` / DocSum JSON）

```
result[pmid].title          → title
result[pmid].authors[].name → authors[]（格式：LastName FirstInitials）
result[pmid].pubdate        → year（前 4 位，格式可能为 "2023 Jan 15"）
result[pmid].source         → venue（期刊名缩写）
result[pmid].fulljournalname→ venue（全称）
result[pmid].uid            → pubmed_id
result[pmid].articleids[type=doi].value → doi
result[pmid].articleids[type=pmc].value → pmc_id（如有，可获取免费全文）
```

### PMC 全文访问

```bash
# PMC ID 格式：PMC + 数字（如 PMC9750103）
# 全文 PDF（部分可访问）
curl -s "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9750103/pdf/"
```

### BibTeX 拼装

PubMed 无 BibTeX 导出端点，从 `esummary` 字段拼装：

```
@article{[pmid],
  title   = {[title]},
  author  = {[authors joined by " and "]},
  journal = {[fulljournalname]},
  year    = {[pubdate 前4位]},
  doi     = {[doi]},
  pmid    = {[uid]}
}
```

## 已知陷阱

- `esummary` 才返回 JSON DocSum 元数据；`efetch` 主要用于 XML 详情/摘要，不要把 `efetch` 当成 JSON metadata 接口（发现于 2026-04-01）
- **复杂 query 的 URL 编码陷阱（发现于 2026-06-06）**：含空格/引号/括号/加号(`+`)的 query 直接用 `curl 'https://...?term=...'` 常因 shell 解释或 curl 的 URL globbing（exit code 3）而静默失败。正确做法：用 `-G` + `--data-urlencode` 模式：
  ```bash
  curl -s -G 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi' \
    --data-urlencode 'db=pubmed' \
    --data-urlencode 'retmax=50' \
    --data-urlencode 'retmode=json' \
    --data-urlencode 'datetype=pdat' \
    --data-urlencode 'mindate=2021' \
    --data-urlencode 'maxdate=2026' \
    --data-urlencode 'email=user@example.com' \
    --data-urlencode 'term=(organ-on-a-chip[Title/Abstract] OR "organ chip"[Title/Abstract]) AND (multiomics[Title/Abstract] OR "multi-omics"[Title/Abstract])'
  ```
  `-G` 将 `--data-urlencode` 的参数附加到 GET 请求的 URL 上，同时自动处理所有特殊字符编码。不要再用 `curl -s 'https://...?term='` 拼 URL 字符串的传参方式。
- 作者名格式为 `LastName FirstInitials`（如 `Smith JA`），非全名，BibTeX 中需保持此格式或标注来源
- `pubdate` 字段格式不统一，可能是 "2023"、"2023 Jan"、"2023 Jan 15" 等，取前 4 位提取年份
- 批量 efetch 时，`id` 参数多个 PMID 用逗号分隔，单次建议不超过 200 个
- 非生物医学领域论文收录很少，该平台仅适用于生命科学/医学领域
- `pmc` articleid 存在表示 PMC 有收录，但不代表可免费获取全文（需进一步确认 Open Access 状态）
