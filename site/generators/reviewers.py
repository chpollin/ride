"""Reviewers generator — /reviewers/index.html."""

from .base import PageGenerator


class ReviewerGenerator(PageGenerator):
    """Generate the reviewers listing page."""

    def generate(self, reviewers, **kwargs):
        """Generate /reviewers/index.html with all unique reviewers.

        Args:
            reviewers: List of ReviewerEntry (author + their reviews), sorted A-Z.
        """
        self.render(
            "reviewers.html",
            "reviewers/index.html",
            reviewers=reviewers,
            active_nav="reviewers",
        )
