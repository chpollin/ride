#!/usr/bin/env python3
"""RIDE Static Site Builder — orchestrates the full build pipeline."""

import argparse
import json
import logging
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# Ensure site/ is on the Python path
SITE_DIR = Path(__file__).resolve().parent
if str(SITE_DIR) not in sys.path:
    sys.path.insert(0, str(SITE_DIR))

from models import Issue, Author, Review
from parsers import TEIParser
from generators import (
    ReviewGenerator,
    FactsheetGenerator,
    IssueGenerator,
    HomepageGenerator,
    ReviewerGenerator,
    DataGenerator,
    AboutGenerator,
    SearchGenerator,
    SitemapGenerator,
    RedirectGenerator,
)

logger = logging.getLogger("build")

REPO_ROOT = SITE_DIR.parent                  # Repository root (contains issues/)
STATIC_DIR = SITE_DIR / "static"              # CSS, JS, fonts, images
CONTENT_DIR = SITE_DIR / "content"            # Markdown files for /about/* pages
DEFAULT_OUTPUT = REPO_ROOT / "_site"          # Gitignored build output
DEFAULT_SITE_URL = "https://ride.i-d-e.de"   # Production URL for canonical links


# ------------------------------------------------------------------
# Data structures
# ------------------------------------------------------------------

@dataclass
class ReviewSource:
    """Discovered XML source file."""
    xml_path: Path
    issue_number: int
    slug: str


@dataclass
class ReviewerEntry:
    """A unique reviewer with their reviews."""
    author: Author
    reviews: list


@dataclass
class ChartData:
    """Pre-computed data for the /data/ page, derived in build step 3."""
    counts: dict = field(default_factory=dict)          # {"se": N, "dtc": N, "te": N}
    score_buckets: list = field(default_factory=list)    # [{"label": "0–10%", "count": N}, ...]
    category_data: list = field(default_factory=list)    # [{"name": …, "yes": N, "no": N, "na": N}, ...]
    chart_data_scores: str = ""                          # JSON string for data-chart attribute
    chart_data_categories: str = ""                      # JSON string for data-chart attribute


# ------------------------------------------------------------------
# 1. DISCOVER
# ------------------------------------------------------------------

def discover_sources(issues_dir: Path) -> list[ReviewSource]:
    """Walk issues/issueNN/slug/slug-tei.xml and return sorted source list."""
    sources = []
    if not issues_dir.is_dir():
        logger.error("Issues directory not found: %s", issues_dir)
        return sources

    for issue_dir in sorted(issues_dir.iterdir()):
        if not issue_dir.is_dir():
            continue
        match = re.match(r"issue(\d+)", issue_dir.name)
        if not match:
            continue
        issue_num = int(match.group(1))

        for slug_dir in sorted(issue_dir.iterdir()):
            if not slug_dir.is_dir():
                continue
            slug = slug_dir.name
            # Canonical name is slug-tei.xml.  If that does not exist, fall
            # back to any *-tei.xml, then any *.xml in the directory.
            xml_path = slug_dir / f"{slug}-tei.xml"
            if not xml_path.exists():
                candidates = list(slug_dir.glob("*-tei.xml"))
                if candidates:
                    xml_path = candidates[0]
                else:
                    candidates = list(slug_dir.glob("*.xml"))
                    if candidates:
                        xml_path = candidates[0]
                    else:
                        logger.warning("No XML found in %s", slug_dir)
                        continue

            sources.append(ReviewSource(
                xml_path=xml_path,
                issue_number=issue_num,
                slug=slug,
            ))

    return sources


# ------------------------------------------------------------------
# 2. PARSE
# ------------------------------------------------------------------

def parse_sources(sources: list[ReviewSource]) -> tuple[list[Review], list[tuple[str, Exception]]]:
    """Parse all XML sources into Review models. Returns (reviews, errors)."""
    reviews = []
    errors = []
    for src in sources:
        try:
            review = TEIParser(src.xml_path, src.issue_number).parse()
            reviews.append(review)
        except Exception as e:
            errors.append((src.slug, e))
            logger.warning("Failed to parse %s: %s", src.slug, e)
    return reviews, errors


# ------------------------------------------------------------------
# 3. DERIVE
# ------------------------------------------------------------------

