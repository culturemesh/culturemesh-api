from test.unit import client
from api import credentials
import mock
import datetime


event_by_id_descrip = (('id', 8, None, 20, 20, 0, False),
                       ('id_network', 8, None, 20, 20, 0, False),
                       ('id_host', 8, None, 20, 20, 0, False),
                       ('date_created', 7, None, 19, 19, 0, False),
                       ('event_date', 12, None, 19, 19, 0, False),
                       ('title', 253, None, 50, 50, 0, False),
                       ('address_1', 253, None, 40, 40, 0, False),
                       ('address_2', 253, None, 30, 30, 0, True),
                       ('city', 253, None, 100, 100, 0, True),
                       ('country', 253, None, 50, 50, 0, True),
                       ('description', 253, None, 500, 500, 0, False),
                       ('region', 253, None, 50, 50, 0, True))
event_by_id_obj = (23, 251, 3, datetime.datetime(2014, 8, 19, 0, 10, 54),
                   datetime.datetime(2014, 9, 24, 0, 10), 'Random Event',
                   '123 Random', '', 'San Francisco', None, 'cool stuff', 'CA')


@mock.patch("api.apiutils.execute_get_one",
            return_value=(event_by_id_obj, event_by_id_descrip))
def test_get_event_by_id(get_one, client):
    response = client.get("/event/23",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT * FROM `events` WHERE id=%s"
    get_one.assert_called_with(query, '23')
    assert response.status_code == 200
    exp = {'address_1': '123 Random', 'address_2': '', 'city': 'San Francisco',
           'country': None, 'date_created': 'Tue, 19 Aug 2014 00:10:54 GMT',
           'description': 'cool stuff',
           'event_date': 'Wed, 24 Sep 2014 00:10:00 GMT', 'id': 23,
           'id_host': 3, 'id_network': 251, 'region': 'CA',
           'title': 'Random Event'}
    assert response.json == exp


@mock.patch("api.apiutils.execute_get_one",
            return_value=((0,), (('reg_count', 8, None, 21, 21, 0, False),)))
def test_get_reg_count(get_one, client):
    response = client.get("/event/23/reg_count",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT count(*) \
             as reg_count \
             from event_registration \
             where id_event=%s"
    get_one.assert_called_with(query, ('23',))
    assert response.status_code == 200
    assert response.json == {'reg_count': 0}


test_get_reg_des = (('id_guest', 8, None, 20, 20, 0, False),
                    ('id_event', 8, None, 20, 20, 0, False),
                    ('date_registered', 7, None, 19, 19, 0, False),
                    ('job', 253, None, 50, 50, 0, True))
test_get_reg_obj = (
    (171, 125, datetime.datetime(2018, 9, 19, 11, 13, 43), 'guest'),
    (172, 125, datetime.datetime(2018, 9, 7, 23, 48, 7), 'host'))


@mock.patch('api.apiutils.execute_get_many',
            return_value=(test_get_reg_obj, test_get_reg_des))
def test_get_reg(get_many, client):
    response = client.get("/event/125/reg",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT *                           " \
            "FROM event_registration                           " \
            "WHERE id_event=%sORDER BY date_registered DESC"
    get_many.assert_called_with(query, ('125',), 100)
    assert response.status_code == 200
    exp = [{'date_registered': 'Wed, 19 Sep 2018 11:13:43 GMT', 'id_event': 125,
            'id_guest': 171, 'job': 'guest'},
           {'date_registered': 'Fri, 07 Sep 2018 23:48:07 GMT', 'id_event': 125,
            'id_guest': 172, 'job': 'host'}]
    assert response.json == exp


@mock.patch('api.apiutils.execute_get_many',
            return_value=((), test_get_reg_des))
def test_get_reg_empty(get_many, client):
    response = client.get("/event/23/reg",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT *                           " \
            "FROM event_registration                           " \
            "WHERE id_event=%sORDER BY date_registered DESC"
    get_many.assert_called_with(query, ('23',), 100)
    assert response.status_code == 200
    exp = []
    assert response.json == exp
