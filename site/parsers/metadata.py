"""Extracts all metadata from teiHeader."""

from lxml import etree
from models.author import Author
from models.review import ReviewedResource, Revision

NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def _text(el) -> str:
    """Get text content of an element, stripping whitespace."""
    if el is None:
        return ""
    return " ".join((el.text or "").split() + [
        " ".join((child.tail or "").split())
        for child in el
    ]).strip()


def _all_text(el) -> str:
    """Get all text content recursively."""
    if el is None:
        return ""
    parts = []
    if el.text:
        parts.append(el.text.strip())
    for child in el:
        parts.append(_all_text(child))
        if child.tail:
            parts.append(child.tail.strip())
    return " ".join(p for p in parts if p)


def parse_metadata(root: etree._Element) -> dict:
    """Parse teiHeader and return a dict of Review fields."""
    header = root.find(".//tei:teiHeader", NS)
    if header is None:
        return {}

    result = {}

    # ride_id from TEI/@xml:id
    result["ride_id"] = root.get("{http://www.w3.org/XML/1998/namespace}id", "")

    # titleStmt
    title_stmt = header.find(".//tei:titleStmt", NS)
    if title_stmt is not None:
        title_el = title_stmt.find("tei:title", NS)
        result["title"] = _all_text(title_el) if title_el is not None else ""
        result["authors"] = _parse_authors(title_stmt)

    # publicationStmt
    pub_stmt = header.find(".//tei:publicationStmt", NS)
    if pub_stmt is not None:
        result.update(_parse_publication(pub_stmt))

    # seriesStmt
    series_stmt = header.find(".//tei:seriesStmt", NS)
    if series_stmt is not None:
        result.update(_parse_series(series_stmt))

    # notesStmt
    notes_stmt = header.find(".//tei:notesStmt", NS)
    if notes_stmt is not None:
        result.update(_parse_notes(notes_stmt))

    # profileDesc
    profile = header.find(".//tei:profileDesc", NS)
    if profile is not None:
        result.update(_parse_profile(profile))

    # revisionDesc
    revision = header.find(".//tei:revisionDesc", NS)
    if revision is not None:
        result["revisions"] = _parse_revisions(revision)

    return result


def _parse_authors(title_stmt: etree._Element) -> list[Author]:
    authors = []
    for author_el in title_stmt.findall("tei:author", NS):
        name_el = author_el.find("tei:name", NS)
        forename = ""
        surname = ""
        if name_el is not None:
            fn = name_el.find("tei:forename", NS)
            sn = name_el.find("tei:surname", NS)
            forename = _text(fn) if fn is not None else ""
            surname = _text(sn) if sn is not None else ""

        orcid = author_el.get("ref", "")
        affiliation = ""
        place = ""
        aff_el = author_el.find("tei:affiliation", NS)
        if aff_el is not None:
            org = aff_el.find("tei:orgName", NS)
            pl = aff_el.find("tei:placeName", NS)
            affiliation = _text(org) if org is not None else ""
            place = _text(pl) if pl is not None else ""

        email = ""
        email_el = author_el.find("tei:email", NS)
        if email_el is not None:
            email = _text(email_el)

        if forename or surname:
            authors.append(Author(
                forename=forename,
                surname=surname,
                orcid=orcid,
                affiliation=affiliation,
                place=place,
                email=email,
            ))
    return authors


def _parse_publication(pub_stmt: etree._Element) -> dict:
    result = {}
    pub_el = pub_stmt.find("tei:publisher", NS)
    result["publisher"] = _text(pub_el) if pub_el is not None else ""

    date_el = pub_stmt.find("tei:date", NS)
    if date_el is not None:
        result["publication_date"] = _all_text(date_el)
        result["publication_date_iso"] = date_el.get("when", "")

    for idno in pub_stmt.findall("tei:idno", NS):
        idno_type = idno.get("type", "")
        if idno_type == "URI":
            result["canonical_url"] = _text(idno)
        elif idno_type == "DOI":
            result["doi"] = _text(idno)
        elif idno_type == "archive":
            result["archive_url"] = _text(idno)

    avail = pub_stmt.find("tei:availability/tei:licence", NS)
    if avail is not None:
        result["license_url"] = avail.get("target", "")

    return result


