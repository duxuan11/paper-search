# Biomedical Engineering Discipline Profile

## Use When

Default discipline for paper-search v2.0. Use for biomedical engineering topics (medical devices, tissue engineering, organ-on-a-chip, microfluidics, biomaterials, neural engineering, medical imaging, biosensors, biomechanics, drug delivery, wearable devices, AI-assisted diagnosis, surgical robotics), and any clinical-engineering crossover.

## Platform Route

| Need | Preferred Sources | Priority |
|------|-------------------|----------|
| **Biomedical engineering search** | **PubMed** | 🥇 default |
| Preprints (latest BME research) | bioRxiv, medRxiv, engrXiv | 🥈 |
| Full text OA | PubMed Central, Europe PMC, Unpaywall | — |
| Clinical trials | ClinicalTrials.gov | — |
| Medical devices / imaging engineering | IEEE Xplore, SPIE Digital Library | 🥉 |
| Citation counts / author info | Semantic Scholar | — |
| DOI / publisher metadata | Crossref | — |
| Cross-disciplinary supplement | OpenAlex | — |
| Chinese BME literature | CNKI (CDP must) | — |

## Query Expansion — Biomedical Engineering

### Step 1: Identify BME Subfield

| Subfield | Chinese Keywords | English / MeSH Terms |
|----------|-----------------|----------------------|
| Tissue Engineering | 组织工程 | `"Tissue Engineering"[MeSH]`, `"Tissue Scaffolds"[MeSH]` |
| Organ-on-a-Chip | 器官芯片 | `"Lab-On-A-Chip Devices"[MeSH]`, `"Microphysiological Systems"[MeSH]` |
| Microfluidics | 微流控 | `"Microfluidics"[MeSH]`, `"Microfluidic Analytical Techniques"[MeSH]` |
| Biomaterials | 生物材料 | `"Biocompatible Materials"[MeSH]`, `"Biomimetic Materials"[MeSH]` |
| Neural Engineering | 神经工程 | `"Brain-Computer Interfaces"[MeSH]`, `"Deep Brain Stimulation"[MeSH]` |
| Medical Imaging | 医学影像 | `"Diagnostic Imaging"[MeSH]`, MRI/CT/Ultrasound/PET specific MeSH |
| Medical Devices | 医疗器械 | `"Equipment and Supplies"[MeSH]`, `"Prostheses and Implants"[MeSH]` |
| Biosensors | 生物传感器 | `"Biosensing Techniques"[MeSH]`, `"Wearable Electronic Devices"[MeSH]` |
| Drug Delivery | 药物递送 | `"Drug Delivery Systems"[MeSH]`, `"Nanoparticles"[MeSH]` |
| Surgical Robotics | 手术机器人 | `"Robotic Surgical Procedures"[MeSH]`, `"Surgery, Computer-Assisted"[MeSH]` |
| AI in Medicine | AI辅助诊断 | `"Artificial Intelligence"[MeSH]` + `"Diagnosis, Computer-Assisted"[MeSH]` |
| Biomechanics | 生物力学 | `"Biomechanical Phenomena"[MeSH]`, `"Mechanical Phenomena"[MeSH]` |

### Step 2: Cross-domain Query Pattern

Biomedical engineering is inherently cross-disciplinary. Always expand queries to cover both engineering and clinical aspects:

```bash
# Pattern A: Engineering + Clinical (AND)
"Tissue Engineering"[MeSH] AND "bioprinting"[Title/Abstract] AND "vascularization"[Title/Abstract]

# Pattern B: Technology + Application
"Lab-On-A-Chip Devices"[MeSH] AND ("drug development"[Title/Abstract] OR "toxicity testing"[Title/Abstract])

# Pattern C: Disease + Technology Intervention
"myocardial infarction"[MeSH] AND "cardiac patch"[Title/Abstract] AND "tissue engineering"[MeSH]

# Pattern D: Material + Biological Response
"Biocompatible Materials"[MeSH] AND ("osteogenesis"[MeSH] OR "bone regeneration"[MeSH])
```

### Step 3: Filter by Publication Type

```bash
# Clinical studies only
query + "Clinical Trial"[pt]

# Reviews (systematic reviews, meta-analyses)
query + "Review"[pt] OR "Systematic Review"[pt] OR "Meta-Analysis"[pt]

# Latest research (original articles)
query + "Journal Article"[pt] NOT "Review"[pt]

# Preprints — search bioRxiv/medRxiv separately
```

## Ranking

Read `references/rankings/biomed-evidence-ranking.md` first. For biomedical engineering, apply two-dimensional ranking:

| Priority | Clinical Evidence | Engineering Validation |
|----------|------------------|----------------------|
| 1 | Systematic reviews / meta-analyses | Validated device/system (preclinical + clinical data) |
| 2 | RCTs (randomized controlled trials) | Prototype with in vivo validation |
| 3 | Cohort / case-control studies | Prototype with in vitro validation |
| 4 | Case series / reports | Computational model / simulation |
| 5 | Narrative reviews | Concept paper / proof of concept |
| 6 | Preprints | Preprints |

- Clinical evidence takes priority for therapeutic/interventional topics.
- Engineering validation takes priority for device/materials topics.
- When both dimensions exist, clinical evidence dominates the sorting weight.

## Output Fields

Required for BME papers:
- `pubmed_id` — PubMed ID
- `pmcid` — PubMed Central ID (if OA)
- `doi`
- `publication_type` — journal article / review / clinical trial / preprint
- `study_type` — RCT / cohort / case-control / in vitro / in vivo / computational
- `sample_size` — if clinical
- `population` / `model_system` — human / animal model / cell line
- `mesh_terms` — MeSH headings
- `bme_subfield` — mapped from Step 1 subfield table
- `technology_readiness_level` — estimated TRL 1-9 if inferable
- `full_text_status`

## Safety Boundary

Do not interpret clinical data as medical advice. For implantable devices, surgical procedures, or drug delivery systems, note regulatory approval status (FDA 510(k) / PMA, CE marking, NMPA) when inferable from metadata or abstract. Flag preclinical-only results explicitly.
