====================
Guide for Developers
====================

Live Debugging
==============

The server can take a while to reflect changes, so if you want to check that the
server has registered code changes and is serving the latest version, you can
use the ``/dev/note`` endpoint. This endpoint serves the contents of
``note.txt``, which you can change to display custom text. If that new text is
displayed at that endpoint, you know the server has updated to reflect your
changes.

Tests
=====

Unit Tests
----------

Unit tests are stored in the ``/test/unit/`` directory. They can be executed
by running the ``test.sh`` file. As unit tests, these do not cover interactions
with resources outside this repository (e.g. the MySQL database). Instead, the
code that would normally perform this interaction has been isolated into
functions that are mocked by the tests. This mocking defines the function's
response, prevents the function from actually running, and lets the test code
assert that the function was called with particular parameters.

These tests serve to verify that the code works as expected. They also provide
a form of documentation, as they define the expected inputs and outputs of many
functions. Tests are a great place to look for detailed specifications of
expected function use and behavior.