from test.unit import client
from api import credentials
import mock


def test_ping(client):
    response = client.get('/language/ping',
                          query_string={"key": credentials.api["key"]})
    assert response.data.decode() == 'pong'


language_by_id_obj = (1, 'Mandarin Chinese/Putonghua', 935, 0, None, None)
language_by_id_desc = (('id', 8, None, 20, 20, 0, False),
                       ('name', 253, None, 50, 50, 0, False),
                       ('num_speakers', 3, None, 4, 4, 0, False),
                       ('added', 2, None, 1, 1, 0, False),
                       ('tweet_terms', 253, None, 200, 200, 0, True),
                       ('tweet_terms_override', 253, None, 200, 200, 0, True))


@mock.patch("api.apiutils.execute_get_one",
            return_value=(language_by_id_obj, language_by_id_desc))
def test_get_event_by_id(get_one, client):
    response = client.get("/language/1",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT * FROM `languages` WHERE id=%s"
    get_one.assert_called_with(query, '1')
    assert response.status_code == 200
    exp = {'added': 0, 'id': 1, 'name': 'Mandarin Chinese/Putonghua',
           'num_speakers': 935, 'tweet_terms': None,
           'tweet_terms_override': None}
    assert response.json == exp


autocomplete_obj = ((3, 'English', 365, 0, None, '0'),
                    (7, 'Bengali', 202, 0, None, None),
                    (18, 'French', 74, 0, None, None))
autocomplete_des = (('id', 8, None, 20, 20, 0, False),
                    ('name', 253, None, 50, 50, 0, False),
                    ('num_speakers', 3, None, 4, 4, 0, False),
                    ('added', 2, None, 1, 1, 0, False),
                    ('tweet_terms', 253, None, 200, 200, 0, True),
                    ('tweet_terms_override', 253, None, 200, 200, 0, True))


@mock.patch('api.blueprints.languages.controllers.execute_get_many',
            return_value=(autocomplete_obj, autocomplete_des))
def test_autocomplete(get_many, client):
    search_text = 'en'
    response = client.get('/language/autocomplete',
                          query_string={'key': credentials.api['key'],
                                        'input_text': search_text})
    query = "SELECT * FROM languages WHERE languages.name REGEXP %s " \
            "ORDER BY num_speakers DESC;"
    get_many.assert_called_with(query, ('en',), 20)
    assert response.status_code == 200
    exp = [{'added': 0, 'id': 3, 'name': 'English', 'num_speakers': 365,
            'tweet_terms': None, 'tweet_terms_override': '0'},
           {'added': 0, 'id': 7, 'name': 'Bengali', 'num_speakers': 202,
            'tweet_terms': None, 'tweet_terms_override': None},
           {'added': 0, 'id': 18, 'name': 'French', 'num_speakers': 74,
            'tweet_terms': None, 'tweet_terms_override': None}]
    assert response.json == exp


@mock.patch('api.blueprints.languages.controllers.execute_get_many',
            return_value=((), ()))
def test_autocomplete_no_query(get_many, client):
    response = client.get('/language/autocomplete',
                          query_string={'key': credentials.api['key']})
    get_many.assert_not_called()
    assert response.status_code == 400


@mock.patch('api.blueprints.languages.controllers.execute_get_many',
            return_value=((), ()))
def test_autocomplete_query_none(get_many, client):
    response = client.get('/language/autocomplete',
                          query_string={'key': credentials.api['key'],
                                        'input_text': None})
    get_many.assert_not_called()
    assert response.status_code == 400
    # TODO: This behavior makes the `if input_text is None` check useless
    assert "Must have valid input_text field" not in response.data.decode()


@mock.patch('api.blueprints.languages.controllers.execute_get_many',
            return_value=((), ()))
def test_autocomplete_query_none(get_many, client):
    search_text = 'nonexistentLocationQuery'
    response = client.get('/language/autocomplete',
                          query_string={'key': credentials.api['key'],
                                        'input_text': search_text})
    query = "SELECT * FROM languages WHERE languages.name REGEXP %s " \
            "ORDER BY num_speakers DESC;"
    get_many.assert_called_with(query, ('nonexistentLocationQuery',), 20)
    assert response.status_code == 200
    assert response.json == []
