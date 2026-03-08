from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .review import Review


@dataclass
class Issue:
    number: int
    title: str = ""  # e.g., "Digital Scholarly Editions"
    issue_type: str = ""  # "editions", "textcollections", "tools"
    doi: str = ""
    editors: list[str] = field(default_factory=list)
    reviews: list["Review"] = field(default_factory=list)

    @property
    def url_slug(self) -> str:
        return f"issue-{self.number}"

    @property
    def url(self) -> str:
        return f"/issues/{self.url_slug}/"

    @property
    def review_count(self) -> int:
        return len([r for r in self.reviews if not r.is_editorial])

    @property
    def has_editorial(self) -> bool:
        return any(r.is_editorial for r in self.reviews)

    @property
    def editorial(self):
        for r in self.reviews:
            if r.is_editorial:
                return r
        return None

    @classmethod
    def detect_type(cls, issue_title: str) -> str:
        title_lower = issue_title.lower()
        if "text collection" in title_lower:
            return "textcollections"
        elif "tool" in title_lower:
            return "tools"
        else:
            return "editions"
