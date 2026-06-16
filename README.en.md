<table>
  <tr>
    <td width="220" valign="middle">
      <img src="assets/logo.png" alt="paper-search logo" width="180" />
    </td>
    <td valign="middle">
      <h1>paper-search skill</h1>
    </td>
  </tr>
</table>

<p align="center">Biomedical-engineering-first academic paper search — PubMed-first, cross-disciplinary metadata fusion</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v2.1.0-0f766e" alt="version" />
  <img src="https://img.shields.io/badge/license-MIT-1f2937" alt="license" />
  <img src="https://img.shields.io/badge/test-make%20test%20%7C%20make%20test--release-2563eb" alt="test" />
</p>

<p align="center">
  <a href="https://github.com/duxuan11/paper-search/stargazers">
    <img src="https://img.shields.io/github/stars/duxuan11/paper-search?style=social" alt="GitHub stars" />
  </a>
  <a href="https://github.com/duxuan11/paper-search/commits/main">
    <img src="https://img.shields.io/github/last-commit/duxuan11/paper-search" alt="last commit" />
  </a>
  <a href="https://github.com/duxuan11/paper-search">
    <img src="https://img.shields.io/badge/repo-GitHub-111827?logo=github" alt="repo link" />
  </a>
</p>

<p align="center"><a href="README.md">简体中文</a> | English</p>

paper-search is an academic search skill for AI agents, designed for biomedical engineering and cross-disciplinary literature retrieval. It uses **PubMed as the default entry point** (NCBI E-utilities) with MeSH-controlled vocabulary expansion, supplemented by Semantic Scholar, Europe PMC, Crossref, OpenAlex, Unpaywall, bioRxiv/medRxiv, and more.

Key differentiators: **PubMed-first biomedical engineering focus**, **built-in 372-journal impact factor table** (12 categories, 2024 IF), **programmatic IF lookup via iikx.com API**, and **two-pass search strategy** (lightweight summary first, deep fetch later).

## Quick Start

```bash
git clone https://github.com/duxuan11/paper-search ~/.claude/skills/paper-search
bash ~/.claude/skills/paper-search/scripts/check-deps.sh
```

Once installed, ask your AI assistant:

```text
Search for papers on vascular organoids from the last 3 years, sorted by impact factor, top 10
```

## News

- `2026-06-16` **Git history cleaned**: All upstream commits removed; repo now starts clean from two root commits
- `2026-06-16` **IF table expanded**: From ~80 to **372 journals** across 12 categories, with 2024 IF data verified via iikx.com API. New categories: cell biology, immunology, genetics, nanomedicine, pharmacology
- `2026-06-16` **Project renamed**: `academic-search` → `paper-search`, moved to `duxuan11/paper-search`
- `2026-06-12` Added iikx.com free IF API query guide: `references/impact-factor/iikx-api-cookbook.md`
- `2026-06-09` SKILL.md rewrite: multi-omics search strategy, S2 429 rate-limit handling, Zotero batch import tiered scheme
- `2026-06-06` Initial IF lookup table (5 categories, ~80 journals)
- `2026-05-08` Added OA PDF download manifest and batch download helper

## Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
- [Impact Factor Lookup](#impact-factor-lookup)
- [Installation](#installation)
- [Requirements](#requirements)
- [Testing](#testing)
- [Usage Examples](#usage-examples)
- [Relationship With scansci-pdf](#relationship-with-scansci-pdf)
- [Multidisciplinary Usage](#multidisciplinary-usage)
- [Platforms and Access Strategy](#platforms-and-access-strategy)
- [CDP Proxy API](#cdp-proxy-api)
- [Project Structure](#project-structure)
- [Design Principles](#design-principles)
- [License](#license)

## Overview

- **Platform coverage**: PubMed (primary), Semantic Scholar, Europe PMC, Crossref, OpenAlex, Unpaywall, arXiv, bioRxiv/medRxiv, ClinicalTrials.gov, Google Scholar, ACM DL, IEEE Xplore, Papers with Code, CNKI
- **Operating principles**: PubMed-first, API-first, structured-output-first, CDP only when necessary
- **Typical tasks**: keyword search, impact factor lookup, citation analysis, PDF/BibTeX retrieval, Zotero import, systematic review support
- **Target users**: researchers and AI agents in biomedical engineering, organoids, organ-on-a-chip, medical imaging, AI in medicine, cell biology, and related fields

## Core Features

| Capability | Description |
|-----------|-------------|
| PubMed-first search | NCBI E-utilities with MeSH terms; covers 3,400+ biomedical journals |
| Impact factor lookup | Built-in 12-category, 372-journal IF table (2024 data); programmatic iikx.com API support |
| Two-pass search | Lightweight summary table first → deep fetch only for confirmed core papers |
| Query expansion | MeSH-controlled vocabulary + free-text; synonyms, sub-concepts, abbreviations |
| Evidence-level ranking | Systematic review > RCT > cohort > case report; preprints labeled separately |
| IF-sorted output | Journals matched against built-in IF table; sort by IF descending |
| Cross-platform dedup | DOI/PMID as primary key, title+year fuzzy match as secondary |
| Open-access PDF cascade | PMC → Europe PMC → bioRxiv/medRxiv → S2 → OpenAlex → Unpaywall → publisher fallback |
| Full-text access status | Records `open_pdf`, `needs_institution`, `no_open_pdf`, `anti_bot_blocked`, etc. |
| BibTeX export | One-shot NCBI efetch for all authors + volume/issue/pages |
| Zotero import | Tiered strategy: ≤3 via MCP serial / 4–10 via Web API batch / >10 via .bib file |
| Citation counts | Semantic Scholar API + Google Scholar supplement |
| CDP browser mode | Direct Chrome connection for Google Scholar and CNKI |
| Failure signal handling | 429 / timeout / empty results each have explicit direction adjustments |
| Pre-seeded site knowledge | Platform patterns for PubMed, Semantic Scholar, arXiv, IEEE, CNKI, etc. |

## Impact Factor Lookup

Paper-Search ships with a comprehensive 2024 JCR IF lookup table covering **372 journals across 12 categories**:

| Category | Journals | Examples |
|----------|----------|----------|
| Top-Tier & Methods | 59 | Nature/Science/Cell, Adv Mater, PNAS (IF 6.4–101.8) |
| Organoids, OoC & Biomaterials | 41 | Biomaterials, Bioactive Materials, Lab Chip, Tissue Eng |
| Cell Biology & Development | 26 | Cell Death & Diff, Autophagy, Apoptosis, Development |
| Medical Imaging, AI & Bioinformatics | 30 | Med Image Anal, IEEE TMI, Nature Mach Intell, Radiology |
| Biotechnology & Microbiology | 25 | Trends Biotechnol, Bioresource Technol |
| Biochemistry & Molecular Biology | 31 | Mol Cancer, Nucleic Acids Res, Mol Cell, Redox Biol |
| Immunology | 33 | Immunity, Nat Rev Immunol, J Immunother Cancer |
| Nanoscience & Nanomedicine | 20 | ACS Nano, J Nanobiotechnol |
| Genetics & Genomics | 34 | Nat Rev Genet, Genome Biol, Am J Hum Genet |
| Pharmacology & Therapeutics | 24 | Signal Transduct Target Ther, Pharmacol Rev, Gene Ther |
| Dermatology & Skin Biology | 19 | JAAD, Br J Dermatol, Wound Repair |
| Mega Journals | 30 | Sci Rep, PLOS One, Sensors |

IF data sourced from [iikx.com](https://www.iikx.com/sci/) free API. See `references/impact-factor/iikx-api-cookbook.md` for programmatic batch queries.

## Installation

**Option 1: Let AI install it**

```
Install this skill for me: https://github.com/duxuan11/paper-search
```

**Option 2: Manual**

```bash
git clone https://github.com/duxuan11/paper-search ~/.claude/skills/paper-search
```

**Option 3: Local symlink (for development)**

```bash
ln -sfn "$(pwd)" ~/.claude/skills/paper-search
```

## Requirements

PubMed, Semantic Scholar, arXiv, and other API-based platforms work out of the box with no setup.

CDP mode requires **Node.js 22+** and Chrome remote debugging:

1. Open `chrome://inspect/#remote-debugging` in Chrome
2. Check **Allow remote debugging for this browser instance**

Environment check (runs automatically):

```bash
bash ~/.claude/skills/paper-search/scripts/check-deps.sh
```

## Testing

```bash
cd paper-search
make test         # local regression test
make test-release # pre-release regression test
```

## Usage Examples

```
Search for papers on vascular organoids from the last 3 years, sorted by impact factor, top 10
```

```
Find all papers by Yann LeCun on Semantic Scholar, sorted by citation count
```

```
Get the BibTeX for this paper: 10.1038/s41586-023-06436-1
```

```
Look up BERT, GPT-3, and T5 in parallel — give me a comparison table with metadata and citation counts
```

```
Check Google Scholar for the citation count of "Attention Is All You Need"
```

```
What is the latest impact factor of Biomaterials?
```

### Open-Access PDF Download Manifest

Generate a manifest:

```bash
node scripts/oa-pdf-download.mjs \
  --input results.json \
  --manifest download-manifest.json
```

Download only `open_pdf` records:

```bash
node scripts/oa-pdf-download.mjs \
  --input results.json \
  --manifest download-manifest.json \
  --download \
  --out-dir ./papers
```

### Relationship With scansci-pdf

Paper-Search handles discovery, filtering, metadata, impact factor lookup, and open-access PDF manifests.
For maximal PDF acquisition (WebVPN, institutional proxy, source racing), use scansci-pdf.

## Multidisciplinary Usage

| Discipline | Focus |
|------------|-------|
| **Biomedical Engineering (default)** | **PubMed**, Europe PMC, bioRxiv/medRxiv, IEEE Xplore |
| Medicine / Life Science | PubMed, PMC, Europe PMC, ClinicalTrials.gov |
| CS / AI (medical AI) | arXiv, Semantic Scholar, IEEE, Papers with Code |
| Chemistry / Materials (biomaterials) | PubMed, Crossref, ACS, RSC, Springer |
| Physics / Mathematics | arXiv, NASA ADS, INSPIRE HEP |
| Social Science / Economics | RePEc, NBER, SSRN |
| Humanities / Law | Google Scholar, JSTOR, Project MUSE |

## Platforms and Access Strategy

| Platform | Access Method | Requires Chrome Debugging |
|----------|--------------|:------------------------:|
| **PubMed** | **NCBI E-utilities (primary)** | No |
| Semantic Scholar | REST API | No |
| Crossref | REST API | No |
| OpenAlex | REST API | No |
| Unpaywall | REST API | No |
| Europe PMC | REST API | No |
| bioRxiv / medRxiv | REST API | No |
| ClinicalTrials.gov | REST API | No |
| arXiv | REST API | No |
| Papers with Code | REST API | No |
| ACM DL | WebFetch + Jina | No |
| IEEE Xplore | WebFetch / Jina / Official API | No |
| ScienceDirect / Wiley / Springer / ACS | Open-access check + institution notice | No |
| Google Scholar | CDP browser | **Yes** |
| CNKI | CDP browser | **Yes** |

## CDP Proxy API

```bash
bash ~/.claude/skills/paper-search/scripts/check-deps.sh
curl -s "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/new?url=https://scholar.google.com"
curl -s -X POST "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/eval?target=ID" -d 'document.title'
curl -s "http://127.0.0.1:${CDP_PROXY_PORT:-3456}/close?target=ID"
```

See `references/cdp-api.md` for the full API reference.

## Project Structure

```
paper-search/
├── Makefile
├── SKILL.md                          # Main instruction (philosophy + platform matrix + capabilities)
├── README.md                         # Chinese README
├── README.en.md                      # English README (this file)
├── scripts/
│   ├── cdp-proxy.mjs                 # CDP Proxy HTTP server
│   ├── check-deps.sh                 # Environment check + auto-start Proxy
│   ├── oa-pdf-download.mjs           # OA PDF manifest generation and download
│   ├── bibtex-export.py              # BibTeX export script
│   ├── self-test.sh                  # Local regression test
│   └── release-test.sh               # Pre-release regression test
├── references/
│   ├── api-cookbook.md               # Multi-platform API call reference
│   ├── metadata-schema.md            # Unified metadata schema
│   ├── venue-rankings.md             # Journal/conference ranking reference
│   ├── cdp-api.md                    # CDP Proxy HTTP API reference
│   ├── impact-factor/                # 372-journal IF table + iikx API cookbook
│   ├── disciplines/                  # Discipline routing profiles
│   ├── rankings/                     # Evidence-level and journal ranking
│   ├── workflows/                    # Systematic review workflows
│   ├── site-patterns/                # Platform and publisher site knowledge
│   └── publisher-pdf-patterns.md     # Publisher PDF direct-link patterns
└── docs/
    ├── skill-usage-comparison.md
    └── multidisciplinary-improvement-analysis.md
```

## Design Principles

> Skill = philosophy + technical facts, not an operations manual. Explain tradeoffs and let the AI decide.

- **Bottleneck is filtering, not searching**: Lightweight summary table first → deep fetch for confirmed core papers
- **Evidence-level first**: Systematic reviews > RCTs > cohort > case reports; engineering validation tier for device papers
- **PubMed-first**: MeSH-controlled vocabulary covers both engineering and clinical dimensions
- **API-first**: Never simulate a browser for platforms that offer a public API
- **IF-ranked output**: Built-in 372-journal IF table supports programmatic iikx.com API batch queries
- **Structured output**: Unified schema, DOI as dedup key, directly exportable as BibTeX

---

## License

MIT · Author: Xuan Du
