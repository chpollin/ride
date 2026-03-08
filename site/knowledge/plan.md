# RIDE Static Site — Implementation Plan

## Goal
Rebuild the RIDE journal website (ride.i-d-e.de) as a static site generated from TEI/XML data in the GitHub repository. The static site replaces the existing WordPress site entirely and is deployed via GitHub Actions to GitHub Pages.

## Decisions Made
- **Build tool**: Python 3.12 (lxml + Jinja2) — no SSG framework
- **CSS**: Pure Vanilla CSS with custom properties
- **JS**: Vanilla JavaScript, no framework
- **Search**: Pagefind (static, build-time indexing)
- **Interface language**: English
- **Scope**: Complete replacement of ride.i-d-e.de
- **CI/CD**: GitHub Actions → GitHub Pages
- **Fonts**: Self-hosted .woff2 (DSGVO compliance)
- **Custom domain**: `ride.i-d-e.de` via CNAME file in build output

## Scope Numbers
- 21 issues, 107 reviews + 4 editorials = 111 entries
- 3 questionnaire schemas: SE (80 reviews), DTC (20 reviews), TE (16 reviews, multi-resource)
- 847 images (~131 MB), 111 PDFs (~328 MB), ~13 MB XML
- Output estimate: ~440-450 MB (well within GitHub Pages 1 GB limit)

## Implementation Phases

### Phase 1: Core Parsing
Build the Python pipeline to parse TEI/XML into structured data models.

| # | Task | File(s) | Status |
|---|---|---|---|
| 1 | Directory structure + requirements.txt | `site/`, `requirements.txt` | Written |
| 2 | Data models | `models/*.py` | Written |
| 3 | Metadata parser | `parsers/metadata.py` | Written |
| 4 | Body parser (TEI → HTML) | `parsers/body.py` | Written |
| 5 | Image URL rewriter | `parsers/images.py` | Written |
| 6 | Questionnaire parsers (SE, DTC, TE) | `parsers/taxonomy_*.py` | Written |
| 7 | Taxonomy router | `parsers/taxonomy_router.py` | Written |
| 8 | TEI parser orchestrator | `parsers/tei_parser.py` | Written |
| 9 | Citation generators | `parsers/citations.py` | Written |
| 10 | Test Phase 1 against reference files | — | Done (8/8 pass) |

**Phase 1 testing** must cover at minimum:
- `sandrart-tei.xml` (SE baseline, German)
- `anne-frank-tei.xml` (recent SE)
- `celt-tei.xml` (DTC, old URL variant)
- `anemoskala-tei.xml` (DTC, new URL variant, extensionless images)
- `collationtools-tei.xml` (TE, 3 reviewed resources)
- `editorial-tei.xml` from issue 06 (editorial with pictures)
- `editorial-tei.xml` from issue 16 (editorial without pictures)
- `everynamecounts-tei.xml` (erroneous URI)

### Phase 2: Templates + CSS
Create all HTML templates and the CSS design system.

| # | Task | File(s) | Status |
|---|---|---|---|
| 11 | Base template (nav, footer) | `templates/base.html`, `components/nav.html`, `components/footer.html` | Written |
| 12 | Review template | `templates/review.html`, `components/review_sidebar.html`, `components/review_meta.html` | Written |
| 13 | Factsheet template | `templates/factsheet.html`, `components/factsheet_section.html` | Written |
| 14 | Listing templates | `templates/homepage.html`, `issues_list.html`, `issue_single.html`, `reviewers.html`, `data_overview.html`, `about.html`, `search.html` | Written |
| 15 | Review card component | `components/review_card.html` | Written |
| 16 | Citation box component | `components/citation_box.html` | Written |
| 17 | Main CSS (design tokens, layout, responsive) | `static/css/main.css` | Written |
| 18 | Review CSS | `static/css/review.css` | Written |
| 19 | Factsheet CSS | `static/css/factsheet.css` | Written |
| 20 | Print CSS | `static/css/print.css` | Written |

### Phase 3: Generators + Build
Implement page generators and the build orchestrator.

| # | Task | File(s) | Status |
|---|---|---|---|
| 21 | Base generator (Jinja2 env, filters, render helper) | `generators/base.py` | Pending |
| 22 | Build orchestrator (discover, parse, derive, generate) | `build.py` | Pending |
| 23 | Review generator (+ copy PDF/images/XML) | `generators/reviews.py` | Pending |
| 24 | Factsheet generator (skip editorials) | `generators/factsheets.py` | Pending |
| 25 | Issue generators (list + single pages) | `generators/issues.py` | Pending |
| 26 | Homepage generator | `generators/homepage.py` | Pending |
| 27 | Reviewer generator | `generators/reviewers.py` | Pending |
| 28 | Data/charts generator (aggregate questionnaire data) | `generators/data.py` | Pending |
| 29 | About generator (Markdown → HTML) | `generators/about.py` | Pending |
| 30 | Search generator (Pagefind UI shell) | `generators/search.py` | Pending |
| 31 | Sitemap generator | `generators/sitemap.py` | Pending |
| 32 | Redirect generator (WordPress URL stubs) | `generators/redirects.py` | Pending |

