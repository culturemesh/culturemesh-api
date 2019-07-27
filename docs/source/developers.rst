====================
Guide for Developers
====================

--------------
Live Debugging
--------------


The server can take a while to reflect changes, so if you want to check that the
server has registered code changes and is serving the latest version, you can
use the ``/dev/note`` endpoint. This endpoint serves the contents of
``note.txt``, which you can change to display custom text. If that new text is
displayed at that endpoint, you know the server has updated to reflect your
changes.

-----
Tests
-----

Unit Tests
==========

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

Mocking Database Retrieval
--------------------------

When only a single piece of data needs to be retrieved from the database, the
``execute_get_one`` function is generally used. It accepts a MySQL query with
arguments, and it returns the object (a tuple) from the database along with a
description (also a tuple) of the object's values. This method can readily be
mocked for testing like so:

.. code-block:: python

    obj = (47228, None, 'United States')
    des = (('id', 8, None, 20, 20, 0, False),
           ('iso_a2', 254, None, 6, 6, 0, True),
           ('name', 253, None, 50, 50, 0, True))


    @mock.patch("api.apiutils.execute_get_one", return_value=(obj, des))
    def test_get_by_id(get_one, client):
        response = client.get("/47228",
                              query_string={"key": credentials.api["key"]})
        query = "SELECT * FROM `table` WHERE id=%s"
        get_one.assert_called_with(query, '47228')
        assert response.status_code == 200
        exp = {'id': 47228, 'iso_a2': None, 'name': 'United States'}
        assert response.json == exp

The mocking is performed by the ``@mock`` decorator, which specifies that the
``execute_get_one`` method will return a tuple of the ``obj`` and ``des`` tuples
defined earlier. This mimics what the database would actually return. Then, when
the endpoint is tested using ``client.get(...)``, the tuple specified in the
mocking is returned without using the database. We can then use assert
statements to check that the mocked method was called as expected and that the
returned data was processed correctly into the final JSON.

The same strategy is used to mock retrieval of multiple items
(``execute_get_many``) and of all items (``execute_get_all``).