def _parse_series(series_stmt: etree._Element) -> dict:
    result = {}
    issue_scope = series_stmt.find("tei:biblScope[@unit='issue']", NS)
    if issue_scope is not None:
        result["issue_title"] = _all_text(issue_scope)
        n = issue_scope.get("n", "")
        if n:
            result["_issue_number_from_series"] = int(n)

    editors = []
    for editor_el in series_stmt.findall("tei:editor", NS):
        role = editor_el.get("role", "")
        if role == "managing":
            continue  # Skip managing editors for issue_editors list
        name = _all_text(editor_el)
        if name:
            editors.append(name)
    result["issue_editors"] = editors

    for idno in series_stmt.findall("tei:idno", NS):
        if idno.get("type") == "DOI":
            result["issue_doi"] = _text(idno)

    return result


def _parse_notes(notes_stmt: etree._Element) -> dict:
    result = {}
    resources = []
    for ri in notes_stmt.findall("tei:relatedItem[@type='reviewed_resource']", NS):
        resources.append(_parse_reviewed_resource(ri))
    result["reviewed_resources"] = resources

    criteria_ri = notes_stmt.find("tei:relatedItem[@type='reviewing_criteria']", NS)
    if criteria_ri is not None:
        ref = criteria_ri.find(".//tei:ref", NS)
        if ref is not None:
            result["reviewing_criteria_url"] = ref.get("target", "")
            result["reviewing_criteria_label"] = _all_text(ref)

    return result


def _parse_reviewed_resource(ri: etree._Element) -> ReviewedResource:
    bibl = ri.find("tei:bibl", NS)
    if bibl is None:
        return ReviewedResource()

    title_el = bibl.find("tei:title", NS)
    title = _all_text(title_el) if title_el is not None else ""

    editors = []
    for ed in bibl.findall("tei:editor", NS):
        name = _all_text(ed)
        if name:
            editors.append(name)

    contributors = []
    for resp in bibl.findall("tei:respStmt", NS):
        role_el = resp.find("tei:resp", NS)
        name_el = resp.find("tei:persName", NS)
        role = _text(role_el) if role_el is not None else ""
        name = _all_text(name_el) if name_el is not None else ""
        if name:
            contributors.append({"role": role, "name": name})

    pub_date = ""
    for date_el in bibl.findall("tei:date", NS):
        if date_el.get("type") == "publication":
            pub_date = _all_text(date_el)

    url = ""
    access_date = ""
    for idno in bibl.findall("tei:idno", NS):
        if idno.get("type") == "URI":
            url = _text(idno)
    for date_el in bibl.findall("tei:date", NS):
        if date_el.get("type") == "accessed":
            access_date = _all_text(date_el)

    xml_id = ri.get("{http://www.w3.org/XML/1998/namespace}id", "")

    return ReviewedResource(
        title=title,
        editors=editors,
        contributors=contributors,
        publication_date=pub_date,
        url=url,
        access_date=access_date,
        xml_id=xml_id,
    )


def _parse_profile(profile: etree._Element) -> dict:
    result = {}
    lang_el = profile.find("tei:langUsage/tei:language", NS)
    if lang_el is not None:
        result["language"] = lang_el.get("ident", "en")

    keywords = []
    for term in profile.findall(".//tei:textClass/tei:keywords/tei:term", NS):
        kw = _text(term)
        if kw:
            keywords.append(kw)
    result["keywords"] = keywords

    return result


def _parse_revisions(revision_desc: etree._Element) -> list[Revision]:
    revisions = []
    for change in revision_desc.findall("tei:change", NS):
        date = change.get("when", "")
        desc = _all_text(change)
        revisions.append(Revision(date=date, description=desc))
    return revisions
