from rs_lint import LinterModule, LinterRule

def test_construct():
    module = LinterModule('foo')
    assert module.name == 'foo'
    assert module.rules == []

def test_add_rule():
    module = LinterModule('module')
    rule = LinterRule('rule')
    module.add_rule(rule)
    assert module.rules == [rule]