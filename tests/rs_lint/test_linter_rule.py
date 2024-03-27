from rs_lint import LinterRule


def test_construct():
    rule = LinterRule("foo")
    assert rule.name == "foo"
