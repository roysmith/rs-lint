from rs_lint import SectionOrderModule


def test_construct():
    module = SectionOrderModule("foo")
    assert module.name == "foo"
