from test.unit import client
import mock
import datetime
import json
from mock import call


def test_ping(client):
    response = client.get('/event/ping')
    assert response.data.decode() == 'pong'


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
    response = client.get("/event/23")
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
    response = client.get("/event/23/reg_count")
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
    response = client.get("/event/125/reg")
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
    response = client.get("/event/23/reg")
    query = "SELECT *                           " \
            "FROM event_registration                           " \
            "WHERE id_event=%sORDER BY date_registered DESC"
    get_many.assert_called_with(query, ('23',), 100)
    assert response.status_code == 200
    exp = []
    assert response.json == exp


new_event_spec = {"id_network": 1,
                  "id_host": 2,
                  "event_date": "2018-12-24T22:17:30.900Z",
                  "title": "Title!",
                  "address_1": "Address1",
                  "address_2": "Address2",
                  "country": "Country",
                  "city": "City",
                  "region": "Region",
                  "description": "The Event Description!"}


new_event_obj = (65,)
new_event_def = (('id', 8, None, 20, 20, 0, False),)


@mock.patch('api.apiutils.execute_insert')
@mock.patch('api.blueprints.users.utils.execute_insert')
@mock.patch('api.blueprints.events.controllers.execute_get_one',
            return_value=(new_event_obj, new_event_def))
@mock.patch('api.blueprints.events.controllers.get_curr_user_id',
            return_value=2)
@mock.patch('api.blueprints.accounts.controllers.auth.authenticate',
            return_value=True)
def test_new_event(auth, get_user_id, get_one, execute_insert_events,
                   execute_insert_apiutils, client):
    new_event_json = json.dumps(new_event_spec)
    response = client.post('/event/new', data=new_event_json,
                           content_type='application/json')
    auth.assert_called_with(None, None)
    get_user_id.assert_called_with()

    insert_query = 'INSERT INTO events (id_network,id_host,event_date,' \
                   'title,address_1,address_2,country,city,region,' \
                   'description)  values ' \
                   '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
    insert_args = (1, 2, '2018-12-24T22:17:30.900Z', 'Title!', 'Address1',
                   'Address2', 'Country', 'City', 'Region',
                   'The Event Description!')

    execute_insert_apiutils.assert_called_with(insert_query, insert_args)

    join_event_query = "INSERT INTO event_registration VALUES " \
                       "(%s,%s,CURRENT_TIMESTAMP, %s)"
    join_event_args = (2, 65, 'host')

    execute_insert_events.assert_called_with(join_event_query, join_event_args)

    get_event_id_query = "SELECT id FROM events WHERE id_host=%s AND id_" \
                         "network=%s ORDER BY id DESC LIMIT 1"
    get_event_id_args = (2, 1)
    get_one.assert_called_with(get_event_id_query, get_event_id_args)
    assert response.status_code == 200
    assert response.data.decode() == 'OK'


new_event_spec['id'] = 64
update_event_obj = (64, 1, 157, datetime.datetime(2018, 7, 24, 19, 36, 2),
                    datetime.datetime(2018, 7, 24, 7, 5), 'Test Event 2',
                    'Address1', '', 'City', 'Country',
                    "let;I'll;ajsdfila;sgr", 'Region')
