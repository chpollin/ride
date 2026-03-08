"""Homepage generator — /index.html with stats, latest issues, latest review."""

from .base import PageGenerator


class HomepageGenerator(PageGenerator):
    """Generate the site homepage."""

    def generate(self, issues, non_editorial, reviewers, **kwargs):
        """Generate /index.html with aggregate stats and teasers.

        Args:
            issues:        List of Issue models.
            non_editorial: Reviews excluding editorials (pre-filtered by build.py).
            reviewers:     List of ReviewerEntry models.
        """
        # Latest 3 issues (highest number first)
        sorted_issues = sorted(issues, key=lambda i: i.number, reverse=True)
        latest_issues = sorted_issues[:3]

        # Most recently published review (by ISO date string comparison)
        latest_review = None
        if non_editorial:
            latest_review = max(
                non_editorial,
                key=lambda r: r.publication_date_iso or "",
            )

        self.render(
            "homepage.html",
            "index.html",
            total_reviews=len(non_editorial),
            total_issues=len(issues),
            total_reviewers=len(reviewers),
            latest_issues=latest_issues,
            latest_review=latest_review,
            active_nav="home",
        )
