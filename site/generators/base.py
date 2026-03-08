"""PageGenerator base class — Jinja2 environment, filters, render helper."""

import re
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

SITE_NAME = "RIDE – A review journal for digital editions and resources"
SITE_URL = "https://ride.i-d-e.de"


# ------------------------------------------------------------------
# Custom Jinja2 filters
# ------------------------------------------------------------------

def _striptags(value: str) -> str:
    """Remove HTML tags from a string."""
    if not value:
        return ""
    return re.sub(r"<[^>]+>", "", str(value))


def _format_date(value: str, fmt: str = "%B %Y") -> str:
    """Format an ISO date string (e.g. '2014-06') for display."""
    if not value:
        return ""
    try:
        if len(value) == 7:  # "2014-06"
            dt = datetime.strptime(value, "%Y-%m")
        elif len(value) == 10:  # "2014-06-15"
            dt = datetime.strptime(value, "%Y-%m-%d")
        else:
            return value
        return dt.strftime(fmt)
    except ValueError:
        return value


def _slugify(value: str) -> str:
    """Convert a string to a URL-safe slug."""
    s = str(value).lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s.strip("-")


def _doi_url(value: str) -> str:
    """Convert a DOI to its resolver URL."""
    if not value:
        return ""
    if value.startswith("http"):
        return value
    return f"https://doi.org/{value}"


def _truncate_html(value: str, length: int = 200) -> str:
    """Strip tags then truncate."""
    text = _striptags(value)
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "…"


# ------------------------------------------------------------------
# PageGenerator base
# ------------------------------------------------------------------

class PageGenerator:
    """Base class for all page generators."""

    def __init__(self, output_dir: Path, site_url: str = SITE_URL):
        """Initialise Jinja2 environment, register filters and globals.

        Args:
            output_dir: Root directory for generated files (e.g. ``_site/``).
            site_url:   Base URL used for canonical links and sitemap.
        """
        self.output_dir = output_dir
        self.site_url = site_url.rstrip("/")

        # Locate templates relative to this file
        template_dir = Path(__file__).resolve().parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.env.filters["striptags"] = _striptags
        self.env.filters["format_date"] = _format_date
        self.env.filters["slugify"] = _slugify
        self.env.filters["doi_url"] = _doi_url
        self.env.filters["truncate_html"] = _truncate_html

        # Global context available in every template
        self.env.globals.update({
            "site_name": SITE_NAME,
            "site_url": self.site_url,
            "current_year": datetime.now().year,
        })

    def render(self, template_name: str, output_path: str, **context) -> Path:
        """Render a template to a file under output_dir.

        Args:
            template_name: Template file name (e.g. "review.html").
            output_path: Relative path under output_dir (e.g. "reviews/slug/index.html").
            **context: Template variables.

        Returns:
            The absolute Path of the written file.
        """
        template = self.env.get_template(template_name)
        html = template.render(**context)

        dest = self.output_dir / output_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        return dest

    def generate(self, **kwargs):
        """Override in subclasses to generate all pages for this generator."""
        raise NotImplementedError
