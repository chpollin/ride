# RIDE Static Site — Architecture

## Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Build | Python 3.12 (lxml + Jinja2) | Excellent XML parsing, flexible templating |
| CSS | Vanilla CSS (custom properties) | Full control, no framework overhead |
| JS | Vanilla JavaScript (ES modules) | No build step needed, minimal bundle |
| Search | Pagefind | Static build-time indexing, no backend |
| CI/CD | GitHub Actions | Integrated with repo, free for public repos |
| Hosting | GitHub Pages | Free, custom domain support, CDN |
| Input | TEI/XML from `issues/` | Existing data, unchanged |
| Output | Static HTML in `_site/` | Gitignored, rebuilt on every push |

**Dependencies** (`requirements.txt`):
```
lxml>=5.0
Jinja2>=3.1
MarkupSafe>=2.1
markdown>=3.5
```

No JavaScript build tools. No bundler. No Node.js in development (only in CI for Pagefind).

## Source Code Structure

```
site/
  build.py                    # Entry point — orchestrates full build
  requirements.txt

  models/                     # Dataclasses — pure data, no I/O
    __init__.py
    author.py                 # Author(forename, surname, orcid, affiliation, ...)
    questionnaire.py          # Questionnaire, QuestionnaireSection, QuestionnaireItem
    issue.py                  # Issue(number, title, type, reviews)
    review.py                 # Review, ReviewedResource, Section, Footnote, Revision

  parsers/                    # XML → Model transformation
    __init__.py
    tei_parser.py             # Orchestrator: XML file → Review model
    metadata.py               # teiHeader → dict of Review fields
    body.py                   # TEI body → HTML (recursive element walker)
    images.py                 # WordPress CDN URL → local path rewriter
    taxonomy_router.py        # Detects SE/DTC/TE → dispatches to correct parser
    taxonomy_se.py            # Scholarly Editions questionnaire (se001-se220)
    taxonomy_dtc.py           # Digital Text Collections questionnaire
    taxonomy_te.py            # Tools & Environments questionnaire (multi-resource)
    citations.py              # Citation generators (BibTeX, RIS, APA, MLA, Chicago)

  generators/                 # Model → HTML page generation
    __init__.py
    base.py                   # PageGenerator base class
    homepage.py               # /
    issues.py                 # /issues/ + /issues/issue-N/
    reviews.py                # /reviews/{slug}/ + copies PDFs/images/XML
    factsheets.py             # /reviews/{slug}/factsheet/
    data.py                   # /data/ — aggregated charts
    reviewers.py              # /reviewers/
    about.py                  # /about/*
    search.py                 # /search/ — Pagefind UI shell
    sitemap.py                # /sitemap.xml
    redirects.py              # WordPress URL redirect stubs

  templates/
    base.html                 # Master layout: head, nav, footer, scripts
    homepage.html
    issues_list.html
    issue_single.html
    review.html               # Most complex: sidebar, TOC, meta, body, bib
    factsheet.html
    data_overview.html
    reviewers.html
    about.html
    search.html
    components/
      nav.html
      footer.html
      review_sidebar.html     # TOC + meta panel (sticky)
      review_meta.html        # Published date, DOI, downloads
      citation_box.html       # Copy-to-clipboard citation formats
      factsheet_section.html  # Reusable questionnaire section
      review_card.html        # Review card for listings

  static/                     # Copied as-is to _site/
    css/
      main.css                # Design tokens, layout, typography, responsive
      review.css              # Article-specific styles
      factsheet.css           # Factsheet visualization
      print.css               # Print stylesheet
    js/
      toc.js                  # Scroll spy + reading progress
      footnotes.js            # Footnote popovers
      lightbox.js             # Image zoom overlay
      theme.js                # Dark/light mode toggle
      charts.js               # Chart rendering for data page
    fonts/                    # Self-hosted Google Fonts (DSGVO compliance)
      SourceSerif4-*.woff2
      SourceSans3-*.woff2
      SourceCodePro-*.woff2
    img/
      ride-logo.svg

  content/                    # Static page content (Markdown)
    about.md                  # Must be authored by editors
    editorial-board.md
    publishing-policy.md
    ethical-code.md
    contact.md
    reviewing-criteria.md

  knowledge/                  # Project documentation (this directory)
    data.md
    architecture.md
    design.md
    plan.md
```

