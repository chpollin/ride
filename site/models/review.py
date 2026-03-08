from dataclasses import dataclass, field
from typing import Optional
from .author import Author
from .questionnaire import Questionnaire


@dataclass
class ReviewedResource:
    title: str = ""
    editors: list[str] = field(default_factory=list)
    contributors: list[dict] = field(default_factory=list)  # [{"role": ..., "name": ...}]
    publication_date: str = ""
    url: str = ""
    access_date: str = ""
    xml_id: str = ""  # For multi-resource linking


@dataclass
class Section:
    id: str
    title: str
    html: str
    level: int = 2  # h2, h3, etc.


@dataclass
class Footnote:
    id: str
    number: int
    html: str


@dataclass
class Revision:
    date: str
    description: str = ""


@dataclass
class Review:
    # Identity
    slug: str
    ride_id: str  # e.g., "ride.1.5"
    issue_number: int

    # Metadata
    title: str = ""
    authors: list[Author] = field(default_factory=list)

    # Publication
    publisher: str = ""
    publication_date: str = ""  # "June 2014"
    publication_date_iso: str = ""  # "2014-06"
    doi: str = ""
    canonical_url: str = ""
    archive_url: str = ""
    license_url: str = ""

    # Series/Issue
    issue_title: str = ""
    issue_type: str = ""
    issue_editors: list[str] = field(default_factory=list)
    issue_doi: str = ""

    # Reviewed resource(s)
    reviewed_resources: list[ReviewedResource] = field(default_factory=list)
    reviewing_criteria_url: str = ""
    reviewing_criteria_label: str = ""

    # Questionnaire(s)
    questionnaires: list[Questionnaire] = field(default_factory=list)

    # Content
    language: str = "en"
    keywords: list[str] = field(default_factory=list)
    abstract_html: str = ""
    sections: list[Section] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)
    bibliography_html: list[str] = field(default_factory=list)

    # Revisions
    revisions: list[Revision] = field(default_factory=list)

    # Paths
    pdf_filename: str = ""
    xml_filename: str = ""
    image_filenames: list[str] = field(default_factory=list)

    @property
    def is_editorial(self) -> bool:
        return self.ride_id.endswith(".0")

    @property
    def has_questionnaire(self) -> bool:
        return len(self.questionnaires) > 0

    @property
    def url(self) -> str:
        return f"/reviews/{self.slug}/"

    @property
    def factsheet_url(self) -> str:
        return f"/reviews/{self.slug}/factsheet/"

    @property
    def pdf_url(self) -> str:
        if self.pdf_filename:
            return f"/reviews/{self.slug}/{self.pdf_filename}"
        return ""

    @property
    def xml_url(self) -> str:
        if self.xml_filename:
            return f"/reviews/{self.slug}/{self.xml_filename}"
        return ""

    @property
    def doi_url(self) -> str:
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return ""

    @property
    def first_author(self) -> Optional[Author]:
        return self.authors[0] if self.authors else None

    @property
    def author_names(self) -> str:
        return ", ".join(a.full_name for a in self.authors)

    @property
    def section_titles(self) -> list[dict]:
        """For TOC generation."""
        titles = []
        if self.abstract_html:
            titles.append({"id": "abstract", "title": "Abstract", "level": 2})
        for section in self.sections:
            titles.append({"id": section.id, "title": section.title, "level": section.level})
        if self.bibliography_html:
            titles.append({"id": "bibliography", "title": "Bibliography", "level": 2})
        if self.footnotes:
            titles.append({"id": "footnotes", "title": "Notes", "level": 2})
        return titles
