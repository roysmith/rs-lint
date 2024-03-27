from dataclasses import dataclass, field

from .linter_rule import LinterRule


@dataclass
class LinterModule:
    name: str = field(init=False)
    rules: list[LinterRule] = field(default_factory=list)

    def __post_init__(self):
        self.name = self.__class__.__name__.removesuffix("Module")

    def add_rule(self, rule):
        self.rules.append(rule)
