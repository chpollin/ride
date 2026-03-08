# RIDE Data Documentation

> All numbers verified against the actual repository on 2026-03-08.

## Repository Overview

| Metric | Verified Value |
|---|---|
| Total Issues | 21 (issue01 through issue21) |
| Total Entries | 111 (107 reviews + 4 editorials) |
| Reviews (non-editorial) | 107 |
| Editorials | 4 (in issues 06, 08, 09, 16) |
| XML files in tei_all/ | 104 (reviews only, editorials excluded) |
| PDFs | 111 files, ~328 MB total |
| Images | 847 files (839 .png + 3 .PNG + 5 .jpg), ~131 MB total |
| XML data | ~13 MB total |
| Total assets (PDF + images + XML) | ~472 MB |
| XML encoding | UTF-8 (all files) |
| ISSN | None (RIDE has no ISSN) |
| License | CC-BY 4.0 |

## Directory Structure

```
ride/
  issues/
    issue01/ through issue21/
      {slug}/
        {slug}-tei.xml          # TEI/XML review
        {slug}.pdf              # PDF version (always present)
        pictures/               # Images (absent in 3 reviews + 1 editorial)
          picture-1.png
          picture-2.png ...
      editorial/                # Only in issues 06, 08, 09, 16
        editorial-tei.xml
        editorial.pdf
        pictures/               # Present in 06, 08, 09 — ABSENT in 16
  tei_all/                      # 104 XMLs (reviews only, no editorials)
  schema/
    ride.odd                    # ODD specification (2,333 lines)
    ride.rng                    # RelaxNG validation schema
  README.md
  .gitignore                    # Ignores *.xpr (Oxygen XML Editor)
```

## Review Count per Issue

| Issue | Reviews | Editorial | Total | Type |
|---|---|---|---|---|
| 01 | 5 | — | 5 | SE |
| 02 | 5 | — | 5 | SE |
| 03 | 5 | — | 5 | SE |
| 04 | 5 | — | 5 | SE |
| 05 | 5 | — | 5 | SE |
| 06 | 10 | 1 | 11 | DTC |
| 07 | 5 | — | 5 | SE |
| 08 | 5 | 1 | 6 | DTC |
| 09 | 5 | 1 | 6 | DTC |
| 10 | 5 | — | 5 | SE |
| 11 | 5 | — | 5 | TE |
| 12 | 5 | — | 5 | SE |
| 13 | 5 | — | 5 | SE |
| 14 | 5 | — | 5 | SE |
| 15 | 7 | — | 7 | TE |
| 16 | 5 | 1 | 6 | SE |
| 17 | 5 | — | 5 | SE |
| 18 | 5 | — | 5 | SE |
| 19 | 4 | — | 4 | TE |
| 20 | 5 | — | 5 | SE |
| 21 | 1 | — | 1 | SE |
| **Total** | **107** | **4** | **111** | |

## Issue Types (3 distinct types)

Determined by the `<biblScope unit="issue">` text in each review's `seriesStmt`.

| Type | Code | Issues | Count |
|---|---|---|---|
| Digital Scholarly Editions | SE | 01, 02, 03, 04, 05, 07, 10, 12, 13, 14, 16, 17, 18, 20, 21 | 15 issues |
| Digital Text Collections | DTC | 06, 08, 09 | 3 issues |
| Tools and Environments | TE | 11, 15, 19 | 3 issues |

**Programmatic detection**: Match against `<biblScope>` text content:
- Contains "Text Collection" → DTC
- Contains "Tool" → TE
- Otherwise → SE

## TEI/XML File Structure

### Root Element
```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="ride.{issue}.{position}">
```
- Editorials: `ride.X.0` (e.g., `ride.6.0`)
- Reviews: `ride.X.N` where N >= 1

### teiHeader

#### titleStmt
- `<title>` — Review title
- `<author ref="https://orcid.org/...">` — Author(s) with:
  - `<name>/<forename>` + `<surname>`
  - `<affiliation>/<orgName>` + `<placeName>`
  - `<email>`

**Multi-author entries** (14 total):
- 10 reviews: wba, litteraturbanken, wba_upgrade, digital-mappa, lakomp, fontane-notebooks, europaeische-religionsfrieden, chatgpt, oxygen-framework, tei-publisher
- 4 editorials: all editorials have 2-3 authors

#### publicationStmt
- `<publisher>` — "Institut für Dokumentologie und Editorik e.V."
- `<date when="YYYY-MM">` — Publication date (text content varies: "June 2014", "Apr 2025", etc.)
- `<idno type="URI">` — Canonical URL
- `<idno type="DOI">` — DOI (e.g., `10.18716/ride.a.20.4`)
- `<idno type="archive">` — GitHub PDF raw URL
- `<availability>/<licence target="..."/>` — CC-BY 4.0