## Output Structure (_site/)

```
_site/
  index.html                          # Homepage
  .nojekyll                           # Disable Jekyll on GitHub Pages
  CNAME                               # Custom domain (written by build.py)
  robots.txt
  sitemap.xml

  issues/
    index.html                        # All issues overview
    issue-1/ ... issue-21/
      index.html                      # Single issue page

  reviews/
    {slug}/
      index.html                      # Full review article
      factsheet/
        index.html                    # Questionnaire factsheet (not for editorials)
      pictures/
        picture-1.png ...             # Copied from source
      {slug}.pdf                      # Copied from source
      {slug}-tei.xml                  # Copied for download

  data/
    index.html                        # Aggregated charts page

  reviewers/
    index.html

  about/
    index.html
    editorial-board/index.html
    publishing-policy/index.html
    ethical-code/index.html
    contact/index.html
    reviewing-criteria/index.html

  search/
    index.html                        # Pagefind UI

  pagefind/                           # Generated by Pagefind CLI
    pagefind.js, pagefind-ui.js, ...

  css/ js/ fonts/                     # Copied from static/
```

**tei_all/ is NOT used by the build.** The build reads directly from `issues/issueNN/slug/slug-tei.xml`. tei_all/ is a convenience copy maintained by the editors and is excluded from the output.

## Data Flow

```
TEI/XML files (issues/issueNN/slug/slug-tei.xml)
    │
    ▼
  TEIParser (parsers/tei_parser.py)
    ├── metadata.py → Author, ReviewedResource, Revision
    ├── body.py → Section[], Footnote[], bibliography HTML
    ├── taxonomy_router.py → Questionnaire[]
    │     ├── taxonomy_se.py  (SE: 80 reviews in 15 issues)
    │     ├── taxonomy_dtc.py (DTC: 20 reviews in 3 issues)
    │     └── taxonomy_te.py  (TE: 16 reviews in 3 issues, multi-resource)
    └── images.py → rewrite WordPress CDN URLs to local paths
    │
    ▼
  Review models (107 reviews + 4 editorials)
    │
    ▼
  build.py orchestrator
    ├── Group reviews by issue → 21 Issue models
    ├── Extract unique reviewers → Author list
    ├── Aggregate questionnaire data → chart data
    │
    ▼
  Page Generators (generators/)
    ├── homepage.py    → /index.html
    ├── issues.py      → /issues/*, /issues/issue-N/
    ├── reviews.py     → /reviews/{slug}/ + copy PDF/images/XML
    ├── factsheets.py  → /reviews/{slug}/factsheet/ (skip editorials)
    ├── data.py        → /data/
    ├── reviewers.py   → /reviewers/
    ├── about.py       → /about/*
    ├── search.py      → /search/
    ├── sitemap.py     → /sitemap.xml
    └── redirects.py   → old WordPress URL stubs
    │
    ▼
  _site/ (~472 MB: HTML + CSS + JS + images + PDFs)
    │
    ▼
  Pagefind CLI (indexes reviews/*/index.html only)
    │
    ▼
  GitHub Pages deployment
```

## Build Pipeline (build.py)

```python
def main(output_dir, site_url):
    # 1. DISCOVER — Walk issues/issueNN/slug/slug-tei.xml
    sources = discover_reviews(REPO_ROOT / "issues")
    # → list of (xml_path, issue_number, slug)

    # 2. PARSE — TEIParser for each XML → Review model
    reviews = []
    errors = []
    for src in sources:
        try:
            review = TEIParser(src.xml_path, src.issue_number).parse()
            reviews.append(review)
        except Exception as e:
            errors.append((src.slug, e))
            print(f"WARNING: Failed to parse {src.slug}: {e}")
    # Continue with successfully parsed reviews

    # 3. DERIVE — Build secondary data structures
    issues = group_by_issue(reviews)
    reviewers = extract_unique_reviewers(reviews)
    chart_data = aggregate_questionnaire_data(reviews)

    # 4. CLEAN — Remove old _site/
    clean_output(output_dir)

    # 5. COPY STATIC — CSS, JS, fonts from static/
    copy_static(STATIC_DIR, output_dir)

    # 6. GENERATE — All page generators
    # (each generator writes to output_dir)

    # 7. WRITE META — .nojekyll, CNAME, robots.txt
    (output_dir / ".nojekyll").touch()
    (output_dir / "CNAME").write_text("ride.i-d-e.de")

    # 8. REPORT
    print(f"Built {len(reviews)} entries ({len(errors)} errors)")
    if errors:
        for slug, err in errors:
            print(f"  FAILED: {slug} — {err}")
```

