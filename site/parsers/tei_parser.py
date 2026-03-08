"""TEI Parser Orchestrator — XML file in, Review model out."""

import logging
from pathlib import Path

from lxml import etree

from models.issue import Issue
from models.review import Review
from .metadata import parse_metadata
from .body import BodyParser
from .taxonomy_router import parse_questionnaires
from .images import list_image_files

logger = logging.getLogger(__name__)


class TEIParser:
    """Parse a single TEI/XML file into a fully populated Review model."""

    def __init__(self, xml_path: Path | str, issue_number: int):
        self.xml_path = Path(xml_path)
        self.issue_number = issue_number

    def parse(self) -> Review:
        root = etree.parse(str(self.xml_path)).getroot()
        slug = self.xml_path.parent.name

        # --- Metadata ---
        meta = parse_metadata(root)
        meta.pop("_issue_number_from_series", None)
        issue_type = Issue.detect_type(meta.get("issue_title", ""))

        # --- Body ---
        body = BodyParser(root, slug, self.issue_number).parse()

        # --- Questionnaires ---
        questionnaires = parse_questionnaires(root)
        reviewed_resources = meta.get("reviewed_resources", [])
        self._link_te_resource_labels(questionnaires, reviewed_resources)

        # --- File assets ---
        xml_filename = self.xml_path.name
        pdf_filename = self._find_pdf(slug)
        image_filenames = self._find_images()

        # --- Build Review ---
        return Review(
            slug=slug,
            ride_id=meta.pop("ride_id", ""),
            issue_number=self.issue_number,
            issue_type=issue_type,
            **meta,
            **body,
            questionnaires=questionnaires,
            xml_filename=xml_filename,
            pdf_filename=pdf_filename,
            image_filenames=image_filenames,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _link_te_resource_labels(questionnaires, reviewed_resources):
        """For TE reviews, populate resource_label from reviewed_resources."""
        resource_map = {r.xml_id: r.title for r in reviewed_resources if r.xml_id}
        for q in questionnaires:
            if q.schema_type == "te" and q.resource_id and not q.resource_label:
                q.resource_label = resource_map.get(q.resource_id, "")

    def _find_pdf(self, slug: str) -> str:
        pdf_path = self.xml_path.parent / f"{slug}.pdf"
        if pdf_path.exists():
            return pdf_path.name
        # Try editorial naming
        pdf_path = self.xml_path.parent / "editorial.pdf"
        if pdf_path.exists():
            return pdf_path.name
        logger.warning("No PDF found for %s", slug)
        return ""

    def _find_images(self) -> list[str]:
        pictures_dir = self.xml_path.parent / "pictures"
        if not pictures_dir.is_dir():
            return []
        return list_image_files(pictures_dir)
