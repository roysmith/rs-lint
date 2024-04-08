from dataclasses import dataclass, field

import mwparserfromhell as mwp


@dataclass
class Article:
    """This is a stateful wrapper around a Wikicode, with the
    added functionality of an iterator over the nodes which
    can perform limited lookahead.

    """

    text: str
    code: mwp.wikicode.Wikicode = field(init=False)
    node_index: int = 0

    def __post_init__(self):
        self.code = mwp.parse(self.text)

    def next(self):
        "Return the next node and advance"
        node = self.peek()
        if node is not None:
            self.advance()
        return node

    def peek(self):
        try:
            node = self.code.nodes[self.node_index]
        except IndexError:
            return None
        return node

    def advance(self):
        self.node_index += 1
