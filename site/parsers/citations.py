"""Citation generators — Review model → formatted citation strings."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.review import Review

JOURNAL_TITLE = "RIDE – A review journal for digital editions and resources"


def _year(review: "Review") -> str:
    """Extract 4-digit year from ISO date (e.g. '2014-06' → '2014')."""
    if review.publication_date_iso:
        return review.publication_date_iso[:4]
    return ""


def _doi_url(review: "Review") -> str:
    if review.doi:
        return f"https://doi.org/{review.doi}"
    return ""


# ------------------------------------------------------------------
# BibTeX
# ------------------------------------------------------------------

def bibtex(review: "Review") -> str:
    authors = " and ".join(
        f"{a.surname}, {a.forename}" for a in review.authors
    )
    year = _year(review)
    lines = [
        f"@article{{{review.slug},",
        f"  author    = {{{authors}}},",
        f"  title     = {{{review.title}}},",
        f"  journal   = {{{JOURNAL_TITLE}}},",
        f"  number    = {{{review.issue_number}}},",
    ]
    if year:
        lines.append(f"  year      = {{{year}}},")
    if review.doi:
        lines.append(f"  doi       = {{{review.doi}}},")
        lines.append(f"  url       = {{{_doi_url(review)}}},")
    lines.append("}")
    return "\n".join(lines)


# ------------------------------------------------------------------
# RIS
# ------------------------------------------------------------------

def ris(review: "Review") -> str:
    lines = ["TY  - JOUR"]
    for a in review.authors:
        lines.append(f"AU  - {a.surname}, {a.forename}")
    lines.append(f"TI  - {review.title}")
    lines.append(f"T2  - {JOURNAL_TITLE}")
    lines.append(f"IS  - {review.issue_number}")
    year = _year(review)
    if year:
        lines.append(f"PY  - {year}")
    if review.publication_date_iso:
        da = review.publication_date_iso.replace("-", "/")
        lines.append(f"DA  - {da}")
    if review.doi:
        lines.append(f"DO  - {review.doi}")
    url = _doi_url(review) or review.canonical_url
    if url:
        lines.append(f"UR  - {url}")
    if review.publisher:
        lines.append(f"PB  - {review.publisher}")
    if review.language:
        lines.append(f"LA  - {review.language}")
    lines.append("ER  - ")
    return "\n".join(lines)


# ------------------------------------------------------------------
# APA 7th edition
# ------------------------------------------------------------------

def apa(review: "Review") -> str:
    # Authors: Surname, F., & Surname2, F.
    parts = []
    for a in review.authors:
        initials = ". ".join(n[0] for n in a.forename.split() if n) + "."
        parts.append(f"{a.surname}, {initials}")
    if len(parts) == 1:
        author_str = parts[0]
    elif len(parts) == 2:
        author_str = f"{parts[0]}, & {parts[1]}"
    else:
        author_str = ", ".join(parts[:-1]) + f", & {parts[-1]}"

    year = _year(review)
    year_str = f" ({year})" if year else ""

    ref = f"{author_str}{year_str}. {review.title}. {JOURNAL_TITLE}, ({review.issue_number})."
    doi = _doi_url(review)
    if doi:
        ref += f" {doi}"
    return ref


# ------------------------------------------------------------------
# MLA 9th edition
# ------------------------------------------------------------------

def mla(review: "Review") -> str:
    authors = review.authors
    if len(authors) == 1:
        a = authors[0]
        author_str = f"{a.surname}, {a.forename}"
    elif len(authors) == 2:
        author_str = (
            f"{authors[0].surname}, {authors[0].forename}"
            f", and {authors[1].full_name}"
        )
    elif len(authors) >= 3:
        author_str = f"{authors[0].surname}, {authors[0].forename}, et al."
    else:
        author_str = ""

    year = _year(review)
    ref = f'{author_str}. "{review.title}." {JOURNAL_TITLE}, no. {review.issue_number}, {year}.'
    doi = _doi_url(review)
    if doi:
        ref = ref.rstrip(".") + f". {doi}."
    return ref


# ------------------------------------------------------------------
# Chicago 17th edition (notes-bibliography style)
# ------------------------------------------------------------------

def chicago(review: "Review") -> str:
    authors = review.authors
    if len(authors) == 1:
        a = authors[0]
        author_str = f"{a.surname}, {a.forename}"
    elif len(authors) == 2:
        author_str = (
            f"{authors[0].surname}, {authors[0].forename}"
            f", and {authors[1].full_name}"
        )
    elif len(authors) >= 3:
        author_str = (
            f"{authors[0].surname}, {authors[0].forename}, "
            + ", ".join(a.full_name for a in authors[1:-1])
            + f", and {authors[-1].full_name}"
        )
    else:
        author_str = ""

    year = _year(review)
    ref = f'{author_str}. "{review.title}." {JOURNAL_TITLE}, no. {review.issue_number} ({year}).'
    doi = _doi_url(review)
    if doi:
        ref = ref.rstrip(".") + f". {doi}."
    return ref


# ------------------------------------------------------------------
# All formats as a dict
# ------------------------------------------------------------------

def all_citations(review: "Review") -> dict[str, str]:
    """Return all citation formats for a review."""
    return {
        "bibtex": bibtex(review),
        "ris": ris(review),
        "apa": apa(review),
        "mla": mla(review),
        "chicago": chicago(review),
    }