### Phase 4: Interactivity (JavaScript)
Add client-side interactivity.

| # | Task | File(s) | Status |
|---|---|---|---|
| 33 | TOC scroll spy + progress bar | `static/js/toc.js` | Pending |
| 34 | Footnote popovers | `static/js/footnotes.js` | Pending |
| 35 | Image lightbox | `static/js/lightbox.js` | Pending |
| 36 | Dark/light mode toggle | `static/js/theme.js` | Pending |
| 37 | Data page charts | `static/js/charts.js` | Pending |

### Phase 5: CI/CD + Content
Set up automation and static content.

| # | Task | File(s) | Status |
|---|---|---|---|
| 38 | GitHub Actions workflow | `.github/workflows/build-deploy.yml` | Pending |
| 39 | Self-host fonts (download .woff2) | `static/fonts/*.woff2` | Pending |
| 40 | About page content (placeholder for editors) | `content/*.md` | Pending |
| 41 | RIDE logo SVG | `static/img/ride-logo.svg` | Pending |

**Content note**: The `content/*.md` files (about, editorial board, publishing policy, ethical code, contact, reviewing criteria) must ultimately be authored by the RIDE editors. We create placeholder files with structure and existing text extracted from the WordPress site where possible.

### Phase 6: Integration Testing + Polish

| # | Task | Status |
|---|---|---|
| 42 | Full build (all 111 entries, expect 0 errors) | Pending |
| 43 | Spot-check: SE review rendering (sandrart, anne-frank) | Pending |
| 44 | Spot-check: DTC review rendering (celt, anemoskala) | Pending |
| 45 | Spot-check: TE review rendering (collationtools) | Pending |
| 46 | Spot-check: editorial rendering (issue 06, issue 16) | Pending |
| 47 | Factsheet rendering for all 3 schema types | Pending |
| 48 | Search functionality (Pagefind) | Pending |
| 49 | Responsive testing (375px / 768px / 1280px) | Pending |
| 50 | Accessibility (ARIA, keyboard nav, contrast) | Pending |
| 51 | Performance (lazy loading images, minimal JS) | Pending |
| 52 | Cross-browser (Chrome, Firefox, Safari) | Pending |
| 53 | GitHub Actions: end-to-end build + deploy | Pending |

## Edge Cases

| Case | Count | Details | Solution |
|---|---|---|---|
| Editorials | 4 | No encodingDesc, no abstract, `ride.X.0` | Skip factsheet, handle None for all optional fields |
| Multi-resource TE reviews | varies | Multiple `<taxonomy m="revN">` per file | Sectioned factsheet (one per resource) |
| Missing image extensions | 11 | URLs in `anemoskala` lack `.png` | Filesystem lookup with `.png` fallback |
| Uppercase `.PNG` | 3 | `corlec` (2), `tagebuecher-christian-ii` (1) | Case-insensitive matching |
| `.jpg` images | 5 | `ps` (1), `tustep` (4) | Support in copier + URL rewriter |
| `.docx` in pictures/ | 1 | `transkribus` | Skip non-image files |
| Reviews without pictures/ | 3 | `europarl`, `sauer-seuffert`, `everynamecounts` | Handle empty/missing directory gracefully |
| Editorial without pictures/ | 1 | issue 16 editorial | Handle gracefully |
| German reviews | majority | Most reviews are in German | `<html lang="de">` on article, UI stays English |
| Erroneous URI in XML | 1 | issue 21 has `<idno type="URI">` pointing to issue-1 | Derive URLs from folder structure, never trust XML URIs |
| Multi-author entries | 14 | 10 reviews + 4 editorials | Already handled in metadata parser |
| DTC taxonomy URL variants | 2 | Issue 06 vs issues 08/09 use different URL paths | Router handles both via `text-collection` substring match |

## Verification Checklist

- [ ] `python site/build.py --output _site` completes with 0 errors on all 111 entries
- [ ] `_site/reviews/sandrart/index.html` renders correctly (text, images, footnotes, TOC)
- [ ] All 107 reviews + 4 editorials generate valid HTML
- [ ] Images load from local paths (no broken images)
- [ ] All 111 PDFs downloadable
- [ ] Factsheets render correctly for SE, DTC, and TE reviews
- [ ] TE factsheets show multiple resources (collationtools)
- [ ] No factsheet generated for editorials
- [ ] Pagefind returns results for "Anne Frank", "TEI", "Sahle"
- [ ] Mobile layout correct at 375px
- [ ] Dark mode toggle works and persists
- [ ] Footnote popovers appear on desktop
- [ ] Image lightbox opens/closes with keyboard support
- [ ] WordPress redirect stubs resolve correctly
- [ ] `_site/CNAME` contains `ride.i-d-e.de`
- [ ] GitHub Actions workflow builds and deploys successfully
- [ ] Total `_site/` size < 1 GB
