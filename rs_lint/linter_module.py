from dataclasses import dataclass, field

from .linter_rule import LinterRule

@dataclass
class LinterModule:
    name: str
    rules: list[LinterRule] = field(default_factory=list)

    def add_rule(self, rule):
        self.rules.append(rule)
