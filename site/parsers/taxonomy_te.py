"""Tools & Environments questionnaire parser (criteria-tools)."""

from lxml import etree
from models.questionnaire import Questionnaire, QuestionnaireSection, QuestionnaireItem

NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def parse_te_taxonomy(taxonomy: etree._Element, resource_id: str = "") -> Questionnaire:
    """Parse a Tools & Environments taxonomy into a Questionnaire.

    Tools reviews can have multiple taxonomies (one per reviewed resource),
    identified by the `m` attribute on the taxonomy element.
    """
    base_url = taxonomy.get("{http://www.w3.org/XML/1998/namespace}base", "")
    m_attr = taxonomy.get("m", resource_id)

    sections = []
    for top_cat in taxonomy.findall("tei:category", NS):
        section = _parse_section(top_cat)
        if section:
            sections.append(section)

    return Questionnaire(
        schema_type="te",
        schema_url=base_url,
        resource_id=m_attr,
        sections=sections,
    )


def _parse_section(cat: etree._Element) -> QuestionnaireSection | None:
    cat_descs = cat.findall("tei:catDesc", NS)
    if not cat_descs:
        return None

    section_name = _text(cat_descs[0])

    items = []
    for child_cat in cat.findall("tei:category", NS):
        item = _parse_question(child_cat)
        if item:
            items.append(item)

    if not section_name and not items:
        return None

    return QuestionnaireSection(name=section_name, items=items)


def _parse_question(cat: etree._Element) -> QuestionnaireItem | None:
    xml_id = cat.get("{http://www.w3.org/XML/1998/namespace}id", "")
    cat_descs = cat.findall("tei:catDesc", NS)
    if not cat_descs:
        return None

    label = _text(cat_descs[0])
    catalogue_ref = ""
    ref_el = cat_descs[0].find("tei:ref", NS)
    if ref_el is not None:
        catalogue_ref = _text(ref_el)
        label = label.replace(catalogue_ref, "").strip()

    description = _text(cat_descs[1]) if len(cat_descs) > 1 else ""

    children = cat.findall("tei:category", NS)
    if not children:
        return None

    selected_value = None
    selected_label = ""
    child_items = []
    gloss = ""

    for child in children:
        child_id = child.get("{http://www.w3.org/XML/1998/namespace}id", "")
        child_descs = child.findall("tei:catDesc", NS)
        if not child_descs:
            continue

        option_label = _text(child_descs[0])

        is_selected = False
        for cd in child_descs:
            num = cd.find("tei:num[@type='boolean']", NS)
            if num is not None and num.get("value", "0") == "1":
                is_selected = True
                break

        for cd in child_descs:
            gloss_el = cd.find("tei:gloss", NS)
            if gloss_el is not None:
                g = _text(gloss_el)
                if g:
                    gloss = g

        for cd in child_descs:
            desc_el = cd.find("tei:desc", NS)
            if desc_el is not None:
                d = _text(desc_el)
                if d and is_selected:
                    gloss = d

        if is_selected:
            selected_label = option_label
            if option_label.lower() in ("yes",):
                selected_value = True
            elif option_label.lower() in ("no",):
                selected_value = False
            elif option_label.lower() in ("not applicable", "n/a"):
                selected_value = None
            else:
                selected_value = True

        child_items.append(QuestionnaireItem(
            id=child_id,
            label=option_label,
            value=is_selected if is_selected else False,
            gloss=gloss if is_selected and gloss else "",
        ))
        gloss = ""

    selected_children = [c for c in child_items if c.value]
    is_multi = len(selected_children) > 1 or len(children) > 3

    if is_multi:
        return QuestionnaireItem(
            id=xml_id,
            label=label,
            description=description,
            catalogue_ref=catalogue_ref,
            value=True if selected_children else False,
            value_label=", ".join(c.label for c in selected_children),
            children=child_items,
        )
    else:
        return QuestionnaireItem(
            id=xml_id,
            label=label,
            description=description,
            catalogue_ref=catalogue_ref,
            value=selected_value,
            value_label=selected_label,
        )


def _text(el: etree._Element) -> str:
    if el is None:
        return ""
    return " ".join("".join(el.itertext()).split()).strip()
