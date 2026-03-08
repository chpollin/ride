"""About page generator — /about/*/index.html from Markdown content."""

import logging
from pathlib import Path

import markdown

from .base import PageGenerator

logger = logging.getLogger(__name__)

# (filename_without_ext, page_title, url_slug)
# An empty slug means the page lives at /about/index.html directly.
ABOUT_PAGES = [
    ("about", "About RIDE", ""),
    ("editorial-board", "Editorial Board", "editorial-board"),
    ("publishing-policy", "Publishing Policy", "publishing-policy"),
    ("ethical-code", "Ethical Code", "ethical-code"),
    ("contact", "Contact", "contact"),
    ("reviewing-criteria", "Reviewing Criteria", "reviewing-criteria"),
]


class AboutGenerator(PageGenerator):
    """Generate about pages from Markdown files."""

    def generate(self, content_dir: Path, **kwargs):
        """Render each about page from its Markdown source.

        If a ``.md`` file does not exist yet, a placeholder is rendered so the
        build never fails on missing editorial content (Phase 5, Task 40).

        Args:
            content_dir: Directory containing ``*.md`` source files.
        """
        for filename, title, slug in ABOUT_PAGES:
            md_path = content_dir / f"{filename}.md"
            if md_path.exists():
                md_text = md_path.read_text(encoding="utf-8")
                # tables + fenced_code for rich content; toc for auto-generated
                # heading anchors in longer about pages.
                html_content = markdown.markdown(
                    md_text,
                    extensions=["tables", "fenced_code", "toc"],
                )
            else:
                logger.warning("Content file not found: %s", md_path)
                html_content = f"<p><em>Content for &ldquo;{title}&rdquo; is coming soon.</em></p>"

            out_path = f"about/{slug}/index.html" if slug else "about/index.html"
            self.render(
                "about.html",
                out_path,
                page_title=title,
                page_slug=slug,
                content=html_content,
                active_nav="about",
            )
