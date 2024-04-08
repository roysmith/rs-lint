from mwparserfromhell.nodes import Template

from rs_lint import Article


def test_construct():
    article = Article("")
    assert article.text == ""
    assert article.code == ""
    assert article.node_index == 0


def test_next_returns_none_with_empty_node_list():
    article = Article("")
    assert article.next() is None


def test_next_returns_none_at_end_of_nodes():
    article = Article("foo")
    assert article.next() == "foo"
    assert article.next() is None


def test_peek():
    article = Article("foo")
    assert article.peek() == "foo"
    assert article.peek() == "foo"
    assert article.next() == "foo"
    assert article.next() is None
