# RIDE Static Site — Design System

## Design Philosophy
- Modern, clean, professional academic journal
- Readability-first for long-form scholarly text
- Responsive (mobile-first)
- Accessible (WCAG 2.1 AA)
- Minimal, purposeful interactivity (no unnecessary animations)

## Color Palette

### Light Mode
| Token | Value | Usage |
|---|---|---|
| `--color-bg` | `#ffffff` | Page background |
| `--color-bg-secondary` | `#f8f9fa` | Cards, sidebar, code blocks |
| `--color-bg-tertiary` | `#e9ecef` | Hover states, borders, factsheet bars |
| `--color-text` | `#212529` | Primary text |
| `--color-text-secondary` | `#495057` | Secondary text, captions |
| `--color-text-muted` | `#6c757d` | Meta info, dates |
| `--color-primary` | `#1a5276` | Deep academic blue — headings, nav |
| `--color-primary-light` | `#2980b9` | Links, active states |
| `--color-accent` | `#c0392b` | Scholarly red — footnote markers, alerts |
| `--color-border` | `#dee2e6` | Subtle borders |
| `--color-code-bg` | `#f4f4f4` | Inline code background |

### Dark Mode
| Token | Value | Usage |
|---|---|---|
| `--color-bg` | `#1a1a2e` | Page background |
| `--color-bg-secondary` | `#16213e` | Cards, sidebar |
| `--color-bg-tertiary` | `#0f3460` | Hover, borders |
| `--color-text` | `#e0e0e0` | Primary text |
| `--color-text-secondary` | `#b0b0b0` | Secondary text |
| `--color-text-muted` | `#808080` | Meta info |
| `--color-primary` | `#5dade2` | Links, headings |
| `--color-primary-light` | `#85c1e9` | Active states |
| `--color-accent` | `#e74c3c` | Footnotes, alerts |
| `--color-border` | `#333355` | Borders |
| `--color-code-bg` | `#1e1e3a` | Code background |

### Factsheet Indicators
| Indicator | Color | Meaning |
|---|---|---|
| `--color-yes` | `#27ae60` | Green — criterion met |
| `--color-no` | `#e74c3c` | Red — criterion not met |
| `--color-na` | `#95a5a6` | Gray — not applicable |

## Typography

### Font Stack
| Role | Font | Fallback | Size |
|---|---|---|---|
| Body text | Source Serif 4 | Georgia, serif | 1.125rem (18px) |
| Headings | Source Sans 3 | Helvetica Neue, sans-serif | varies |
| Code | Source Code Pro | Courier New, monospace | 0.9rem |

**Font loading**: Self-hosted `.woff2` files in `static/fonts/`. No external requests to Google Fonts (DSGVO compliance for a German-based journal). Required weights:
- Source Serif 4: 400 (regular), 400 italic, 600 (semibold), 700 (bold)
- Source Sans 3: 400, 500, 600, 700
- Source Code Pro: 400

### Type Scale
| Element | Size | Weight | Line Height |
|---|---|---|---|
| Body `<p>` | 1.125rem | 400 | 1.75 |
| H1 (page title) | 2rem | 700 | 1.3 |
| H2 (sections) | 1.5rem | 600 | 1.3 |
| H3 (subsections) | 1.25rem | 600 | 1.4 |
| Small / captions | 0.875rem | 400 | 1.5 |
| Footnote markers | 0.75rem | — | superscript |
| Navigation | 0.9375rem | 500 | — |

### Text Formatting
- Body text: justified with `hyphens: auto`
- Max line width: `42rem` (~65-75 characters)
- Paragraph spacing: `1.5rem` margin-bottom

## Spacing Scale
| Token | Value |
|---|---|
| `--space-xs` | 0.25rem |
| `--space-sm` | 0.5rem |
| `--space-md` | 1rem |
| `--space-lg` | 1.5rem |
| `--space-xl` | 2rem |
| `--space-2xl` | 3rem |
| `--space-3xl` | 4rem |

## Layout

### Breakpoints (Mobile-first)
| Name | Min-width | Layout Changes |
|---|---|---|
| Default | — | Single column, no sidebar |
| Tablet portrait | 640px | Wider margins |
| Tablet landscape | 768px | Two-column review cards |
| Desktop | 1024px | Sidebar appears on review pages |
| Wide | 1280px | Max-width container |

