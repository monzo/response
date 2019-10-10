from unittest import mock

import pytest

from response.core.util import sanitize


def test_sanitise_handles_none():
    try:
        sanitize(None)
    except TypeError:
        pytest.fail("Unexpected TypeError handling None")


def test_sanitise_sends_sends_to_bleach():
    with mock.patch("bleach.clean", return_value="good text string"):
        actual = sanitize("bad text string")
        assert actual == "good text string"
