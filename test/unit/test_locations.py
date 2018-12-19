from test.unit import client
from api import credentials
import mock
from mock import call


country_by_id_obj = (47228, None, 'United States', '-129.3214', '61.660733', 1,
                     None, 'USA, United States', 1)
country_by_id_des = (('id', 8, None, 20, 20, 0, False),
                     ('iso_a2', 254, None, 6, 6, 0, True),
                     ('name', 253, None, 50, 50, 0, True),
                     ('latitude', 253, None, 9, 9, 0, True),
                     ('longitude', 253, None, 9, 9, 0, True),
                     ('population', 3, None, 10, 10, 0, False),
                     ('feature_code', 253, None, 6, 6, 0, True),
                     ('tweet_terms', 253, None, 200, 200, 0, True),
                     ('tweet_terms_override', 2, None, 1, 1, 0, True))


@mock.patch("api.apiutils.execute_get_one",
            return_value=(country_by_id_obj, country_by_id_des))
def test_get_country_by_id(get_one, client):
    response = client.get("/location/countries/47228",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT * FROM `countries` WHERE id=%s"
    get_one.assert_called_with(query, '47228')
    assert response.status_code == 200
    exp = {'feature_code': None, 'id': 47228, 'iso_a2': None,
           'latitude': '-129.3214', 'longitude': '61.660733',
           'name': 'United States', 'population': 1,
           'tweet_terms': 'USA, United States', 'tweet_terms_override': 1}
    assert response.json == exp


region_by_id_obj = (56130, 'New York', 43.0003, -75.4999, 47228,
                    'United States', 1, None, None, 'USA, United States', 0, 1)
region_by_id_des = (('id', 8, None, 20, 20, 0, False),
                    ('name', 253, None, 50, 50, 0, False),
                    ('latitude', 4, None, 7, 7, 4, False),
                    ('longitude', 4, None, 7, 7, 4, False),
                    ('country_id', 8, None, 20, 20, 0, False),
                    ('country_name', 253, None, 50, 50, 0, False),
                    ('population', 3, None, 10, 10, 0, False),
                    ('feature_code', 253, None, 6, 6, 0, True),
                    ('tweet_terms', 253, None, 200, 200, 0, True),
                    ('country_tweet_terms', 253, None, 200, 200, 0, True),
                    ('tweet_terms_override', 2, None, 1, 1, 0, True),
                    ('country_tweet_terms_override', 2, None, 1, 1, 0, True))


@mock.patch("api.apiutils.execute_get_one",
            return_value=(region_by_id_obj, region_by_id_des))
def test_get_region_by_id(get_one, client):
    response = client.get("/location/regions/56130",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT * FROM `regions` WHERE id=%s"
    get_one.assert_called_with(query, '56130')
    assert response.status_code == 200
    exp = {'country_id': 47228, 'country_name': 'United States',
           'country_tweet_terms': 'USA, United States',
           'country_tweet_terms_override': 1, 'feature_code': None,
           'id': 56130, 'latitude': 43.0003, 'longitude': -75.4999,
           'name': 'New York', 'population': 1, 'tweet_terms': None,
           'tweet_terms_override': 0}
    assert response.json == exp


city_by_id_obj = (327181, 'New York City', 40.7143, -74.006, 56130,
                  'New York', 47228, 'United States', 8175133, 'PPL', None,
                  None, 'USA, United States', 0, 1, 0)
city_by_id_des = (('id', 8, None, 20, 20, 0, False),
                  ('name', 253, None, 50, 50, 0, False),
                  ('latitude', 4, None, 7, 7, 4, False),
                  ('longitude', 4, None, 7, 7, 4, False),
                  ('region_id', 8, None, 20, 20, 0, True),
                  ('region_name', 253, None, 50, 50, 0, True),
                  ('country_id', 8, None, 20, 20, 0, True),
                  ('country_name', 253, None, 50, 50, 0, True),
                  ('population', 8, None, 8, 8, 0, False),
                  ('feature_code', 253, None, 6, 6, 0, True),
                  ('tweet_terms', 253, None, 200, 200, 0, True),
                  ('region_tweet_terms', 253, None, 200, 200, 0, True),
                  ('country_tweet_terms', 253, None, 200, 200, 0, True),
                  ('region_tweet_terms_override', 2, None, 1, 1, 0, True),
                  ('country_tweet_terms_override', 2, None, 1, 1, 0, True),
                  ('tweet_terms_override', 2, None, 1, 1, 0, True))


@mock.patch("api.apiutils.execute_get_one",
            return_value=(city_by_id_obj, city_by_id_des))
def test_get_city_by_id(get_one, client):
    response = client.get("/location/cities/327181",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT * FROM `cities` WHERE id=%s"
    get_one.assert_called_with(query, '327181')
    assert response.status_code == 200
    exp = {'country_id': 47228, 'country_name': 'United States',
           'country_tweet_terms': 'USA, United States',
           'country_tweet_terms_override': 1, 'feature_code': 'PPL',
           'id': 327181, 'latitude': 40.7143, 'longitude': -74.006,
           'name': 'New York City', 'population': 8175133, 'region_id': 56130,
           'region_name': 'New York', 'region_tweet_terms': None,
           'region_tweet_terms_override': 0, 'tweet_terms': None,
           'tweet_terms_override': 0}

    assert response.json == exp


def mock_autocomplete_get_many(sql_q_format, args, count):
    cities_obj = (('North York', 135351, 21359, 44888),
                  ('Yorkton', 136221, 21392, 44888),
                  ('York', 183111, 27255, 45356),
                  ('York', 316511, 56196, 47228),
                  ('Yorkville', 322071, 55921, 47228),
                  ('West New York', 326241, 56108, 47228),
                  ('East New York', 326611, 56130, 47228),
                  ('New York City', 327181, 56130, 47228))
    cities_des = (('name', 253, None, 50, 50, 0, False),
                  ('city_id', 8, None, 20, 20, 0, False),
                  ('region_id', 8, None, 20, 20, 0, True),
                  ('country_id', 8, None, 20, 20, 0, True))
    regions_obj = (('New York', 'null', 56130, 47228),)
    regions_des = (('name', 253, None, 50, 50, 0, False),
                   ('city_id', 253, None, 4, 4, 31, False),
                   ('region_id', 8, None, 20, 20, 0, False),
                   ('country_id', 8, None, 20, 20, 0, False))
    countries_obj = ()
    countries_des = (('name', 253, None, 50, 50, 0, True),
                     ('city_id', 253, None, 4, 4, 31, False),
                     ('region_id', 253, None, 4, 4, 31, False),
                     ('country_id', 8, None, 20, 20, 0, False))
    if 'cities.name' in sql_q_format:
        return cities_obj, cities_des
    elif 'regions.name' in sql_q_format:
        return regions_obj, regions_des
    elif 'countries.name' in sql_q_format:
        return countries_obj, countries_des
    else:
        raise ValueError("Parameter sql_q_format should contain "
                         "<location type>.name")


@mock.patch('api.blueprints.locations.controllers.execute_get_many',
            side_effect=mock_autocomplete_get_many)
def test_autocomplete(get_many, client):
    search_text = 'york'
    response = client.get('/location/autocomplete',
                          query_string={'key': credentials.api['key'],
                                        'input_text': search_text})
    cit_format = "SELECT cities.name, id AS city_id, region_id, country_id " \
                 "FROM cities WHERE cities.name REGEXP %s"
    reg_format = "SELECT regions.name, 'null' AS city_id, id AS region_id, " \
                 "country_id FROM regions WHERE regions.name REGEXP %s"
    cou_format = "SELECT countries.name, 'null' AS city_id, 'null' AS " \
                 "region_id, id AS country_id FROM countries WHERE " \
                 "countries.name REGEXP %s"
    calls = [call(form, ('york',), 100) for form in
             [cit_format, reg_format, cou_format]]
    get_many.assert_has_calls(calls, any_order=False)
    assert response.status_code == 200
    exp = [{'city_id': 135351, 'country_id': 44888, 'name': 'North York',
            'region_id': 21359},
           {'city_id': 136221, 'country_id': 44888, 'name': 'Yorkton',
            'region_id': 21392},
           {'city_id': 183111, 'country_id': 45356, 'name': 'York',
            'region_id': 27255},
           {'city_id': 316511, 'country_id': 47228, 'name': 'York',
            'region_id': 56196},
           {'city_id': 322071, 'country_id': 47228, 'name': 'Yorkville',
            'region_id': 55921},
           {'city_id': 326241, 'country_id': 47228, 'name': 'West New York',
            'region_id': 56108},
           {'city_id': 326611, 'country_id': 47228, 'name': 'East New York',
            'region_id': 56130},
           {'city_id': 327181, 'country_id': 47228, 'name': 'New York City',
            'region_id': 56130},
           {'city_id': 'null', 'country_id': 47228, 'name': 'New York',
            'region_id': 56130}]
    assert response.json == exp
