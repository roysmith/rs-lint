from rs_lint import Article


def test_construct():
    article = Article("")
    assert article.text == ""
    assert article.code == ""
