"""TEI body → HTML converter using recursive element walking."""

from lxml import etree
from markupsafe import Markup
from models.review import Section, Footnote
from .images import rewrite_image_url

NS = {"tei": "http://www.tei-c.org/ns/1.0"}
TEI_NS = "http://www.tei-c.org/ns/1.0"


class BodyParser:
    """Converts TEI <text> content to HTML sections, footnotes, and bibliography."""

    def __init__(self, root: etree._Element, review_slug: str, issue_number: int):
        self.root = root
        self.review_slug = review_slug
        self.issue_number = issue_number
        self.footnotes: list[Footnote] = []
        self.footnote_counter = 0

    def parse(self) -> dict:
        text_el = self.root.find(".//tei:text", NS)
        if text_el is None:
            return {"abstract_html": "", "sections": [], "footnotes": [], "bibliography_html": []}

        abstract = self._parse_front(text_el)
        sections = self._parse_body(text_el)
        bibliography = self._parse_back(text_el)

        return {
            "abstract_html": abstract,
            "sections": sections,
            "footnotes": self.footnotes,
            "bibliography_html": bibliography,
        }

    def _parse_front(self, text_el: etree._Element) -> str:
        front = text_el.find("tei:front", NS)
        if front is None:
            return ""
        abstract_div = front.find("tei:div[@type='abstract']", NS)
        if abstract_div is None:
            return ""
        return self._children_to_html(abstract_div)

    def _parse_body(self, text_el: etree._Element) -> list[Section]:
        body = text_el.find("tei:body", NS)
        if body is None:
            return []

        sections = []
        for div in body.findall("tei:div", NS):
            section = self._parse_div(div, level=2)
            if section:
                sections.append(section)
        return sections

    def _parse_div(self, div: etree._Element, level: int) -> Section:
        div_id = div.get("{http://www.w3.org/XML/1998/namespace}id", "")
        head_el = div.find("tei:head", NS)
        title = self._inline_to_html(head_el) if head_el is not None else ""
        title_text = self._text_content(head_el) if head_el is not None else ""

        html_parts = []
        for child in div:
            tag = _local(child)
            if tag == "head":
                continue  # Already extracted
            elif tag == "div":
                # Nested div → subsection
                sub = self._parse_div(child, level + 1)
                html_parts.append(f'<h{sub.level} id="{sub.id}">{sub.title}</h{sub.level}>')
                html_parts.append(sub.html)
            else:
                html_parts.append(self._element_to_html(child))

        return Section(
            id=div_id,
            title=title_text,
            html="\n".join(html_parts),
            level=level,
        )

    def _parse_back(self, text_el: etree._Element) -> list[str]:
        back = text_el.find("tei:back", NS)
        if back is None:
            return []

        bib_div = back.find("tei:div[@type='bibliography']", NS)
        if bib_div is None:
            return []

        entries = []
        for bibl in bib_div.findall(".//tei:bibl", NS):
            xml_id = bibl.get("{http://www.w3.org/XML/1998/namespace}id", "")
            html = self._inline_to_html(bibl)
            if xml_id:
                entries.append(f'<span id="{xml_id}">{html}</span>')
            else:
                entries.append(html)
        return entries

    # --- Element handlers ---

    def _element_to_html(self, el: etree._Element) -> str:
        tag = _local(el)
        handler = getattr(self, f"_handle_{tag}", None)
        if handler:
            return handler(el)
        # Fallback: render children
        return self._children_to_html(el)

    def _handle_p(self, el: etree._Element) -> str:
        pid = el.get("{http://www.w3.org/XML/1998/namespace}id", "")
        id_attr = f' id="{pid}"' if pid else ""
        content = self._inline_to_html(el)
        return f"<p{id_attr}>{content}</p>"

    def _handle_figure(self, el: etree._Element) -> str:
        fig_id = el.get("{http://www.w3.org/XML/1998/namespace}id", "")
        id_attr = f' id="{fig_id}"' if fig_id else ""

        graphic = el.find("tei:graphic", NS)
        img_url = ""
        if graphic is not None:
            raw_url = graphic.get("url", "")
            img_url = rewrite_image_url(raw_url, self.review_slug)

        caption = ""
        head_el = el.find("tei:head", NS)
        if head_el is not None:
            caption = self._inline_to_html(head_el)

        num = fig_id.replace("img", "") if fig_id.startswith("img") else ""
        fig_label = f"Fig. {num}: " if num else ""

        return (
            f'<figure{id_attr} class="review-figure">'
            f'<img src="{img_url}" alt="{_strip_html(caption)}" loading="lazy">'
            f'<figcaption>{fig_label}{caption}</figcaption>'
            f'</figure>'
        )

    def _handle_note(self, el: etree._Element) -> str:
        self.footnote_counter += 1
        n = self.footnote_counter
        note_id = el.get("{http://www.w3.org/XML/1998/namespace}id", f"fn{n}")
        content = self._inline_to_html(el)

        self.footnotes.append(Footnote(id=note_id, number=n, html=content))

        return (
            f'<sup class="fn-ref" id="{note_id}-ref">'
            f'<a href="#{note_id}" role="doc-noteref">{n}</a>'
            f'</sup>'
        )

    def _handle_list(self, el: etree._Element) -> str:
        rend = el.get("rend", "bulleted")
        if rend in ("ordered", "numbered"):
            tag = "ol"
        elif rend == "labeled":
            return self._handle_labeled_list(el)
        else:
            tag = "ul"

        items = []
        for item in el.findall("tei:item", NS):
            items.append(f"<li>{self._inline_to_html(item)}</li>")

        return f"<{tag}>{''.join(items)}</{tag}>"

    def _handle_labeled_list(self, el: etree._Element) -> str:
        items = []
        for item in el.findall("tei:item", NS):
            label = item.find("tei:label", NS)
            label_html = self._inline_to_html(label) if label is not None else ""
            content = self._inline_to_html(item)
            items.append(f"<dt>{label_html}</dt><dd>{content}</dd>")
        return f"<dl>{''.join(items)}</dl>"

    def _handle_table(self, el: etree._Element) -> str:
        rows = []
        for row in el.findall("tei:row", NS):
            cells = []
            role = row.get("role", "")
            cell_tag = "th" if role == "label" else "td"
            for cell in row.findall("tei:cell", NS):
                cols = cell.get("cols", "")
                colspan = f' colspan="{cols}"' if cols else ""
                rows_attr = cell.get("rows", "")
                rowspan = f' rowspan="{rows_attr}"' if rows_attr else ""
                content = self._inline_to_html(cell)
                cells.append(f"<{cell_tag}{colspan}{rowspan}>{content}</{cell_tag}>")
            rows.append(f"<tr>{''.join(cells)}</tr>")
        return f'<div class="table-wrapper"><table>{"".join(rows)}</table></div>'

    def _handle_cit(self, el: etree._Element) -> str:
        quote = el.find("tei:quote", NS)
        bibl = el.find("tei:bibl", NS)
        quote_html = self._inline_to_html(quote) if quote is not None else ""
        bibl_html = self._inline_to_html(bibl) if bibl is not None else ""
        return (
            f'<blockquote>'
            f'<p>{quote_html}</p>'
            f'{"<footer>" + bibl_html + "</footer>" if bibl_html else ""}'
            f'</blockquote>'
        )

    def _handle_quote(self, el: etree._Element) -> str:
        return f"<q>{self._inline_to_html(el)}</q>"

    def _handle_lg(self, el: etree._Element) -> str:
        """Line group (poetry)."""
        lines = []
        for l_el in el.findall("tei:l", NS):
            lines.append(self._inline_to_html(l_el))
        return '<div class="line-group">' + "<br>".join(lines) + "</div>"

    # --- Inline element handlers ---

    def _inline_to_html(self, el: etree._Element) -> str:
        """Convert an element's mixed content (text + children + tails) to HTML."""
        if el is None:
            return ""
        parts = []
        if el.text:
            parts.append(_esc(el.text))
        for child in el:
            parts.append(self._inline_element_to_html(child))
            if child.tail:
                parts.append(_esc(child.tail))
        return "".join(parts)

    def _inline_element_to_html(self, el: etree._Element) -> str:
        tag = _local(el)

        if tag == "emph":
            return f"<em>{self._inline_to_html(el)}</em>"

        if tag == "code":
            return f"<code>{self._inline_to_html(el)}</code>"

        if tag == "ref":
            return self._handle_ref(el)

        if tag == "note":
            return self._handle_note(el)

        if tag == "figure":
            return self._handle_figure(el)

        if tag == "hi":
            return self._handle_hi(el)

        if tag == "lb":
            return "<br>"

        if tag == "bibl":
            xml_id = el.get("{http://www.w3.org/XML/1998/namespace}id", "")
            id_attr = f' id="{xml_id}"' if xml_id else ""
            return f'<span class="bibl"{id_attr}>{self._inline_to_html(el)}</span>'

        if tag == "title":
            return f"<cite>{self._inline_to_html(el)}</cite>"

        if tag == "list":
            return self._handle_list(el)

        if tag == "table":
            return self._handle_table(el)

        if tag == "cit":
            return self._handle_cit(el)

        if tag == "quote":
            return self._handle_quote(el)

        if tag == "seg":
            return f"<span>{self._inline_to_html(el)}</span>"

        if tag == "foreign":
            lang = el.get("{http://www.w3.org/XML/1998/namespace}lang", "")
            return f'<span lang="{lang}">{self._inline_to_html(el)}</span>'

        if tag == "label":
            return f"<strong>{self._inline_to_html(el)}</strong>"

        if tag == "item":
            # item can appear inline in some contexts
            return self._inline_to_html(el)

        if tag == "head":
            return self._inline_to_html(el)

        if tag == "p":
            return self._handle_p(el)

        if tag == "lg":
            return self._handle_lg(el)

        if tag == "graphic":
            url = el.get("url", "")
            img_url = rewrite_image_url(url, self.review_slug)
            return f'<img src="{img_url}" loading="lazy">'

        if tag == "affiliation":
            return self._inline_to_html(el)

        if tag == "name":
            return self._inline_to_html(el)

        if tag == "persName":
            return self._inline_to_html(el)

        if tag == "orgName":
            return self._inline_to_html(el)

        if tag == "date":
            return self._inline_to_html(el)

        if tag == "num":
            return self._inline_to_html(el)

        if tag == "desc":
            return self._inline_to_html(el)

        if tag == "gloss":
            return self._inline_to_html(el)

        # Fallback: just render content
        return self._inline_to_html(el)

    def _handle_ref(self, el: etree._Element) -> str:
        target = el.get("target", "")
        ref_type = el.get("type", "")
        content = self._inline_to_html(el)

        if ref_type == "crossref":
            # Internal bibliography reference
            href = target if target.startswith("#") else f"#{target}"
            return f'<a href="{href}" class="crossref">{content}</a>'
        elif target.startswith("#"):
            return f'<a href="{target}">{content}</a>'
        elif target:
            return f'<a href="{target}" target="_blank" rel="noopener">{content}</a>'
        else:
            return content

    def _handle_hi(self, el: etree._Element) -> str:
        rend = el.get("rend", "")
        content = self._inline_to_html(el)
        if rend == "sup":
            return f"<sup>{content}</sup>"
        elif rend == "bold":
            return f"<strong>{content}</strong>"
        elif rend == "italic":
            return f"<em>{content}</em>"
        elif rend == "underline":
            return f'<span class="underline">{content}</span>'
        elif rend == "smallcaps":
            return f'<span class="smallcaps">{content}</span>'
        elif rend == "monospace":
            return f"<code>{content}</code>"
        else:
            return content

    # --- Helpers ---

    def _children_to_html(self, el: etree._Element) -> str:
        """Convert all children of an element to HTML."""
        parts = []
        if el.text:
            parts.append(_esc(el.text))
        for child in el:
            parts.append(self._element_to_html(child))
            if child.tail:
                parts.append(_esc(child.tail))
        return "".join(parts)

    def _text_content(self, el: etree._Element) -> str:
        """Get plain text content of an element."""
        if el is None:
            return ""
        return "".join(el.itertext()).strip()


def _local(el: etree._Element) -> str:
    """Get local name of element, stripping namespace."""
    tag = el.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag if isinstance(tag, str) else ""


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _strip_html(html: str) -> str:
    """Strip HTML tags for use in alt attributes."""
    import re
    return re.sub(r"<[^>]+>", "", html)
