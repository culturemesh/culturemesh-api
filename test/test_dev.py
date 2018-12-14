from hypothesis import given
from hypothesis.strategies import text
from hypothesis import assume
from test import client

"""Tests for developer endpoints defined in :py:class:`api.controllers.dev`

"""

NOTE_TEST_STRING = "Hi, this is 1 note!"


def test_meta_write_to_note_file(client):
    with open(client.application.config["NOTE_PATH"], "w") as note_file:
        note_file.write(NOTE_TEST_STRING)

    with open(client.application.config["NOTE_PATH"], "r") as note_file:
        assert note_file.read() == NOTE_TEST_STRING


def test_note_returns_file_contents(client):
    with open(client.application.config["NOTE_PATH"], "w") as note_file:
        note_file.write(NOTE_TEST_STRING)
    assert client.get("/dev/note").data.decode() == NOTE_TEST_STRING


@given(test_string=text())
def test_note_returns_any_file_contents(client, test_string):
    assume('\r' not in test_string)
    with open(client.application.config["NOTE_PATH"], "w") as note_file:
        note_file.write(test_string)
    assert client.get("/dev/note").data.decode() == test_string
