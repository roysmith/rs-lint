from textwrap import dedent

import pytest
from mwparserfromhell.wikicode import Wikicode

from rs_lint import SectionOrderModule, Article


def make_article(text: str) -> Article:
    """Leading whitespace is stripped to make things play nice with autoformatters
    like black.  Typical usage is:

            article = make_article(
            '''\
                ==Foo==
                blah
            '''
        )
    """
    return Article(dedent(text))


def test_construct():
    module = SectionOrderModule()
    assert module.name == "SectionOrder"


@pytest.mark.parametrize(
    "text, expected_result",
    [
        (
            "",
            "",
        ),
        (
            "==Foo==\nblah\n",
            "",
        ),
        (
            "{{xxx}}\n==Foo==\nbar\n",
            "{{xxx}}\n",
        ),
        (
            "{{abc}}\n{{xyz}}\n==Foo==\nblah, blah\n",
            "{{abc}}\n{{xyz}}\n",
        ),
    ],
)
def test_get_pre_content(text, expected_result):
    module = SectionOrderModule()
    article = Article(text)
    result = module.get_pre_content(article)
    assert isinstance(result, Wikicode)
    assert result == expected_result
