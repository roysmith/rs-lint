from rs_lint import SectionOrderModule


def test_construct():
    module = SectionOrderModule()
    assert module.name == "SectionOrder"
