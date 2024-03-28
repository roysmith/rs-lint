from textwrap import dedent

import pytest
from mwparserfromhell.wikicode import Wikicode, Template

from rs_lint import SectionOrderModule, Article
from rs_lint.section_order_module import TemplateType


@pytest.fixture
def module():
    return SectionOrderModule()


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


def test_construct(module):
    assert module.name == "SectionOrder"


def test_get_pre_content_templates(module):
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
    templates = list(module.get_pre_content_templates(article))
    assert len(templates) == 4


@pytest.mark.parametrize(
    "name, template_type",
    [
        ("short description", TemplateType.SHORT_DESCRIPTION),
        ("shortdescription", TemplateType.SHORT_DESCRIPTION),
    ],
)
def test_classify_template(module, name, template_type):
    template = Template(name)
    assert module.classify_template(template) == template_type


def test_get_pre_content_template_types(module):
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
    values = [t.value for t in module.get_pre_content_template_types(article)]
    assert sorted(values) == values
