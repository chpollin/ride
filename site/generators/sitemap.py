"""Sitemap generator — /sitemap.xml."""

from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from .base import PageGenerator


class SitemapGenerator(PageGenerator):
    """Generate sitemap.xml."""

    def generate(self, issues, reviews, **kwargs):
        """Generate /sitemap.xml with all public URLs.

        Priority scheme:
        - 1.0  homepage
        - 0.9  individual reviews (primary content)
        - 0.8  issues overview
        - 0.7  individual issue pages
        - 0.6  factsheet sub-pages
        - 0.5  static pages (data, reviewers, about, search)

        Args:
            issues:  List of Issue models.
            reviews: List of Review models.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        urls = []

        urls.append({"loc": "/", "priority": "1.0", "lastmod": today})

        # Issues
        urls.append({"loc": "/issues/", "priority": "0.8", "lastmod": today})
        for issue in issues:
            urls.append({"loc": issue.url, "priority": "0.7"})

        # Reviews + factsheets
        for review in reviews:
            # ISO dates from the parser are "YYYY-MM"; sitemap requires full
            # date, so we append "-01" as a safe default day.
            lastmod = review.publication_date_iso or ""
            if len(lastmod) == 7:
                lastmod += "-01"
            urls.append({
                "loc": review.url,
                "priority": "0.9",
                "lastmod": lastmod,
            })
            if review.has_questionnaire and not review.is_editorial:
                urls.append({
                    "loc": review.factsheet_url,
                    "priority": "0.6",
                    "lastmod": lastmod,
                })

        # Static pages
        for page in ["/data/", "/reviewers/", "/about/", "/search/"]:
            urls.append({"loc": page, "priority": "0.5"})

        # Build XML
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for url in urls:
            lines.append("  <url>")
            lines.append(f"    <loc>{escape(self.site_url + url['loc'])}</loc>")
            if url.get("lastmod"):
                lines.append(f"    <lastmod>{escape(url['lastmod'])}</lastmod>")
            if url.get("priority"):
                lines.append(f"    <priority>{url['priority']}</priority>")
            lines.append("  </url>")
        lines.append("</urlset>")

        dest = self.output_dir / "sitemap.xml"
        dest.write_text("\n".join(lines), encoding="utf-8")
