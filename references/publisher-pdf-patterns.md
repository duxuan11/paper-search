# Publisher-Specific PDF Download Patterns

> Supplemental to `paper-search` PDF/全文获取 section. When the standard OA pipeline (PMC → Europe PMC → Unpaywall) fails, try these publisher-specific patterns.

## Nature / Nature Communications (Open Access)

When the paper is OA (confirmed via Europe PMC `isOpenAccess: Y`), the direct PDF URL works with proper headers even when Sci-Hub doesn't have it:

```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept: application/pdf" \
  -o output.pdf \
  -w "HTTP %{http_code} Size: %{size_download}" \
  "https://www.nature.com/articles/{doi}.pdf"
```

Without the `User-Agent` header, Nature redirects to `idp.nature.com/authorize` (auth wall). Without `Accept: application/pdf`, it may return HTML.

**Verified**: 10.1038/s41467-023-43090-9 (2023, 14 pages, 6.5MB) downloaded successfully via this pattern after:
- scansci-pdf MCP: "no PDF found" (all strategies)
- Sci-Hub (.st, .ru): "article not available"
- PMC curl: reCAPTCHA block
- Browser navigate to nature.com: timeout

## PubMed Central (PMC) ReCAPTCHA Pitfall

PMC PDF URLs are discoverable via the article page (`citation_pdf_url` meta tag), but direct `curl` requests to `pmc.ncbi.nlm.nih.gov/articles/PMC{id}/pdf/` may return Google reCAPTCHA challenge pages instead of PDFs. When this happens:

1. Extract the PDF URL from the PMC page metadata (it works as a URL reference)
2. Try downloading with the same User-Agent header pattern as Nature
3. If still blocked, fall back to publisher direct download

## Europe PMC API — Reliable PMCID Discovery

When you have a DOI but need the PMCID:

```bash
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{doi}&format=json" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); r=d['resultList']['result'][0]; print(f'PMCID: {r.get(\"pmcid\")}'); print(f'isOpenAccess: {r.get(\"isOpenAccess\")}'); print(f'hasPDF: {r.get(\"hasPDF\")}')"
```

Europe PMC is more reliable than the PMC website itself for metadata — it returns JSON API responses without reCAPTCHA.

## Decision Flow

```
DOI known
  │
  ├── Europe PMC API → PMCID + isOpenAccess?
  │     ├── isOpenAccess: Y → try publisher direct (Nature/Springer/etc.)
  │     └── isOpenAccess: N → try Unpaywall → scansci-pdf or inform user
  │
  └── scansci-pdf MCP (scansci_pdf_download)
        ├── Success → done
        └── "no PDF found" → try above pipeline
```

Last verified: 2026-06-15 (Nature Communications OA paper)