### Grid System
- Max layout width: `72rem`
- Content width: `42rem` (for readability)
- Sidebar width: `16rem`
- Gap: `2rem`

### Review Page Layout (Desktop)
```
┌──────────────────────────────────────────────────────┐
│  [RIDE Logo]  About  Issues  Data  Reviewers  Search │  nav
├──────────────────────────────────────────────────────┤
│                  [Progress Bar]                       │
├──────────┬───────────────────────────────────────────┤
│ SIDEBAR  │  MAIN CONTENT                             │
│ (sticky) │                                           │
│          │  [Issue Badge]                             │
│ TOC      │  # Article Title                          │
│ ├ Abstract│  Author Name (ORCID)                     │
│ ├ §1     │  Affiliation                              │
│ ├ §2     │  ─────────────────────                    │
│ ├ §3     │                                           │
│ ├ Biblio │  ## Abstract                              │
│ └ Notes  │  Lorem ipsum...                           │
│          │                                           │
│ META     │  ## 1. Einführung                         │
│ Published│  Lorem ipsum dolor sit amet...            │
│ DOI      │                                           │
│ Downloads│  [Figure 1: Caption]                      │
│ ├ PDF    │                                           │
│ ├ XML    │  Footnote¹ references...                  │
│ └ Cite   │                                           │
│          │  ## Bibliography                           │
│          │  [1] Author. Title. Year...               │
│          │                                           │
│          │  ## Notes                                  │
│          │  1. Footnote text ↑                        │
│          │                                           │
│          │  ┌─────────────────────┐                  │
│          │  │ Citation Suggestion  │                  │
│          │  │ BibTeX | RIS | APA  │                  │
│          │  └─────────────────────┘                  │
│          │                                           │
│          │  [→ View Factsheet]                        │
├──────────┴───────────────────────────────────────────┤
│  Footer: IDE Logo, CC-BY 4.0, Contact, Zenodo DOI    │
└──────────────────────────────────────────────────────┘
```

### Review Page Layout (Mobile)
```
┌────────────────────────┐
│ [☰ Menu]  RIDE  [🔍]  │
├────────────────────────┤
│ [Progress Bar]         │
├────────────────────────┤
│ [Issue Badge]          │
│ # Article Title        │
│ Author (ORCID)         │
│ Published | DOI        │
│ [PDF] [XML] [Cite]    │
├────────────────────────┤
│ [▼ Table of Contents]  │  ← collapsible TOC drawer
│  (tap to expand/       │
│   collapse section     │
│   navigation)          │
├────────────────────────┤
│ ## Abstract            │
│ Lorem ipsum...         │
│                        │
│ ## 1. Einführung       │
│ Lorem ipsum...         │
│                        │
│ [Figure 1: Caption]   │
│                        │
│ ...                    │
├────────────────────────┤
│ Footer                 │
└────────────────────────┘
```

**Mobile TOC behavior**: On screens below 1024px, the sidebar TOC transforms into a collapsible drawer below the article header. Tap the "Table of Contents" bar to expand/collapse. The drawer uses `position: sticky` at the top so it remains accessible while scrolling. Active section is still highlighted via scroll spy.

## Interactive Components

### 1. Sidebar TOC with Scroll Spy
- Sticky position (top + 1.5rem) on desktop (≥1024px)
- Highlights current section based on scroll position
- Uses IntersectionObserver
- Smooth scroll on TOC link click
- Mobile (<1024px): collapsible sticky drawer below article header (see mobile layout above)
- `aria-current="true"` on active section link

### 2. Reading Progress Bar
- Thin bar (3px) at very top of page
- Width = scroll percentage of article content
- Color: `--color-primary`
- Only on review pages
- `aria-hidden="true"` (decorative)

### 3. Footnote Popovers
- Click footnote marker → popover appears near marker
- Content: footnote text
- Dismiss: click-outside or Escape key
- Mobile fallback: scroll to footnote section (popovers are small-screen hostile)
- Popover has arrow pointing to marker
- `role="tooltip"`, `aria-describedby` linking marker to popover

### 4. Image Lightbox
- Click any review figure → fullscreen overlay
- Dark backdrop with centered image
- Close: click backdrop / Escape / X button
- Navigation: arrow keys for prev/next figure
- Shows figure number and caption below image
- Focus trap: Tab cycles within lightbox when open
- `role="dialog"`, `aria-modal="true"`, `aria-label="Image viewer"`

