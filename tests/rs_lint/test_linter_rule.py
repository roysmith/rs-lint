from rs_lint import LinterRule


def test_construct():
    rule = LinterRule()
    assert rule.name == "Linter"
