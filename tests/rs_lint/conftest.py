from pytest_socket import disable_socket


def pytest_runtest_setup():
    # See https://github.com/microsoft/vscode-python/issues/22383
    disable_socket()
