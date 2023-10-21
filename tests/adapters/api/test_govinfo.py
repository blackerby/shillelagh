"""
Tests for the GovInfo adapter.
"""
from datetime import datetime

import pytest
import pytest_mock
import requests
from requests_mock.mocker import Mocker

from shillelagh.adapters.api.govinfo import GovInfoAPI
from shillelagh.backends.apsw.db import connect

from ...fakes import govinfo_empty_response, govinfo_response

FAKE_API_KEY = "44a3270074f30ea5a8f0051941fb6528"


def test_supports() -> None:
    """
    Test the ``supports`` method.
    """

    # Test support of "/collections" endpoint
    assert GovInfoAPI.supports("https://api.govinfo.gov/collections") is False
    assert (
        GovInfoAPI.supports(
            f"https://api.govinfo.gov/collections?api_key={FAKE_API_KEY}",
        )
        is False
    )
    assert (
        GovInfoAPI.supports(
            f"https://api.govinfo.gov/collections/BILLS/2018-01-28T20%3A18%3A10Z?api_key={FAKE_API_KEY}",
        )
        is False
    )
    assert (
        GovInfoAPI.supports(
            f"https://api.govinfo.gov/collections/BILLS/2018-01-28T20%3A18%3A10Z?offset=0&api_key={FAKE_API_KEY}",
        )
        is False
    )
    assert (
        GovInfoAPI.supports(
            f"https://api.govinfo.gov/collections/BILLS/2018-01-28T20%3A18%3A10Z?offset=0&pageSize=1000&api_key={FAKE_API_KEY}",
        )
        is True
    )
    assert (
        GovInfoAPI.supports(
            f"https://api.govinfo.gov/collections/BILLS/2018-01-28T20%3A18%3A10Z/2018-01-29T20%3A18%3A10Z?offset=0&pageSize=1000&api_key={FAKE_API_KEY}",
        )
        is True
    )
    assert (
        GovInfoAPI.supports(
            f"https://api.govinfo.gov/collections/BILLS/2018-01-28T20%3A18%3A10Z/2018-10-21T13:31:42.363926?offset=0&pageSize=1000&api_key={FAKE_API_KEY}",
        )
        is False
    )


def test_govinfo_with_data(mocker, requests_mock):
    """
    Run SQL against the adapter.
    """

    mocker.patch(
        "shillelagh.adapters.api.govinfo.requests_cache.CachedSession",
        return_value=requests.Session(),
    )

    url = f"https://api.govinfo.gov/collections/BILLS/2023-02-28T20%3A18%3A10Z/2023-03-01T20%3A18%3A10Z?offset=0&pageSize=1&api_key={FAKE_API_KEY}"
    requests_mock.get(url, json=govinfo_response)

    connection = connect(":memory:")
    cursor = connection.cursor()
    sql = f"""
        SELECT * FROM "{url}"
    """

    data = list(cursor.execute(sql))
    assert data == [
        (
            "BILLS-118hr796ih",
            datetime(2023, 3, 1, 10, 29, 21),
            "https://api.govinfo.gov/packages/BILLS-118hr796ih/summary",
            "hr",
            "Supply Chain Mapping and Monitoring Act",
            118,
            "2023-02-02",
        ),
    ]


def test_govinfo_no_data(mocker, requests_mock):
    mocker.patch(
        "shillelagh.adapters.api.govinfo.requests_cache.CachedSession",
        return_value=requests.Session(),
    )

    url = f"https://api.govinfo.gov/collections/BILLS/2018-01-28T20%3A18%3A10Z/2018-01-29T20%3A18%3A10Z?offset=0&pageSize=1000&api_key={FAKE_API_KEY}"
    requests_mock.get(url, json=govinfo_empty_response)

    connection = connect(":memory:")
    cursor = connection.cursor()
    sql = f"""
        SELECT * FROM "{url}"
    """

    data = list(cursor.execute(sql))
    assert data == []
