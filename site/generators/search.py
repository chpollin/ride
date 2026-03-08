"""Search page generator — /search/index.html (Pagefind UI shell)."""

from .base import PageGenerator


class SearchGenerator(PageGenerator):
    """Generate the search page shell for Pagefind."""

    def generate(self, **kwargs):
        """Generate /search/index.html.

        The page contains only the Pagefind UI container; the actual search
        index is built by the Pagefind CLI in CI (Phase 5, Task 38).
        """
        self.render(
            "search.html",
            "search/index.html",
            active_nav="search",
        )
