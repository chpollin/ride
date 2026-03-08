from dataclasses import dataclass, field


@dataclass
class Author:
    forename: str
    surname: str
    orcid: str = ""
    affiliation: str = ""
    place: str = ""
    email: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.forename} {self.surname}".strip()

    @property
    def sort_name(self) -> str:
        return f"{self.surname}, {self.forename}".strip(", ")

    @property
    def orcid_url(self) -> str:
        if self.orcid and not self.orcid.startswith("http"):
            return f"https://orcid.org/{self.orcid}"
        return self.orcid
