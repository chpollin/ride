"""Data page generator — /data/index.html with pre-computed chart data."""

from .base import PageGenerator


class DataGenerator(PageGenerator):
    """Generate the data overview page with aggregated questionnaire stats."""

    def generate(self, non_editorial, issues, chart_data, **kwargs):
        """Generate /data/index.html.

        All data aggregation is performed in build.py's DERIVE phase.
        This generator only renders the pre-computed ``chart_data``.

        Args:
            non_editorial: Reviews excluding editorials (for the total count).
            issues:        List of Issue models (for the total count).
            chart_data:    Pre-computed ChartData from ``aggregate_chart_data()``.
        """
        self.render(
            "data_overview.html",
            "data/index.html",
            total_reviews=len(non_editorial),
            total_issues=len(issues),
            counts=chart_data.counts,
            score_buckets=chart_data.score_buckets,
            category_data=chart_data.category_data,
            chart_data_scores=chart_data.chart_data_scores,
            chart_data_categories=chart_data.chart_data_categories,
            active_nav="data",
        )
