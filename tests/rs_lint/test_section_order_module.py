from unittest.mock import call, ANY
from textwrap import dedent

import pytest
from mwparserfromhell.wikicode import Wikicode, Template, Wikilink

from rs_lint import SectionOrderModule, Article
from rs_lint.section_order_module import Element, NodeInfo, Nit


@pytest.fixture
def module(mocker, site):
    mock_Category = mocker.patch("rs_lint.section_order_module.Category", autospec=True)
    mock_Category(site).articles.return_value = [
        mocker.Mock(**{"title.return_value": "redirect"})
    ]
    return SectionOrderModule(site)


@pytest.fixture
def page(mocker, site):
    mock_Page = mocker.patch("rs_lint.section_order_module.Page", autospec=True)
    return mock_Page(site)


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


@pytest.mark.parametrize(
    "template_name, redirect_name, expected_template_type",
    [
        ("short description", None, Element.SHORT_DESCRIPTION),
        ("shortdescription", "short description", Element.SHORT_DESCRIPTION),
    ],
)
def test_classify_node(
    module, page, template_name, redirect_name, expected_template_type
):
    page.title.return_value = template_name
    page.isRedirectPage.return_value = redirect_name is not None
    page.getRedirectTarget().title.return_value = redirect_name
    assert module.classify_node(Template(template_name)) == expected_template_type


@pytest.mark.parametrize(
    "text, expected_types",
    [
        (
            "",
            [],
        ),
        (
            "{{short description}} [[File:X]]",
            [Template("short description"), Wikilink("File:X")],
        ),
    ],
)
def test_get_elements(module, text, expected_types):
    article = make_article(text)
    types = list(module.get_elements(article))
    assert types == expected_types


def make_nit(name: str, ttype: Element) -> Nit:
    return Nit(
        NodeInfo(Template(name), ttype),
        "pre-content node out of order",
    )


@pytest.mark.parametrize(
    "text, expected_nits",
    [
        (
            # Realistic example
            """\
            {{short description|American aviator (1916–2019)}}
            {{Featured article}}

            {{Use mdy dates|date=July 2023}}
            {{Infobox aviator
            | image       = File:WASP Dorothy Kocher Olsen.JPG
            |caption     = Kocher {{circa|1943}} (U.S. Air Force photo).
            | name        = Dorothy Olsen
            | birth_name  = Dorothy Eleanor Kocher
            | birth_date  = {{birth date|1916|7|10}}
            | birth_place = [[Woodburn, Oregon]], U.S.
            | death_date  = {{death date and age|2019|7|23|1916|7|10}}
            | death_place = [[University Place, Washington]], U.S.
            | nationality = <!-- use only when necessary per [[WP:INFONAT]] -->
            | known for   = Member of [[Women Airforce Service Pilots]] (WASP)
            |alt=Portrait of Dorothy Olsen wearing a World-War II style bomber jacket.}}
            '''Dorothy Eleanor Olsen''' ({{née|'''Kocher'''}}; July 10, 1916 – July 23, 2019)
            was an American aircraft pilot and member of the [[Women Airforce Service Pilots]]
            (WASPs) during[[World War II]].  She grew up on her family's farm in
            [[Woodburn, Oregon]], developing an interest in aviation at a young age.
            She earned her [[Private pilot licence|private pilot's license]] in 1939,
            when it was unusual for women to be pilots. 
            """,
            [],
        ),
        (
            # Realistic example with an image
            """\
                {{Short description|Proposed nuclear radiation detecting cat}}
                {{redirect|Raycats|the song|Age Of{{!}}''Age Of''}}
                {{Use dmy dates|date=March 2024}}
                [[File:Green glowing cat.png|thumb|An artist's impression of a ray cat]]
                A '''ray cat'''{{efn||name=name}} is a proposed kind of [[cat]]
                """,
            [],
        ),
        (
            # Image in wrong order
            """\
                {{Short description|Proposed nuclear radiation detecting cat}}
                {{redirect|Raycats|the song|Age Of{{!}}''Age Of''}}
                [[File:Green glowing cat.png|thumb|An artist's impression of a ray cat]]
                {{Use dmy dates|date=March 2024}}
                A '''ray cat'''{{efn||name=name}} is a proposed kind of [[cat]]
                """,
            [
                make_nit("Use dmy dates|date=March 2024", Element.ENGLISH_OR_DATE),
            ],
        ),
        (
            # All in correct order
            "{{short description}} {{Featured article}} {{Use mdy dates}} {{Infobox aviator}}",
            [],
        ),
        (
            # One out of order
            "{{short description}} {{use mdy dates}} {{Featured article}} {{Infobox aviator}}",
            [
                make_nit("Featured article", Element.FEATURED_ARTICLE),
            ],
        ),
        (
            # Two out of order
            "{{Use mdy dates}} {{Featured article}} {{short description}}",
            [
                make_nit("Featured article", Element.FEATURED_ARTICLE),
                make_nit("short description", Element.SHORT_DESCRIPTION),
            ],
        ),
        (
            # Empty article
            "",
            [],
        ),
        (
            # No templates
            "This is the article text",
            [],
        ),
        (
            # No lead section
            """\
                {{short description}}
                ==Blah==
                This is not the lead
                """,
            [],
        ),
    ],
)
def test_get_nits(mocker, module, text, expected_nits):
    article = make_article(text)

    def f(self, template: Template):
        if template.name == "shortdescription":
            return Template("short description", template.params)
        else:
            return template

    mock_get_effective_template = mocker.patch(
        "rs_lint.section_order_module.SectionOrderModule.get_effective_template",
        autospec=True,
        side_effect=f,
    )
    nits = list(module.get_nits(article))
    assert nits == expected_nits
