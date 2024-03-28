from dataclasses import dataclass
from enum import Enum
from typing import Self

from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Text, Template

from rs_lint import LinterModule, Article


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


TEMPLATE_TYPE_MAP = {
    "short description": TemplateType.SHORT_DESCRIPTION,
    "shortdescription": TemplateType.SHORT_DESCRIPTION,
    "featured article": TemplateType.FEATURED_ARTICLE,
    "featured list": TemplateType.FEATURED_LIST,
    "good article": TemplateType.GOOD_ARTICLE,
    "use mdy dates": TemplateType.DATE_FORMAT,
    "use dmy dates": TemplateType.DATE_FORMAT,
}


@dataclass
class SectionOrderModule(LinterModule):

    def get_pre_content_templates(self: Self, article: Article):
        for node in article.code.nodes:
            if isinstance(node, Text) and str(node).strip() == "":
                continue
            if isinstance(node, Template):
                yield node
            else:
                return

    def classify_template(self: Self, template: Template) -> TemplateType:
        for name, template_type in TEMPLATE_TYPE_MAP.items():
            if template.name.matches(name):
                return template_type
        if template.name.lower().startswith("infobox"):
            return TemplateType.INFOBOX
        return None

    def get_pre_content_template_types(self, article):
        for template in self.get_pre_content_templates(article):
            yield self.classify_template(template)