update_event_des = (('id', 8, None, 20, 20, 0, False),
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


@mock.patch('api.apiutils.execute_insert')
@mock.patch('api.apiutils.execute_get_one',
            return_value=(update_event_obj, update_event_des))
@mock.patch('api.blueprints.events.controllers.get_curr_user_id',
            return_value=157)
@mock.patch('api.blueprints.accounts.controllers.auth.authenticate',
            return_value=True)
def test_update_event(auth, get_id, get_one, insert, client):
    new_event_json = json.dumps(new_event_spec)
    response = client.put('/event/new', data=new_event_json,
                          content_type='application/json')
    auth.assert_called_with(None, None)
    get_id.assert_called_with()

    get_one_format = 'SELECT * FROM `events` WHERE id=%s'
    get_one.assert_called_with(get_one_format, 64)

    insert_format = 'UPDATE events SET id_network=%s, id_host=%s, ' \
                    'event_date=%s, title=%s, address_1=%s, address_2=%s, ' \
                    'country=%s, city=%s, region=%s, description=%s WHERE id=%s'
    insert_args = (1, 157, '2018-12-24T22:17:30.900Z', 'Title!', 'Address1',
                   'Address2', 'Country', 'City', 'Region',
                   'The Event Description!', 64)
    insert.assert_called_with(insert_format, insert_args)

    assert response.status_code == 200
    assert response.data.decode() == 'OK'


@mock.patch('api.blueprints.events.controllers.execute_mod')
@mock.patch('api.blueprints.accounts.controllers.auth.authenticate',
            return_value=True)
def test_delete_event(auth, mod, client):
    event_id = 1
    response = client.delete('/event/delete', query_string={'id': event_id})
    auth.assert_called_with(None, None)
    calls = [call('DELETE FROM event_registration WHERE id_event=%s',
                  str(event_id)),
             call('DELETE FROM events WHERE id=%s', str(event_id))]
    mod.assert_has_calls(calls, any_order=False)
    assert response.status_code == 200
    assert response.data.decode() == 'OK'


get_by_net_usr_obj = ((157, 122, datetime.datetime(2018, 8, 26, 21, 26, 37),
                       'host', 122, 1, 157,
                       datetime.datetime(2018, 8, 26, 21, 26, 37),
                       datetime.datetime(2018, 8, 26, 18, 52, 36),
                       'New Arrival Information Session', '123 West Street',
                       None, 'SomeCity', 'ThisCountry',
                       'Are you new to the area? Come to ask questions and get '
                       'advice from our panel of residents.', 'MyRegion'),
                      (157, 121, datetime.datetime(2018, 10, 21, 16, 25, 13),
                       'guest', 121, 1, 157,
                       datetime.datetime(2018, 8, 26, 21, 23, 32),
                       datetime.datetime(2018, 8, 26, 16, 11, 31),
                       'Live Music at the Park', '123 North Street', None,
                       'AnyCity', 'ThisCountry',
                       'Come enjoy an afternoon at the park listening to the '
                       'songs of our shared history.', 'SomeRegion'),
                      (157, 120, datetime.datetime(2018, 8, 26, 21, 21, 49),
                       'host', 120, 1, 157,
                       datetime.datetime(2018, 8, 26, 21, 21, 49),
                       datetime.datetime(2018, 8, 26, 21, 19, 47),
                       'Community Picnic', '123 Main Street', None, 'AnyTown',
                       'ThisCountry',
                       'Come for a celebration with food from home and new '
                       'friends!', 'MyState'))
get_by_net_usr_def = (('id_guest', 8, None, 20, 20, 0, False),
                      ('id_event', 8, None, 20, 20, 0, False),
                      ('date_registered', 7, None, 19, 19, 0, False),
                      ('job', 253, None, 50, 50, 0, True),
                      ('id', 8, None, 20, 20, 0, False),
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


@mock.patch('api.apiutils.execute_get_many',
            return_value=(get_by_net_usr_obj, get_by_net_usr_def))
@mock.patch('api.blueprints.events.controllers.get_curr_user_id',
            return_value=157)
@mock.patch('api.blueprints.accounts.controllers.auth.authenticate',
            return_value=True)
def test_get_events_by_network_user(auth, get_user_id, get_many, client):
    response = client.get('/event/currentUserEventsByNetwork/1')
    auth.assert_called_with(None, None)
    get_user_id.assert_called_with()

    query = 'SELECT *                          ' \
            'FROM event_registration INNER JOIN events ON events.id = ' \
            'event_registration.id_event                          ' \
            'WHERE (id_guest=%s OR id_host=%s) AND id_network=%sORDER BY ' \
            'id DESC'
    args = (157, 157, '1')
    get_many.assert_called_with(query, args, 100)
    assert response.status_code == 200
    exp = [{'address_1': '123 West Street', 'address_2': None,
            'city': 'SomeCity', 'country': 'ThisCountry',
            'date_created': 'Sun, 26 Aug 2018 21:26:37 GMT',
            'date_registered': 'Sun, 26 Aug 2018 21:26:37 GMT',
            'description': 'Are you new to the area? Come to ask questions '
                           'and get advice from our panel of residents.',
            'event_date': 'Sun, 26 Aug 2018 18:52:36 GMT', 'id': 122,
            'id_event': 122, 'id_guest': 157, 'id_host': 157, 'id_network': 1,
            'job': 'host', 'region': 'MyRegion',
            'title': 'New Arrival Information Session'},
           {'address_1': '123 North Street', 'address_2': None,
            'city': 'AnyCity', 'country': 'ThisCountry',
            'date_created': 'Sun, 26 Aug 2018 21:23:32 GMT',
            'date_registered': 'Sun, 21 Oct 2018 16:25:13 GMT',
            'description': 'Come enjoy an afternoon at the park listening to '
                           'the songs of our shared history.',
            'event_date': 'Sun, 26 Aug 2018 16:11:31 GMT', 'id': 121,
            'id_event': 121, 'id_guest': 157, 'id_host': 157, 'id_network': 1,
            'job': 'guest', 'region': 'SomeRegion',
            'title': 'Live Music at the Park'},
           {'address_1': '123 Main Street', 'address_2': None,
            'city': 'AnyTown', 'country': 'ThisCountry',
            'date_created': 'Sun, 26 Aug 2018 21:21:49 GMT',
            'date_registered': 'Sun, 26 Aug 2018 21:21:49 GMT',
            'description': 'Come for a celebration with food from home and new '
                           'friends!',
            'event_date': 'Sun, 26 Aug 2018 21:19:47 GMT', 'id': 120,
            'id_event': 120, 'id_guest': 157, 'id_host': 157, 'id_network': 1,
            'job': 'host', 'region': 'MyState', 'title': 'Community Picnic'}]
    assert response.json == exp
