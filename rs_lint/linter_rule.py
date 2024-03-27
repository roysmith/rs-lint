from dataclasses import dataclass, field


@dataclass
class LinterRule:
    name: str = field(init=False)

    def __post_init__(self):
        self.name = self.__class__.__name__.removesuffix("Rule")
