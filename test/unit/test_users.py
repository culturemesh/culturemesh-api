from test.unit import client
from api import credentials
import json
import mock
from hashlib import md5
import datetime


user_def = {"username": "MyUserName3!",
            "first_name": "Human2!",
            "last_name": "Being4!",
            "email": "humanbeing@example.com",
            "password": "Password1!",
            "role": 0,
            "about_me": "",
            "gender": ""}

user_obj = user_def.copy()
user_obj['id'] = 1
user_obj['password'] = \
    md5(str(user_obj["password"]).encode('utf-8')).hexdigest()
user_obj['username'] = 'HumanBeing2!'


@mock.patch("api.apiutils.execute_insert")
@mock.patch("api.blueprints.users.controllers.get_user_by_username",
            return_value=None)
@mock.patch("api.blueprints.users.controllers.get_user_by_email",
            return_value=None)
def test_create_user(user_by_email, user_by_username, execute_insert, client):
    user_def_json = json.dumps(user_def)
    response = client.post("/user/users", data=user_def_json,
                           content_type="application/json",
                           query_string={"key": credentials.api["key"]})

    user_by_email.assert_called_with("humanbeing@example.com")
    user_by_username.assert_called_with("MyUserName3!")

    form = 'INSERT INTO users (username,first_name,last_name,email,password)' \
           '  values (%s, %s, %s, %s, %s);'
    args = ('MyUserName3!', 'Human2!', 'Being4!', 'humanbeing@example.com',
            md5(str(user_def["password"]).encode('utf-8')).hexdigest())
    execute_insert.assert_called_with(form, args)

    assert response.status_code == 200
    assert response.data.decode() == "OK"


@mock.patch("api.apiutils.execute_insert")
@mock.patch("api.blueprints.users.controllers.get_user_by_username",
            return_value=user_obj)
@mock.patch("api.blueprints.users.controllers.get_user_by_email",
            return_value=None)
def test_create_user_username_taken_fail(user_by_email, user_by_username,
                                         execute_insert, client):
    user_def_json = json.dumps(user_def)
    response = client.post("/user/users", data=user_def_json,
                           content_type="application/json",
                           query_string={"key": credentials.api["key"]})

    user_by_username.assert_called_with("MyUserName3!")
    execute_insert.assert_not_called()
    assert response.status_code == 400
    assert response.data.decode() == "Username already taken or invalid params"


@mock.patch("api.apiutils.execute_insert")
@mock.patch("api.blueprints.users.controllers.get_user_by_username",
            return_value=None)
@mock.patch("api.blueprints.users.controllers.get_user_by_email",
            return_value=user_obj)
def test_create_user_email_taken_fail(user_by_email, user_by_username,
                                      execute_insert, client):
    user_def_json = json.dumps(user_def)
    response = client.post("/user/users", data=user_def_json,
                           content_type="application/json",
                           query_string={"key": credentials.api["key"]})

    user_by_email.assert_called_with("humanbeing@example.com")
    execute_insert.assert_not_called()
    assert response.status_code == 400
    assert response.data.decode() == "Username already taken or invalid params"


description = (('id', 8, None, 20, 20, 0, False),
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
               ('fp_code', 254, None, 96, 96, 0, True))

sql_object = (2, 'CYoum23', 'Chris', 'Youm', 'upperbrain@gmail.com',
              'b53a15ae0b7d18f359dd0f5e0fa9cc7b', 0,
              datetime.datetime(2018, 7, 30, 23, 45, 5),
              datetime.datetime(2014, 6, 1, 11, 54, 27), 'M',
              'I am from Korea and working at SF as game developer.', 1, 1,
              1, 1, 1, '97657a61f23bff2b65c63c9aacf4f032',
              '1401652610_0/pp.png', None)


@mock.patch("api.apiutils.execute_get_one",
            return_value=(sql_object, description))
def test_get_user_by_id(get_one, client):
    response = client.get("/user/2",
                          query_string={"key": credentials.api["key"]})
    query = "SELECT * FROM `users` WHERE id=%s"
    get_one.assert_called_with(query, '2')
    assert response.status_code == 200
    exp = {'about_me': 'I am from Korea and working at SF as game developer.',
           'act_code': '97657a61f23bff2b65c63c9aacf4f032', 'company_news': 1,
           'confirmed': 1, 'events_interested_in': 1, 'events_upcoming': 1,
           'first_name': 'Chris', 'fp_code': None, 'gender': 'M', 'id': 2,
           'img_link': '1401652610_0/pp.png',
           'last_login': 'Sun, 01 Jun 2014 11:54:27 GMT', 'last_name': 'Youm',
           'network_activity': 1,
           'register_date': 'Mon, 30 Jul 2018 23:45:05 GMT', 'role': 0,
           'username': 'CYoum23'}
    assert response.json == exp


get_posts_obj = ((381, 2, 1, datetime.datetime(2015, 1, 17, 12, 32, 12),
                  '[b]Picture test[/b] on [link]culturemesh.com[/link]', 'o',
                  None, None, None),)
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
    response = client.get('/user/2/posts',
                          query_string={"key": credentials.api["key"]})
    query = "SELECT *                           " \
            "FROM posts                           " \
            "WHERE id_user=%sORDER BY id DESC"
    get_many.assert_called_with(query, ('2',), 100)
    assert response.status_code == 200
    exp = [{'id': 381, 'id_network': 1, 'id_user': 2, 'img_link': None,
            'post_class': 'o', 'post_date': 'Sat, 17 Jan 2015 12:32:12 GMT',
            'post_original': None,
            'post_text': '[b]Picture test[/b] on [link]culturemesh.com[/link]',
            'vid_link': None}]
    assert response.json == exp


get_net_obj = ((1, 'Palo Alto', 332851, 'California', 55833,
                'United States', 47228, None, None, 'Michigan', 56020,
                'United States', 47228, None, None, 'rc',
                datetime.datetime(2016, 1, 12, 4, 51, 19), None, 'A',
                datetime.datetime(2014, 6, 1, 12, 58, 44)),)
get_net_des = (('id', 8, None, 20, 20, 0, False),
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
               ('twitter_query_level', 254, None, 3, 3, 0, False),
               ('join_date', 7, None, 19, 19, 0, False))


@mock.patch('api.apiutils.execute_get_many',
            return_value=(get_net_obj, get_net_des))
def test_get_networks(get_many, client):
    response = client.get('/user/2/networks',
                          query_string={"key": credentials.api["key"]})
    query = "SELECT networks.*, join_date                           " \
            "FROM network_registration                           " \
            "INNER JOIN networks                           " \
            "ON networks.id = " \
            "network_registration.id_network                           " \
            "WHERE network_registration.id_user=%sORDER BY join_date DESC"
    get_many.assert_called_with(query, ('2',), 100)
    assert response.status_code == 200
    exp = [{'city_cur': 'Palo Alto', 'city_origin': None,
            'country_cur': 'United States', 'country_origin': 'United States',
            'date_added': 'Tue, 12 Jan 2016 04:51:19 GMT', 'id': 1,
            'id_city_cur': 332851, 'id_city_origin': None,
            'id_country_cur': 47228, 'id_country_origin': 47228,
            'id_language_origin': None, 'id_region_cur': 55833,
            'id_region_origin': 56020, 'img_link': None,
            'join_date': 'Sun, 01 Jun 2014 12:58:44 GMT',
            'language_origin': None, 'network_class': 'rc',
            'region_cur': 'California', 'region_origin': 'Michigan',
            'twitter_query_level': 'A'}]
    assert response.json == exp
