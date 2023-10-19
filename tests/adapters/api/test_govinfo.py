"""
Tests for the GovInfo adapter.
"""
import requests

from shillelagh.backends.apsw.db import connect


def test_govinfo(mocker, requests_mock):
    """
    Run SQL against the adapter.
    """
    connection = connect(":memory:")
    cursor = connection.cursor()

    # Mock network requests.
    adapter = requests_mock.Adapter()
    adapter.register_uri("GET", "https://api.example.com/", json={"hello": "world"})

    # And mock the session object.
    session = requests.Session()
    session.mount("https://api.example.com/", adapter)
    mocker.patch(
        "shillelagh.adapters.api.govinfo.GovInfoAPI._get_session",
        return_value=session,
    )

    # Replace this with a URI supported by the adapter.
    sql = """
        SELECT * FROM "https://api.example.com/"
    """
    cursor.execute(sql)
    assert cursor.fetchall() == []
