import pytest
import pytest_socket
import pywikibot


def pytest_runtest_setup():
    # If you are using VS Code, See
    # https://github.com/microsoft/vscode-python/issues/22383#issuecomment-1949198679
    pytest_socket.disable_socket()


@pytest.fixture(autouse=True)
def site(monkeypatch, mocker):
    monkeypatch.setattr(pywikibot.config, "max_retries", 0)
    mocker.patch(
        "pywikibot.Site",
        side_effect=RuntimeError("Don't call pywikibot.Site() in a unit test"),
    )
    return mocker.MagicMock(spec=pywikibot.site.APISite)
