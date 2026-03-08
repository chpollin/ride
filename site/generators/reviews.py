"""Review page generator — /reviews/{slug}/index.html + copy assets."""

import logging
import shutil
from pathlib import Path

from .base import PageGenerator
from parsers.citations import all_citations

logger = logging.getLogger(__name__)


class ReviewGenerator(PageGenerator):
    """Generate individual review pages and copy associated assets."""

    def generate(self, reviews, source_root: Path, **kwargs):
        """Generate all review pages.

        Args:
            reviews: List of Review models.
            source_root: Repository root (parent of issues/).
        """
        for review in reviews:
            self._generate_review(review)
            self._copy_assets(review, source_root)

    def _generate_review(self, review):
        """Render a single review page with all citation formats."""
        citations = all_citations(review)
        self.render(
            "review.html",
            f"reviews/{review.slug}/index.html",
            review=review,
            citations=citations,
            page_title=review.title,
            page_lang=review.language,
            active_nav="issues",
        )

    def _copy_assets(self, review, source_root: Path):
        """Copy PDF, XML, and images from the source repo to the output directory.

        Args:
            review:      Review model with filenames to copy.
            source_root: Repository root containing ``issues/`` directory.
        """
        issue_dir = source_root / "issues" / f"issue{review.issue_number:02d}" / review.slug
        review_out = self.output_dir / "reviews" / review.slug
        review_out.mkdir(parents=True, exist_ok=True)

        # PDF
        if review.pdf_filename:
            src = issue_dir / review.pdf_filename
            if src.exists():
                shutil.copy2(src, review_out / review.pdf_filename)
            else:
                logger.warning("PDF not found: %s", src)

        # XML
        if review.xml_filename:
            src = issue_dir / review.xml_filename
            if src.exists():
                shutil.copy2(src, review_out / review.xml_filename)
            else:
                logger.warning("XML not found: %s", src)

        # Images
        pictures_src = issue_dir / "pictures"
        if pictures_src.is_dir() and review.image_filenames:
            pictures_dst = review_out / "pictures"
            pictures_dst.mkdir(parents=True, exist_ok=True)
            for img_name in review.image_filenames:
                src = pictures_src / img_name
                if src.exists():
                    shutil.copy2(src, pictures_dst / img_name)
                else:
                    # Some source images have uppercase extensions (.PNG);
                    # fall back to case-insensitive match on the filesystem.
                    matched = False
                    for f in pictures_src.iterdir():
                        if f.name.lower() == img_name.lower():
                            shutil.copy2(f, pictures_dst / img_name)
                            matched = True
                            break
                    if not matched:
                        logger.warning("Image not found: %s/%s", review.slug, img_name)