**Known data error**: Issue 21 (everynamecounts) has THREE `<idno type="URI">` elements, two of which erroneously point to `issue-1` instead of `issue-21`. The build must derive URLs from the folder structure, NOT from XML `<idno type="URI">`.

#### seriesStmt
- `<title level="j">` — "RIDE - A review journal for digital editions and resources"
- `<editor>` — Series editors (with ORCID via `ref` attribute)
- `<editor role="managing">` — Managing editors (skip in issue_editors list)
- `<biblScope unit="issue" n="20">Digital Scholarly Editions</biblScope>` — Issue title + number
- `<idno type="DOI">` — Issue DOI

#### notesStmt (reviews only — editorials lack this)
- `<relatedItem type="reviewed_resource">/<bibl>` — Reviewed resource metadata:
  - `<title>`, `<editor>`, multiple `<respStmt>` (role + person)
  - `<date type="publication">`, `<idno type="URI">`, `<date type="accessed">`
  - Tools reviews: `xml:id` on `<relatedItem>` for multi-resource linking
- `<relatedItem type="reviewing_criteria">/<bibl>/<ref>` — Link to criteria used

#### encodingDesc/classDecl/taxonomy (reviews only — editorials lack this)
Contains questionnaire data. Three distinct schemas — see section below.

#### profileDesc
- `<langUsage>/<language ident="de|en">` — Review language
- `<textClass>/<keywords xml:lang="en">/<term>` — Keywords (always English)

#### revisionDesc (optional, not in all files)
- `<change when="YYYY-MM-DD">` — Revision history entries

### text/front (reviews only — editorials lack this)
- `<div type="abstract">/<p>` — Abstract (English, even for German reviews)

### text/body
- `<div xml:id="divN">` — Numbered sections
  - `<head>` — Section heading
  - `<p xml:id="pN">` — Paragraphs with IDs
  - `<figure xml:id="imgN">` — Figures:
    - `<graphic url="...">` — Image URL (WordPress CDN or external)
    - `<head type="legend">` — Caption
  - `<note xml:id="ftnN">` — Inline footnotes (~1,845 total)
  - `<ref target="URL">` — Links; `type="crossref"` = bibliography cross-reference
  - `<emph>` — Emphasis/italic
  - `<code>` — Inline code (~725 occurrences)
  - `<cit>/<quote>` + `<bibl>` — Block quotes (~79 occurrences)
  - `<list rend="bulleted|ordered|numbered|labeled">` — Lists (~111 total)
  - `<table>/<row>/<cell>` — Tables (~12 total); `role="label"` on rows = header
  - `<hi rend="sup|bold|italic|underline|smallcaps|monospace">` — Highlighting
  - `<lb/>` — Line breaks (~376 total)
  - `<foreign xml:lang="...">` — Foreign language spans
  - `<seg>` — Segment (rare)
  - `<lg>/<l>` — Line groups/poetry (rare)

### text/back
- `<div type="bibliography">/<listBibl>/<bibl xml:id="...">` — Bibliography entries with `xml:id` for cross-references

## Three Questionnaire Schemas

### 1. Scholarly Editions (SE) — 15 issues, 80 reviews

- **Identifier**: `xml:base` contains `criteria-version-1-1`
- **URL** (single variant): `http://www.i-d-e.de/publikationen/weitereschriften/criteria-version-1-1`
- **ID pattern**: `se001` through `se220`
- **Sections** (5): Documentation, Contents, Access modes, Aims and methods, Technical accessibility
- **Structure**:
  - Top-level `<category>` (no `xml:id`) = section header, first `<catDesc>` = section name
  - Child `<category xml:id="seNNN">` = question, first `<catDesc>` = label (may include `<ref>` to catalogue), second `<catDesc>` = full question text
  - Grandchild `<category>` = answer option (Yes/No/Not applicable)
    - `<catDesc><num type="boolean" value="0|1"/>` — value="1" means this answer is selected
  - Some questions are multi-select (e.g., document types, subjects, typology) with >3 children
  - "Other" options may have `<catDesc><gloss>free text</gloss></catDesc>`

### 2. Digital Text Collections (DTC) — 3 issues, 20 reviews

- **Identifier**: `xml:base` contains `criteria-text-collections`
- **URL variants** (2 — router must handle both):
  1. `http://www.i-d-e.de/criteria-text-collections-version-1-0` (issue 06)
  2. `https://www.i-d-e.de/publikationen/weitereschriften/criteria-text-collections-version-1-0/` (issues 08, 09)
