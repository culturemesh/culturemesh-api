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
