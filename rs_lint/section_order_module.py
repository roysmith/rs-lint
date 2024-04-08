from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Self, Iterator

from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Node, Template, Wikilink
from pywikibot import Site, Page, Category

from rs_lint import Article


class Element(Enum):
    "See [[en:MOS:ORDER]]."

    SHORT_DESCRIPTION = 1
    TITLE_MODIFIER = 2
    HATNOTE = 3
    FEATURED_ARTICLE = 4
    FEATURED_LIST = 4
    GOOD_ARTICLE = 4
    DELETION_PROTECTION_TAG = 5
    MAINTENANCE_TAG = 6
    ENGLISH_OR_DATE = 7
    INFOBOX = 8
    LANGUAGE_MAINTENANCE = 9
    IMAGE = 10
    NAVIGATION_HEADER = 11


# Keys can be either strings or compiled regular expressions.  For strings,
# the node is compared to the string using Wikicode.matches().  For regexes,
# the normalized node name is tested using re.Pattern.match().
NODE_TYPE_MAP_PRELOAD = {
    "short description": Element.SHORT_DESCRIPTION,
    "DISPLAYTITLE": Element.TITLE_MODIFIER,
    "lowercase title": Element.TITLE_MODIFIER,
    "italic title": Element.TITLE_MODIFIER,
    "featured article": Element.FEATURED_ARTICLE,
    "featured list": Element.FEATURED_LIST,
    "good article": Element.GOOD_ARTICLE,
    "use mdy dates": Element.ENGLISH_OR_DATE,
    "use dmy dates": Element.ENGLISH_OR_DATE,
    re.compile("infobox "): Element.INFOBOX,
}


@dataclass(frozen=True)
class NodeInfo:
    node: Node
    node_type: Element


@dataclass(frozen=True)
class Nit:
    info: NodeInfo
    message: str


@dataclass
class SectionOrderModule:
    site: Site
    node_type_map: dict = field(default_factory=dict)

    def __post_init__(self: Self):
        self.node_type_map = dict(NODE_TYPE_MAP_PRELOAD)
        for template in self.get_hatnote_templates():
            self.node_type_map[str(template.name)] = Element.HATNOTE

    def get_nits(self: Self, article: Article) -> Iterator[Nit]:
        last_value = 0
        for node in self.get_pre_content_nodes(article):
            info = NodeInfo(node, self.classify_node(node))
            value = info.node_type.value
            if value < last_value:
                yield Nit(info, "pre-content node out of order")
            last_value = value

    def get_pre_content_nodes(self: Self, article: Article) -> Iterator[Node]:
        """Gets all the templates and images which appear before the first
        real text in the article (i.e. before the lead).  Blank lines (and
        other whitespace) are ignored.

        """
        while (node := article.peek()) is not None:
            if node.strip() == "":
                article.advance()
                continue
            elif isinstance(node, Template):
                article.advance()
                yield node
            elif isinstance(node, Wikilink) and node.title.startswith("File:"):
                article.advance()
                yield node
            else:
                return

    def get_elements(self: Self, article: Article) -> Iterator[Node]:
        for node in self.get_pre_content_nodes(article):
            yield node

    def classify_node(self: Self, node: Node) -> Element:
        if isinstance(node, Wikilink) and node.title.startswith("File:"):
            return Element.IMAGE
        tname = self.get_effective_template(node).name
        for name, node_type in self.node_type_map.items():
            if isinstance(name, str) and tname.matches(name):
                return node_type
            if isinstance(name, re.Pattern) and name.match(tname.lower()):
                return node_type
        return None

    def get_effective_template(self: Self, template: Template) -> Template:
        """Return the template, following the redirect, if any."""
        page = Page(self.site, f"Template:{template.name}")
        effective_page = page.getRedirectTarget() if page.isRedirectPage() else page
        return Template(effective_page.title(with_ns=False))

    def get_hatnote_templates(self: Self) -> Iterator[Template]:
        cat = Category(self.site, "Hatnote templates")
        for article in cat.articles():
            yield Template(article.title(with_ns=False))
