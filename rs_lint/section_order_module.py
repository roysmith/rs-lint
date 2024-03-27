from dataclasses import dataclass
from typing import Self

from mwparserfromhell.wikicode import Wikicode

from rs_lint import LinterModule, Article


@dataclass
class SectionOrderModule(LinterModule):
    def get_pre_content(self: Self, article: Article) -> Wikicode:
        sections = article.code.get_sections()
        return sections[0]
