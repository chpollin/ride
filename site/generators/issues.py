"""Issue generators — /issues/index.html + /issues/issue-N/index.html."""

from .base import PageGenerator


class IssueGenerator(PageGenerator):
    """Generate issue listing and individual issue pages."""

    def generate(self, issues, **kwargs):
        """Generate the issues overview and one page per issue.

        Args:
            issues: List of Issue models (sorted by number).
        """
        # Issues overview (/issues/index.html)
        self.render(
            "issues_list.html",
            "issues/index.html",
            issues=issues,
            active_nav="issues",
        )

        # Individual issue pages (/issues/issue-N/index.html)
        for issue in issues:
            self.render(
                "issue_single.html",
                f"issues/{issue.url_slug}/index.html",
                issue=issue,
                active_nav="issues",
            )
