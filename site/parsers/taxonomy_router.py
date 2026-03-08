"""Detects which taxonomy schema is used and dispatches to the correct parser."""

from lxml import etree
from models.questionnaire import Questionnaire
from .taxonomy_se import parse_se_taxonomy
from .taxonomy_dtc import parse_dtc_taxonomy
from .taxonomy_te import parse_te_taxonomy

NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def parse_questionnaires(root: etree._Element) -> list[Questionnaire]:
    """Parse all taxonomy elements and return a list of Questionnaires.

    Returns empty list for editorials (no encodingDesc).
    Returns one Questionnaire for SE and DTC reviews.
    Returns multiple Questionnaires for Tools reviews (one per reviewed resource).
    """
    encoding_desc = root.find(".//tei:encodingDesc", NS)
    if encoding_desc is None:
        return []

    taxonomies = encoding_desc.findall(".//tei:taxonomy", NS)
    if not taxonomies:
        return []

    results = []
    for tax in taxonomies:
        base = tax.get("{http://www.w3.org/XML/1998/namespace}base", "")
        m_attr = tax.get("m", "") or tax.get("n", "")

        if "criteria-version-1-1" in base or "criteria-version-1" in base:
            # Check if it's SE (not DTC and not TE)
            if "text-collection" not in base and "tools" not in base:
                results.append(parse_se_taxonomy(tax))
        elif "text-collection" in base:
            results.append(parse_dtc_taxonomy(tax))
        elif "tools" in base:
            results.append(parse_te_taxonomy(tax, m_attr))
        else:
            # Unknown schema - try SE as fallback
            results.append(parse_se_taxonomy(tax))

    return results
