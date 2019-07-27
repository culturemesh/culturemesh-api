from test.unit import client
import mock
import datetime


def test_ping(client):
    response = client.get('/network/ping')
    assert response.data.decode() == 'pong'


get_user_count_description = (('user_count', 8, None, 21, 21, 0, False),)


@mock.patch("api.apiutils.execute_get_one",
            return_value=((16,), get_user_count_description))
def test_get_user_count(get_one, client):
    response = client.get("/network/1/user_count")

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
    response = client.get("/network/1")

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
    response = client.get("/network/1/post_count")

    query = "SELECT count(*) \
             as post_count \
             from posts \
             where id_network=%s"
    get_one.assert_called_with(query, ('1',))
    assert response.status_code == 200
    exp = {'post_count': 48}
    assert response.json == exp


get_events_obj = (
    (61, 547, 1, datetime.datetime(2018, 7, 21, 1, 11, 20),
     datetime.datetime(2018, 7, 21, 1, 11, 20), 'dbbdbbd', 'ehebsbdhd', '', '',
     '', 'she\n', ''),
    (60, 547, 1, datetime.datetime(2018, 7, 21, 1, 1, 10),
     '0000-00-00 00:00:00', 'shsjd', 'djdj', '', '', '', 'snsns', ''),
    (59, 547, 1, datetime.datetime(2018, 7, 21, 0, 50, 28),
     '0000-00-00 00:00:00', 'Test Event', '100 Some Road, Orangetown, CT', '',
     '', '', "something's happening.\n\n", ''))

get_events_des = (('id', 8, None, 20, 20, 0, False),
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
            return_value=(get_events_obj, get_events_des))
def test_get_events(get_many, client):
    response = client.get("/network/547/events")
    query = "SELECT *                           " \
            "FROM events                           " \
            "WHERE id_network=%sORDER BY id DESC"
    get_many.assert_called_with(query, ('547',), 100)
    assert response.status_code == 200
    exp = [{'address_1': 'ehebsbdhd', 'address_2': '', 'city': '',
            'country': '', 'date_created': 'Sat, 21 Jul 2018 01:11:20 GMT',
            'description': 'she\n',
            'event_date': 'Sat, 21 Jul 2018 01:11:20 GMT', 'id': 61,
            'id_host': 1, 'id_network': 547, 'region': '', 'title': 'dbbdbbd'},
           {'address_1': 'djdj', 'address_2': '', 'city': '', 'country': '',
            'date_created': 'Sat, 21 Jul 2018 01:01:10 GMT',
            'description': 'snsns', 'event_date': '0000-00-00 00:00:00',
            'id': 60, 'id_host': 1, 'id_network': 547, 'region': '',
            'title': 'shsjd'},
           {'address_1': '100 Some Road, Orangetown, CT', 'address_2': '',
            'city': '', 'country': '',
            'date_created': 'Sat, 21 Jul 2018 00:50:28 GMT',
            'description': "something's happening.\n\n",
            'event_date': '0000-00-00 00:00:00', 'id': 59, 'id_host': 1,
            'id_network': 547, 'region': '', 'title': 'Test Event'}]
    assert response.json == exp


get_posts_obj = ((635, 171, 545, datetime.datetime(2018, 9, 19, 20, 34, 56),
                  'Testing making a post here!', 'o', None, None, None),)
get_posts_des = (('id', 8, None, 20, 20, 0, False),
                 ('id_user', 8, None, 20, 20, 0, True),
                 ('id_network', 8, None, 20, 20, 0, True),
                 ('post_date', 7, None, 19, 19, 0, False),
                 ('post_text', 252, None, 50331645, 50331645, 0, True),
                 ('post_class', 254, None, 3, 3, 0, False),
                 ('post_original', 8, None, 20, 20, 0, True),
                 ('vid_link', 253, None, 100, 100, 0, True),
                 ('img_link', 253, None, 100, 100, 0, True))


@mock.patch('api.apiutils.execute_get_many',
            return_value=(get_posts_obj, get_posts_des))
def test_get_posts(get_many, client):
    response = client.get("/network/545/posts")
    query = "SELECT *                          " \
            "FROM posts                          " \
            "WHERE id_network=%sORDER BY id DESC"
    get_many.assert_called_with(query, ('545',), 100)
    assert response.status_code == 200
    exp = [{'id': 635, 'id_network': 545, 'id_user': 171, 'img_link': None,
            'post_class': 'o', 'post_date': 'Wed, 19 Sep 2018 20:34:56 GMT',
            'post_original': None, 'post_text': 'Testing making a post here!',
            'vid_link': None}]
    assert response.json == exp


get_users_des = (('id', 8, None, 20, 20, 0, False),
                 ('username', 253, None, 30, 30, 0, True),
                 ('first_name', 253, None, 30, 30, 0, True),
                 ('last_name', 253, None, 30, 30, 0, True),
                 ('email', 253, None, 50, 50, 0, False),
                 ('password', 253, None, 32, 32, 0, True),
                 ('role', 2, None, 1, 1, 0, True),
                 ('register_date', 7, None, 19, 19, 0, False),
                 ('last_login', 7, None, 19, 19, 0, False),
                 ('gender', 253, None, 1, 1, 0, True),
                 ('about_me', 253, None, 500, 500, 0, True),
                 ('events_upcoming', 2, None, 1, 1, 0, True),
                 ('events_interested_in', 2, None, 1, 1, 0, True),
                 ('company_news', 2, None, 1, 1, 0, True),
                 ('network_activity', 2, None, 1, 1, 0, True),
                 ('confirmed', 1, None, 1, 1, 0, False),
                 ('act_code', 253, None, 32, 32, 0, False),
                 ('img_link', 253, None, 50, 50, 0, True),
                 ('fp_code', 254, None, 96, 96, 0, True),
                 ('join_date', 7, None, 19, 19, 0, False))
get_users_obj = ((178, 'sbdbb', 'dndn', 'dbdn', 'snsj',
                  '098f6bcd4621d373cade4e832627b4f6', None,
                  datetime.datetime(2018, 8, 21, 23, 36, 5),
                  '0000-00-00 00:00:00', None, None, None, None, None, None, 0,
                  '', None, None, datetime.datetime(2018, 8, 22, 0, 11, 42)),)


@mock.patch('api.apiutils.execute_get_many',
            return_value=(get_users_obj, get_users_des))
def test_get_users(get_many, client):
    response = client.get("/network/3161/users")
    query = "SELECT users.*, join_date                           " \
            "FROM network_registration                           " \
            "INNER JOIN users                           " \
            "ON users.id = " \
            "network_registration.id_user                           " \
            "WHERE id_network=%sORDER BY join_date DESC"
    get_many.assert_called_with(query, ('3161',), 100)
    assert response.status_code == 200
    exp = [{'about_me': None, 'act_code': '', 'company_news': None,
            'confirmed': 0, 'email': 'snsj', 'events_interested_in': None,
            'events_upcoming': None, 'first_name': 'dndn', 'fp_code': None,
            'gender': None, 'id': 178, 'img_link': None,
            'join_date': 'Wed, 22 Aug 2018 00:11:42 GMT',
            'last_login': '0000-00-00 00:00:00', 'last_name': 'dbdn',
            'network_activity': None,
            'password': '098f6bcd4621d373cade4e832627b4f6',
            'register_date': 'Tue, 21 Aug 2018 23:36:05 GMT', 'role': None,
            'username': 'sbdbb'}]
    assert response.json == exp
