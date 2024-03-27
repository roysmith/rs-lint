from rs_lint import LinterModule, LinterRule


def test_construct():
    module = LinterModule()
    assert module.name == "Linter"
    assert module.rules == []


def test_add_rule():
    module = LinterModule()
    rule = LinterRule()
    module.add_rule(rule)
    assert module.rules == [rule]
