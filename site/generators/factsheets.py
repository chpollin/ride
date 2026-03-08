"""Factsheet generator — /reviews/{slug}/factsheet/index.html (skip editorials)."""

from .base import PageGenerator


class FactsheetGenerator(PageGenerator):
    """Generate factsheet pages for reviews with questionnaires."""

    def generate(self, reviews, **kwargs):
        """Generate a factsheet page for each review that has questionnaire data.

        Editorials and reviews without questionnaires are skipped.

        Args:
            reviews: List of Review models.
        """
        for review in reviews:
            if review.is_editorial or not review.has_questionnaire:
                continue
            self.render(
                "factsheet.html",
                f"reviews/{review.slug}/factsheet/index.html",
                review=review,
                page_title=f"Factsheet: {review.title}",
                active_nav="issues",
            )
