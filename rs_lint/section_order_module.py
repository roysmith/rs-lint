from dataclasses import dataclass
from enum import Enum
import re
from typing import Self, Iterator

from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Text, Template
from pywikibot import Site, Page

from rs_lint import Article


class TemplateType(Enum):
    """See [[en:MOS:ORDER]].  Multiple enums can have the same
    value, indicating they are on the same ordering level.  For
    example:

      7. Templates relating to English variety and date format

    gives rise to both ENGLISH_VARIETY and DATE_FORMAT having the
    same value.  Keeping them as distinct enums can allow for richer
    error eporting.
    """

    SHORT_DESCRIPTION = 1
    TITLE_MODIFIER = 2
    HATNOTE = 3
    FEATURED_ARTICLE = 4
    FEATURED_LIST = 4
    GOOD_ARTICLE = 4
    DELETION_PROTECTION_TAG = 5
    MAINTENANCE_TAG = 6
    ENGLISH_VARIETY = 7
    DATE_FORMAT = 7
    INFOBOX = 8
    LANGUAGE_MAINTENANCE = 9
    IMAGE = 10  # Not really a template, but pretending it is simplifies things
    NAVIGATION_HEADER = 11


# Keys can be either strings of compiled regular expressions.  For strings,
# the template is compared to the string using Wikicode.matches().  For regexes,
# the normalized template name is tested using re.Pattern.match().
TEMPLATE_TYPE_MAP = {
    "short description": TemplateType.SHORT_DESCRIPTION,
    "DISPLAYTITLE": TemplateType.TITLE_MODIFIER,
    "lowercase title": TemplateType.TITLE_MODIFIER,
    "italic title": TemplateType.TITLE_MODIFIER,
    "featured article": TemplateType.FEATURED_ARTICLE,
    "featured list": TemplateType.FEATURED_LIST,
    "good article": TemplateType.GOOD_ARTICLE,
    "use mdy dates": TemplateType.DATE_FORMAT,
    "use dmy dates": TemplateType.DATE_FORMAT,
    re.compile("infobox "): TemplateType.INFOBOX,
}


@dataclass(frozen=True)
class TemplateInfo:
    template: Template
    template_type: TemplateType


@dataclass(frozen=True)
class Nit:
    info: TemplateInfo
    message: str


@dataclass
class SectionOrderModule:
    site: Site

    def get_nits(self: Self, article: Article) -> Iterator[Nit]:
        last_value = 0
        for info in self.get_pre_content_template_info(article):
            value = info.template_type.value
            if value < last_value:
                yield Nit(info, "pre-content template out of order")
            last_value = value

    def get_pre_content_template_info(self, article) -> Iterator[TemplateInfo]:
        for template in self.get_pre_content_templates(article):
            yield TemplateInfo(template, self.classify_template(template))

    def get_pre_content_templates(self: Self, article: Article) -> Iterator[Template]:
        """Gets all the templates which appear before the first real text
        in the article.  Blank lines (and other whitespace) are ignored.
        """
        for node in article.code.nodes:
            if node.strip() == "":
                continue
            if isinstance(node, Template):
                yield node
            else:
                return

    def classify_template(self: Self, template: Template) -> TemplateType:
        tname = self.get_effective_template(template).name
        for name, template_type in TEMPLATE_TYPE_MAP.items():
            if isinstance(name, str) and tname.matches(name):
                return template_type
            if isinstance(name, re.Pattern) and name.match(tname.lower()):
                return template_type
        return None

    def get_effective_template(self, template) -> Template:
        """Return the template, following the redirect, if any."""
        page = Page(self.site, f"Template:{template.name}")
        effective_page = page.getRedirectTarget() if page.isRedirectPage() else page
        return Template(effective_page.title(with_ns=False))
