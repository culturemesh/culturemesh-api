from test.unit import client
from api import credentials
import mock
import datetime


get_user_count_description = (('user_count', 8, None, 21, 21, 0, False),)


@mock.patch("api.apiutils.execute_get_one",
            return_value=((16,), get_user_count_description))
def test_get_user_count(get_one, client):
    response = client.get("/network/1/user_count",
                          query_string={"key": credentials.api["key"]})

    query = "SELECT count(*) \
             as user_count \
             from network_registration \
             where id_network=%s"
    get_one.assert_called_with(query, ('1',))
    assert response.status_code == 200
    exp = {'user_count': 16}
    assert response.json == exp


get_net_by_id_descrip = (('id', 8, None, 20, 20, 0, False),
                         ('city_cur', 253, None, 50, 50, 0, True),
                         ('id_city_cur', 8, None, 20, 20, 0, True),
                         ('region_cur', 253, None, 50, 50, 0, True),
                         ('id_region_cur', 8, None, 20, 20, 0, True),
                         ('country_cur', 253, None, 50, 50, 0, False),
                         ('id_country_cur', 8, None, 20, 20, 0, False),
                         ('city_origin', 253, None, 50, 50, 0, True),
                         ('id_city_origin', 8, None, 20, 20, 0, True),
                         ('region_origin', 253, None, 50, 50, 0, True),
                         ('id_region_origin', 8, None, 20, 20, 0, True),
                         ('country_origin', 253, None, 50, 50, 0, True),
                         ('id_country_origin', 8, None, 20, 20, 0, True),
                         ('language_origin', 253, None, 50, 50, 0, True),
                         ('id_language_origin', 8, None, 20, 20, 0, True),
                         ('network_class', 254, None, 6, 6, 0, False),
                         ('date_added', 7, None, 19, 19, 0, False),
                         ('img_link', 253, None, 50, 50, 0, True),
                         ('twitter_query_level', 254, None, 3, 3, 0, False))
get_net_by_id_sql_obj = (1, 'Palo Alto', 332851, 'California', 55833,
                         'United States', 47228, None, None, 'Michigan', 56020,
                         'United States', 47228, None, None, 'rc',
                         datetime.datetime(2016, 1, 12, 4, 51, 19), None, 'A')


@mock.patch("api.apiutils.execute_get_one",
            return_value=(get_net_by_id_sql_obj, get_net_by_id_descrip))
def test_get_network_by_id(get_one, client):
    response = client.get("/network/1",
                          query_string={"key": credentials.api["key"]})

    query = "SELECT * FROM `networks` WHERE id=%s"
    get_one.assert_called_with(query, '1')
    exp = {'city_cur': 'Palo Alto',
           'city_origin': None,
           'country_cur': 'United States',
           'country_origin': 'United States',
           'date_added': 'Tue, 12 Jan 2016 04:51:19 GMT',
           'id': 1,
           'id_city_cur': 332851,
           'id_city_origin': None,
           'id_country_cur': 47228,
           'id_country_origin': 47228,
           'id_language_origin': None,
           'id_region_cur': 55833,
           'id_region_origin': 56020,
           'img_link': None,
           'language_origin': None,
           'network_class': 'rc',
           'region_cur': 'California',
           'region_origin': 'Michigan',
           'twitter_query_level': 'A'}
    assert response.status_code == 200
    assert response.json == exp


get_post_count_description = (('post_count', 8, None, 21, 21, 0, False),)


@mock.patch("api.apiutils.execute_get_one",
            return_value=((48,), get_post_count_description))
def test_get_post_count(get_one, client):
    response = client.get("/network/1/post_count",
                          query_string={"key": credentials.api["key"]})

    query = "SELECT count(*) \
             as post_count \
             from posts \
             where id_network=%s"
    get_one.assert_called_with(query, ('1',))
    assert response.status_code == 200
    exp = {'post_count': 48}
    assert response.json == exp
