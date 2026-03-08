"""Redirect generator — WordPress URL stubs → /reviews/{slug}/."""

from .base import PageGenerator


class RedirectGenerator(PageGenerator):
    """Generate redirect stubs from old WordPress URLs to new review URLs.

    Old pattern: /issues/issue-N/slug/
    New pattern: /reviews/slug/
    """

    REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{canonical}">
<title>Redirecting…</title>
</head>
<body>
<p>This page has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>"""

    def generate(self, reviews, **kwargs):
        """Generate a redirect stub for every review at its old WordPress path.

        Each stub is a minimal HTML page with ``<meta http-equiv="refresh">``
        and a ``<link rel="canonical">`` so search engines update their index.

        Args:
            reviews: List of Review models.
        """
        for review in reviews:
            # Old WordPress URL: /issues/issue-N/slug/
            old_path = f"issues/issue-{review.issue_number}/{review.slug}/index.html"
            # Guard: only write the redirect if the path has exactly the
            # expected depth (3 slashes) to avoid overwriting issue index pages.
            if old_path.startswith("issues/issue-") and old_path.count("/") == 3:
                target = review.url
                canonical = f"{self.site_url}{target}"
                html = self.REDIRECT_TEMPLATE.format(
                    target=target,
                    canonical=canonical,
                )
                dest = self.output_dir / old_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(html, encoding="utf-8")