### 5. Dark/Light Mode Toggle
- Button in navigation bar (sun/moon icon)
- Priority: localStorage → `prefers-color-scheme` → default light
- Sets `data-theme="dark|light"` on `<html>`
- Transition: 300ms on background and color properties
- `aria-label="Toggle dark mode"`, `aria-pressed` state

### 6. Citation Copy Box
- Tabs: BibTeX | RIS | APA | MLA | Chicago
- Code block with formatted citation
- "Copy" button → copies to clipboard via `navigator.clipboard.writeText()`
- Visual feedback: "Copied!" for 2 seconds
- `role="tablist"` / `role="tab"` / `role="tabpanel"` pattern

### 7. Data Page Charts
- Bar chart: score distribution across reviews
- Grouped bar: yes/no/na per category
- Filter controls: by issue type (SE/DTC/TE)
- Data embedded as JSON in page at build time
- **Implementation**: Start with HTML/CSS bar charts (colored `<div>` elements with percentage widths). Only upgrade to SVG if the CSS approach proves insufficient for grouped/stacked bars. Pure SVG rendering without a chart library is complex to get right — keep it simple.
- Accessible: data tables alongside or as alternative to visual charts

## Page-Specific Design

### Homepage
- Hero section: RIDE logo, tagline, search bar
- Latest issues grid (3 most recent)
- Quick stats: 107 reviews, 21 issues, reviewer count (derived at build time)
- Featured/latest review card

### Issues Overview
- Grid of issue cards
- Each card: issue number, title, type badge (colored), review count, date range
- Filter by type (SE/DTC/TE)
- Type badge colors: SE=blue, DTC=green, TE=purple

### Single Issue
- Issue header: number, title, type badge, editors, DOI
- Editorial link (if exists — 4 issues: 06, 08, 09, 16)
- Review cards in list view

### Review Card (reusable component)
```
┌─────────────────────────────────────┐
│ [Type Badge]        Published: Date │
│ Review Title                        │
│ by Author Name                      │
│ Reviewed: Resource Title            │
│ Keywords: tag1, tag2, tag3          │
│ DOI: 10.18716/ride.a.X.Y           │
└─────────────────────────────────────┘
```

### Factsheet Page
- Header: review title, link back to review
- Score summary bar (percentage of "Yes" answers)
- Sections matching taxonomy structure
- Each question: colored indicator (green/red/gray) + label + description
- Multi-select questions: list of selected options
- "Other" free-text shown in italics
- TE reviews with multiple resources: tabbed or sectioned layout (one section per `m="revN"`)
- Editorials: no factsheet (they have no questionnaire data)

### Reviewers Page
- Alphabetical list
- Each reviewer: name, ORCID badge (linked), affiliation
- Expandable: list of their reviews (links)

### Search Page
- Pagefind UI component
- Pagefind search box with auto-complete
- Results show: title, author, snippet, issue badge

## Metadata (SEO & Scholarly)

### Every Page
- `<title>` — Page-specific + " — RIDE"
- `<meta name="description">` — Page summary
- OpenGraph: `og:title`, `og:description`, `og:type`, `og:url`, `og:site_name`
- `<link rel="canonical">` — Canonical URL under `ride.i-d-e.de`

### Review Pages (additional)
- Dublin Core: `DC.title`, `DC.creator`, `DC.date`, `DC.identifier`, `DC.rights`, `DC.language`
- Google Scholar: `citation_title`, `citation_author`, `citation_doi`, `citation_journal_title`, `citation_publication_date`, `citation_pdf_url`
- Schema.org JSON-LD: `ScholarlyArticle` with author, publisher, DOI, datePublished, isPartOf
- License: CC-BY 4.0

## Print Stylesheet
- Hide: navigation, sidebar, progress bar, theme toggle, lightbox, footnote popovers
- Show: all footnotes inline or at page bottom
- Single column layout
- Serif fonts only (Source Serif 4)
- Black text on white
- URLs printed after links (`a[href]::after { content: " (" attr(href) ")"; }`)
- Page breaks: `break-inside: avoid` on figures, `break-before: avoid` after h2
- DOI and license info in footer
