from unittest.mock import call, ANY
from textwrap import dedent

import pytest
from mwparserfromhell.wikicode import Wikicode, Template

from rs_lint import SectionOrderModule, Article
from rs_lint.section_order_module import TemplateType, TemplateInfo, Nit


@pytest.fixture
def module(site):
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
        ("short description", None, TemplateType.SHORT_DESCRIPTION),
        ("shortdescription", "short description", TemplateType.SHORT_DESCRIPTION),
    ],
)
def test_classify_template(
    module, page, template_name, redirect_name, expected_template_type
):
    page.title.return_value = template_name
    page.isRedirectPage.return_value = redirect_name is not None
    page.getRedirectTarget().title.return_value = redirect_name
    assert module.classify_template(Template(template_name)) == expected_template_type


def test_get_pre_content_template_info(mocker, module):
    article = make_article(
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
            """
    )
    mock_classify_template = mocker.patch(
        "rs_lint.section_order_module.SectionOrderModule.classify_template",
        autospec=True,
    )
    mock_classify_template.side_effect = [
        TemplateType.SHORT_DESCRIPTION,
        TemplateType.FEATURED_ARTICLE,
        TemplateType.DATE_FORMAT,
        TemplateType.INFOBOX,
    ]

    types = [i.template_type for i in module.get_pre_content_template_info(article)]

    assert types == [
        TemplateType.SHORT_DESCRIPTION,
        TemplateType.FEATURED_ARTICLE,
        TemplateType.DATE_FORMAT,
        TemplateType.INFOBOX,
    ]
    values = [t.value for t in types]
    assert sorted(values) == values

    calls = mock_classify_template.call_args_list
    assert [c.args[1].name.strip() for c in calls] == [
        "short description",
        "Featured article",
        "Use mdy dates",
        "Infobox aviator",
    ]


def make_nit(name: str, ttype: TemplateType) -> Nit:
    return Nit(
        TemplateInfo(Template(name), ttype),
        "pre-content template out of order",
    )


@pytest.mark.parametrize(
    "text, names, ttypes, expected_nits",
    [
        (
            # All in correct order
            "{{short description}} {{Featured article}} {{Use mdy dates}} {{Infobox aviator}}",
            [
                "short description",
                "Featured article",
                "Use mdy dates",
                "Infobox aviation",
            ],
            [
                TemplateType.SHORT_DESCRIPTION,
                TemplateType.FEATURED_ARTICLE,
                TemplateType.DATE_FORMAT,
                TemplateType.INFOBOX,
            ],
            [],
        ),
        (
            # One out of order
            "{{short description}} {{use mdy dates}} {{Featured article}} {{Infobox aviator}}",
            [
                "short description",
                "Use mdy dates",
                "Featured article",
                "Infobox aviation",
            ],
            [
                TemplateType.SHORT_DESCRIPTION,
                TemplateType.DATE_FORMAT,
                TemplateType.FEATURED_ARTICLE,
                TemplateType.INFOBOX,
            ],
            [
                make_nit("Featured article", TemplateType.FEATURED_ARTICLE),
            ],
        ),
        (
            # Two out of order
            "{{Use mdy dates}} {{Featured article}} {{short description}}",
            [
                "Use mdy dates",
                "Featured article",
                "short description",
            ],
            [
                TemplateType.DATE_FORMAT,
                TemplateType.FEATURED_ARTICLE,
                TemplateType.SHORT_DESCRIPTION,
            ],
            [
                make_nit("Featured article", TemplateType.FEATURED_ARTICLE),
                make_nit("short description", TemplateType.SHORT_DESCRIPTION),
            ],
        ),
    ],
)
def test_get_nits(mocker, module, text, names, ttypes, expected_nits):
    article = make_article(text)

    mock_get_pre_content_template_info = mocker.patch(
        "rs_lint.section_order_module.SectionOrderModule.get_pre_content_template_info",
        autospec=True,
    )
    mock_get_pre_content_template_info.return_value = [
        TemplateInfo(Template(name), ttype) for name, ttype in zip(names, ttypes)
    ]

    nits = list(module.get_nits(article))
    assert nits == expected_nits