def group_by_issue(reviews: list[Review]) -> list[Issue]:
    """Group reviews into Issue models, sorted by issue number.

    Issue-level metadata (title, editors, DOI) is derived from the first
    review in each group because the TEI files carry this information
    redundantly in every ``<seriesStmt>``.
    """
    issue_map: dict[int, list[Review]] = {}
    for r in reviews:
        issue_map.setdefault(r.issue_number, []).append(r)

    issues = []
    for num in sorted(issue_map.keys()):
        issue_reviews = issue_map[num]
        first = issue_reviews[0]
        issue = Issue(
            number=num,
            title=first.issue_title,
            issue_type=first.issue_type,
            doi=first.issue_doi,
            editors=first.issue_editors,
            reviews=sorted(issue_reviews, key=lambda r: r.ride_id),
        )
        issues.append(issue)
    return issues


def extract_reviewers(reviews: list[Review]) -> list[ReviewerEntry]:
    """Extract unique reviewers (by sort_name) with their reviews, sorted A-Z.

    Editorials are excluded because their authors are issue editors, not
    reviewers, and should not appear on the /reviewers/ page.
    """
    reviewer_map: dict[str, ReviewerEntry] = {}
    for review in reviews:
        if review.is_editorial:
            continue
        for author in review.authors:
            key = author.sort_name.lower()
            if key not in reviewer_map:
                reviewer_map[key] = ReviewerEntry(author=author, reviews=[])
            reviewer_map[key].reviews.append(review)

    return sorted(reviewer_map.values(), key=lambda r: r.author.sort_name.lower())


def aggregate_chart_data(non_editorial: list[Review]) -> ChartData:
    """Aggregate questionnaire statistics for the /data/ overview page.

    Args:
        non_editorial: Reviews excluding editorials (pre-filtered).

    Returns:
        ChartData with counts, score buckets, category breakdown, and JSON strings.
    """
    with_q = [r for r in non_editorial if r.questionnaires]

    # Count questionnaires per schema type (SE/DTC/TE)
    counts = {"se": 0, "dtc": 0, "te": 0}
    for r in with_q:
        for q in r.questionnaires:
            if q.schema_type in counts:
                counts[q.schema_type] += 1

    # Collect %-yes scores from every questionnaire
    scores = [
        q.score_percentage
        for r in with_q for q in r.questionnaires
        if q.total_answered > 0
    ]

    # Distribute into 10 %-point buckets (last bucket includes 100 %)
    buckets = []
    for lo in range(0, 100, 10):
        hi = lo + 10
        if lo < 90:
            count = sum(1 for s in scores if lo <= s < hi)
        else:
            count = sum(1 for s in scores if lo <= s <= hi)
        buckets.append({"label": f"{lo}–{hi}%", "count": count})

    # Aggregate yes/no/na per section name across all questionnaire types
    cat_map: dict[str, dict] = {}
    for r in with_q:
        for q in r.questionnaires:
            for section in q.sections:
                entry = cat_map.setdefault(
                    section.name, {"name": section.name, "yes": 0, "no": 0, "na": 0}
                )
                entry["yes"] += section.total_yes
                entry["no"] += section.total_no
                entry["na"] += section.total_na
    category_data = list(cat_map.values())

    # Serialise for HTML data-chart attributes (consumed by charts.js)
    chart_scores = json.dumps({
        "labels": [b["label"] for b in buckets],
        "values": [b["count"] for b in buckets],
    })
    chart_categories = json.dumps({
        "labels": [c["name"] for c in category_data],
        "yes": [c["yes"] for c in category_data],
        "no": [c["no"] for c in category_data],
        "na": [c["na"] for c in category_data],
    })

    return ChartData(
        counts=counts,
        score_buckets=buckets,
        category_data=category_data,
        chart_data_scores=chart_scores,
        chart_data_categories=chart_categories,
    )


# ------------------------------------------------------------------
# 4. CLEAN
# ------------------------------------------------------------------

def clean_output(output_dir: Path):
    """Remove old output directory."""
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------
# 5. COPY STATIC
# ------------------------------------------------------------------

