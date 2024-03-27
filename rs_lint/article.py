from dataclasses import dataclass, field

import mwparserfromhell as mwp



@dataclass
class Article:
    text: str
    code: mwp.wikicode.Wikicode = field(init=False)

    def __post_init__(self):
        self.code = mwp.parse(self.text)
