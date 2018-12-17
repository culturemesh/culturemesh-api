from test.unit import client
from api import credentials
import mock


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