- **ID pattern**: Named IDs (e.g., `bibl_desc`, `contributors`, `search_simple`)
- **Sections** (8): general_information, aims, content, composition, data_modelling, provision, user_interface, preservation
- **Extra features**: `corresp="#other"` attributes, freetext via `<desc>` elements

### 3. Tools & Environments (TE) — 3 issues, 16 reviews

- **Identifier**: `xml:base` contains `criteria-tools-version-1`
- **URL** (single variant): `https://www.i-d-e.de/publikationen/weitereschriften/criteria-tools-version-1/`
- **ID pattern**: `te`-prefixed with resource prefix (e.g., `rev1-te001`)
- **Multi-resource**: Multiple `<taxonomy m="revN">` per file
  - e.g., collationtools has `m="rev1"`, `m="rev2"`, `m="rev3"` for 3 reviewed tools
- **Sections**: Similar structure to DTC

## Image URL Patterns

### WordPress CDN URLs (in XML `<graphic url="...">`)
```
http(s)://ride.i-d-e.de/wp-content/uploads/issue_X/slug/pictures/picture-N.png
```
- URL uses `issue_1` (no zero-padding) vs local dir `issue01` (zero-padded)
- Mixed `http://` and `https://` usage
- 11 cases in `anemoskala` (issue 08) lack `.png` extension in URL

### Local file paths
```
issues/issueXX/slug/pictures/picture-N.png
```

### Image Edge Cases
| Case | Count | Location | Handling |
|---|---|---|---|
| `.jpg` files | 5 | issue10/ps (1), issue11/tustep (4) | Support in copier + URL rewriter |
| `.PNG` uppercase | 3 | issue09/corlec (2), issue16/tagebuecher-christian-ii (1) | Case-insensitive matching |
| `.docx` in pictures/ | 1 | issue15/transkribus | Skip non-image files |
| Missing extension in URL | 11 | issue08/anemoskala | Filesystem lookup with `.png` fallback |
| Reviews without pictures/ | 3 | issue09/europarl, issue12/sauer-seuffert, issue21/everynamecounts | Handle gracefully |
| Editorials without pictures/ | 1 | issue16/editorial | Handle gracefully |

## DOI Pattern
- Repository: `10.5281/zenodo.4550708`
- Issue: `10.18716/ride.a.{issue_number}`
- Review: `10.18716/ride.a.{issue_number}.{position}`

## WordPress URL Pattern (for redirects)
All reviews follow: `http://ride.i-d-e.de/issues/issue-{N}/{slug-with-hyphens}`

Examples:
- `http://ride.i-d-e.de/issues/issue-1/carolingian-scholarship`
- `http://ride.i-d-e.de/issues/issue-20/anne-frank`

Note: The slug in the URL may differ from the directory name (hyphens vs underscores, different abbreviations). Each review's actual WordPress URL is in `<idno type="URI">` (except issue 21 which is wrong).

## Editorial Structure

| Property | Issues 06, 08, 09 | Issue 16 |
|---|---|---|
| `editorial-tei.xml` | Yes | Yes |
| `editorial.pdf` | Yes | Yes |
| `pictures/` | Yes | **No** |
| `encodingDesc` | No | No |
| `notesStmt` | No | No |
| `front/abstract` | No | No |
| `ride_id` | ride.X.0 | ride.16.0 |
| Multiple authors | Yes (2-3) | Yes (3) |

## Publisher
Institut für Dokumentologie und Editorik e.V. (Institute for Documentology and Scholarly Editing)

## Reference Files for Testing

| File | Purpose |
|---|---|
| `issues/issue01/sandrart/sandrart-tei.xml` | SE baseline, German, first review |
| `issues/issue20/anne-frank/anne-frank-tei.xml` | Recent SE, German, 2025 |
| `issues/issue06/celt/celt-tei.xml` | DTC schema (old URL variant) |
| `issues/issue08/anemoskala/anemoskala-tei.xml` | DTC schema (new URL variant) + extensionless images |
| `issues/issue11/collationtools/collationtools-tei.xml` | TE with 3 reviewed resources |
| `issues/issue19/chatgpt/chatgpt-tei.xml` | TE, recent, multi-author |
| `issues/issue06/editorial/editorial-tei.xml` | Editorial (minimal structure, has pictures) |
| `issues/issue16/editorial/editorial-tei.xml` | Editorial (no pictures) |
| `issues/issue21/everynamecounts/everynamecounts-tei.xml` | Erroneous URI bug |
| `issues/issue05/wba/wba-tei.xml` | SE, multi-author review |
| `schema/ride.odd` | Element definitions for body parser |