def copy_static(static_dir: Path, output_dir: Path):
    """Copy static assets (CSS, JS, fonts, images) to output."""
    if not static_dir.is_dir():
        logger.warning("Static directory not found: %s", static_dir)
        return
    for sub in static_dir.iterdir():
        dst = output_dir / sub.name
        if sub.is_dir():
            shutil.copytree(sub, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(sub, dst)


# ------------------------------------------------------------------
# 7. META FILES
# ------------------------------------------------------------------

def write_meta_files(output_dir: Path, site_url: str):
    """Write .nojekyll, CNAME, robots.txt."""
    (output_dir / ".nojekyll").touch()

    # Extract domain from site_url
    domain = site_url.replace("https://", "").replace("http://", "").strip("/")
    (output_dir / "CNAME").write_text(domain, encoding="utf-8")

    robots = f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n"
    (output_dir / "robots.txt").write_text(robots, encoding="utf-8")


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def main(output_dir: Path = DEFAULT_OUTPUT, site_url: str = DEFAULT_SITE_URL):
    """Run the complete build pipeline.

    Steps: discover → parse → derive → clean → copy static → generate → meta.
    Returns the number of parse errors (0 = success).
    """
    start = time.time()
    logger.info("Starting RIDE build → %s", output_dir)

    # 1. DISCOVER
    sources = discover_sources(REPO_ROOT / "issues")
    logger.info("Discovered %d XML sources", len(sources))

    # 2. PARSE
    reviews, errors = parse_sources(sources)
    logger.info("Parsed %d reviews (%d errors)", len(reviews), len(errors))

    # 3. DERIVE
    issues = group_by_issue(reviews)
    non_editorial = [r for r in reviews if not r.is_editorial]
    reviewers = extract_reviewers(reviews)
    chart_data = aggregate_chart_data(non_editorial)
    logger.info("Derived %d issues, %d unique reviewers", len(issues), len(reviewers))

    # 4. CLEAN
    clean_output(output_dir)

    # 5. COPY STATIC
    copy_static(STATIC_DIR, output_dir)
    logger.info("Copied static assets")

    # 6. GENERATE
    gen_kwargs = dict(
        reviews=reviews,
        non_editorial=non_editorial,
        issues=issues,
        reviewers=reviewers,
        chart_data=chart_data,
        source_root=REPO_ROOT,
        content_dir=CONTENT_DIR,
    )

    # Generators run in dependency order: reviews first (creates slug dirs
    # for factsheets and asset copies), then derived pages, then meta pages.
    # Each generator receives all kwargs and picks what it needs via **kwargs.
    generators = [
        ("Reviews", ReviewGenerator),
        ("Factsheets", FactsheetGenerator),
        ("Issues", IssueGenerator),
        ("Homepage", HomepageGenerator),
        ("Reviewers", ReviewerGenerator),
        ("Data", DataGenerator),
        ("About", AboutGenerator),
        ("Search", SearchGenerator),
        ("Sitemap", SitemapGenerator),
        ("Redirects", RedirectGenerator),
    ]

    for name, GenClass in generators:
        gen = GenClass(output_dir, site_url)
        try:
            gen.generate(**gen_kwargs)
            logger.info("Generated: %s", name)
        except Exception as e:
            # Log but don't abort — remaining generators can still succeed.
            logger.error("Generator %s failed: %s", name, e, exc_info=True)

    # 7. META FILES
    write_meta_files(output_dir, site_url)

    # 8. REPORT
    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"RIDE build complete in {elapsed:.1f}s")
    print(f"  Output:    {output_dir}")
    print(f"  Reviews:   {len(reviews)} ({len(errors)} errors)")
    print(f"  Issues:    {len(issues)}")
    print(f"  Reviewers: {len(reviewers)}")
    if errors:
        print(f"\nFailed ({len(errors)}):")
        for slug, err in errors:
            print(f"  {slug}: {err}")
    print(f"{'='*60}")

    return len(errors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the RIDE static site.")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--site-url",
        default=DEFAULT_SITE_URL,
        help=f"Site URL for canonical links (default: {DEFAULT_SITE_URL})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)-8s %(name)s: %(message)s",
    )

    error_count = main(args.output, args.site_url)
    sys.exit(1 if error_count > 0 else 0)
