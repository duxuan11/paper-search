#!/usr/bin/env python3
"""
bibtex-export.py — Batch PubMed efetch → BibTeX converter

Usage:
  python3 scripts/bibtex-export.py --pmids 37704762,39567792
  python3 scripts/bibtex-export.py --pmids 37704762,39567792 --with-abstracts

Takes one or more PMIDs, fetches full XML from PubMed, and outputs
BibTeX @article entries (optionally with truncated abstracts).

No external dependencies — Python stdlib only (xml.etree + urllib).
"""

import sys, os, urllib.request, xml.etree.ElementTree as ET

PUBMED_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def sanitize(text: str) -> str:
    """Escape BibTeX special characters."""
    if not text:
        return ""
    text = text.replace('\\', '\\\\')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    text = text.replace('$', '\\$')
    text = text.replace('&', '\\&')
    text = text.replace('%', '\\%')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    text = text.replace('^', '\\^{}')
    text = text.replace('~', '\\textasciitilde{}')
    return text

def make_bibtex_key(first_author: str, year: str, journal: str) -> str:
    """Generate a BibTeX key: FirstAuthorYearJournalAbbr."""
    last = first_author.split(",")[0].strip() if "," in first_author else first_author.split()[-1]
    # Short journal name: take first word, remove special chars
    j_short = journal.split()[0].replace("&", "").replace("-", "") if journal else ""
    return f"{last}{year}{j_short}"

def fetch_pmids(pmids: list, api_key: str = None) -> bytes:
    """Fetch PubMed XML for a list of PMIDs."""
    params = [
        ("db", "pubmed"),
        ("id", ",".join(pmids)),
        ("retmode", "xml"),
    ]
    if api_key:
        params.append(("api_key", api_key))
    url = PUBMED_EFETCH + "?" + "&".join(f"{k}={urllib.request.quote(str(v))}" for k, v in params)
    req = urllib.request.Request(url, headers={"User-Agent": "bibtex-export/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read()

def extract_bibtex(xml_bytes: bytes, with_abstracts: bool = False) -> str:
    """Parse PubMed XML and return formatted output."""
    tree = ET.parse(io.BytesIO(xml_bytes))
    root = tree.getroot()
    output_parts = []

    for article in root.findall('.//PubmedArticle'):
        pmid = article.find('.//PMID')
        pmid = pmid.text if pmid is not None else ""

        # Title
        title_el = article.find('.//ArticleTitle')
        title = sanitize(title_el.text) if title_el is not None and title_el.text else ""

        # Abstract
        abstract = ""
        if with_abstracts:
            abstract_parts = article.findall('.//AbstractText')
            if abstract_parts:
                abstract = " ".join(a.text or "" for a in abstract_parts)
                abstract = sanitize(abstract[:500])

        # Authors (BibTeX format: Last, First and Last, First)
        authors = []
        for author in article.findall('.//Author'):
            last = author.find('LastName')
            fore = author.find('ForeName')
            if last is not None and fore is not None:
                authors.append(f"{last.text}, {fore.text}")
        authors_str = " and ".join(authors)

        if not authors:
            authors_str = ""

        # Journal
        journal_el = article.find('.//Journal/Title')
        journal = sanitize(journal_el.text) if journal_el is not None and journal_el.text else ""

        # Year
        year_el = article.find('.//PubDate/Year')
        year = year_el.text if year_el is not None else ""

        # Volume / Issue / Pages
        vol_el = article.find('.//Journal/JournalIssue/Volume')
        volume = vol_el.text if vol_el is not None else ""
        iss_el = article.find('.//Journal/JournalIssue/Issue')
        issue = iss_el.text if iss_el is not None else ""
        pag_el = article.find('.//Pagination/MedlinePgn')
        pages = pag_el.text if pag_el is not None else ""

        # DOI
        doi_el = article.find('.//ArticleId[@IdType="doi"]')
        doi = doi_el.text if doi_el is not None else ""

        # Key
        first_author = authors[0] if authors else ""
        key = make_bibtex_key(first_author, year, journal)

        # Build output
        parts = []
        if with_abstracts and abstract:
            parts.append(f"PMID: {pmid}")
            parts.append(f"ABSTRACT: {abstract}")
            parts.append("")

        parts.append(f"@article{{{key},")
        if authors_str:
            parts.append(f"  author    = {{{authors_str}}},")
        parts.append(f"  title     = {{{title}}},")
        parts.append(f"  journal   = {{{journal}}},")
        parts.append(f"  year      = {{{year}}},")
        if volume:
            parts.append(f"  volume    = {{{volume}}},")
        if issue:
            parts.append(f"  number    = {{{issue}}},")
        if pages:
            parts.append(f"  pages     = {{{pages}}},")
        if doi:
            parts.append(f"  doi       = {{{doi}}}")
        else:
            # Remove trailing comma from the last real field
            if parts[-1].endswith(","):
                parts[-1] = parts[-1][:-1]
        parts.append("}")
        parts.append("")

        output_parts.append("\n".join(parts))

    return "\n".join(output_parts)

def main():
    import io  # for BytesIO

    if "--help" in sys.argv or len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    pmids_arg = None
    with_abstracts = "--with-abstracts" in sys.argv
    api_key = None

    for i, arg in enumerate(sys.argv):
        if arg == "--pmids" and i + 1 < len(sys.argv):
            pmids_arg = sys.argv[i + 1]
        if arg == "--api-key" and i + 1 < len(sys.argv):
            api_key = sys.argv[i + 1]

    if not pmids_arg:
        print("ERROR: --pmids is required", file=sys.stderr)
        sys.exit(1)

    # Auto-resolve API key from environment
    if not api_key:
        for env_name in ("NCBI_API_KEY", "EUTILS_API_KEY", "API_KEY"):
            if os.environ.get(env_name):
                api_key = os.environ[env_name]
                break

    pmids = [p.strip() for p in pmids_arg.split(",") if p.strip()]
    xml = fetch_pmids(pmids, api_key)
    result = extract_bibtex(xml, with_abstracts)
    print(result)

if __name__ == "__main__":
    main()