### Error Handling Strategy
- **Parse errors**: Log warning, skip the broken review, continue with the rest. The build does NOT abort on a single bad XML file.
- **Missing files**: Reviews without `pictures/` or without PDF are handled gracefully (empty lists, no download link).
- **Build summary**: Always print count of successes and failures at the end.

### Local Development
```bash
# Install dependencies
pip install -r site/requirements.txt

# Run build
python site/build.py --output _site

# Serve locally (Python built-in server)
python -m http.server 8000 --directory _site

# Open http://localhost:8000
```

## Key Design Patterns

### Parser: Recursive Element Walker
`body.py` walks the TEI DOM tree recursively. Each TEI element maps to an HTML handler:
- Block: `<div>` → `<section>`, `<p>` → `<p>`, `<figure>` → `<figure>`, `<table>` → `<table>`, `<list>` → `<ul>/<ol>/<dl>`
- Inline: `<emph>` → `<em>`, `<ref>` → `<a>`, `<hi>` → `<sup>/<strong>/<em>/etc.`, `<code>` → `<code>`
- Special: `<note>` → extracted to footnotes list, replaced with `<sup>` marker in-place

### Taxonomy Router
`taxonomy_router.py` inspects `xml:base` to detect the schema type. Must handle:
- SE: `criteria-version-1-1` (one URL variant)
- DTC: `criteria-text-collections` (two URL variants — different host paths!)
- TE: `criteria-tools-version-1` (one URL variant)

All three parsers output the same `Questionnaire` model.

### Generator Base Class
All generators inherit from `PageGenerator`:
- `render(template_name, output_path, **context)` — loads template, renders, writes file
- Jinja2 environment with custom filters (`striptags`, `format_date`, `slugify`, `doi_url`)
- Global context: `site_name`, `site_url`, `current_year`

### Jinja2 Template Inheritance
```
base.html
  ├── homepage.html
  ├── issues_list.html
  ├── issue_single.html
  ├── review.html         → includes: review_sidebar, review_meta, citation_box
  ├── factsheet.html      → includes: factsheet_section
  ├── data_overview.html
  ├── reviewers.html
  ├── about.html
  └── search.html
```

## GitHub Actions Workflow

```yaml
Trigger: push to master OR workflow_dispatch (manual)
Steps:
  1. Sparse checkout (issues/, schema/, site/ — avoids 1.7GB full clone)
  2. Python 3.12 setup with pip cache
  3. Install dependencies from site/requirements.txt
  4. Run build.py → _site/
  5. Optimize PNGs with oxipng (lossless, ~30-50% size reduction)
  6. Run Pagefind indexer on reviews/*/index.html
  7. Upload _site/ as Pages artifact
  8. Deploy to GitHub Pages environment
```

## Size Budget

| Content | Files | Measured Size |
|---|---|---|
| PDFs | 111 | 328 MB |
| Images (before optimization) | 847 | 131 MB |
| Images (after oxipng, estimate) | 847 | ~90-100 MB |
| Generated HTML | ~250 | ~15 MB |
| CSS + JS + fonts | — | ~1 MB |
| Pagefind index | — | ~2 MB |
| **Total (optimized estimate)** | | **~440-450 MB** |

Comfortably within the GitHub Pages 1 GB limit. No fallback needed.

## Custom Domain

The build writes `_site/CNAME` with content `ride.i-d-e.de`. DNS must be configured by the repository owner to point `ride.i-d-e.de` to GitHub Pages (CNAME record to `i-d-e.github.io` or A records to GitHub's IPs).
