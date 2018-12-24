from test.unit import client
import mock
import datetime
import json


def test_ping(client):
    response = client.get('/post/ping')
    assert response.data.decode() == 'pong'


post_by_id_obj = (88, 3, 1, datetime.datetime(2014, 7, 27, 12, 15, 2),
                  'Hey Michiganders in Palo Alto!', 'o', None, '', '')
post_by_id_des = (('id', 8, None, 20, 20, 0, False),
                  ('id_user', 8, None, 20, 20, 0, True),
                  ('id_network', 8, None, 20, 20, 0, True),
                  ('post_date', 7, None, 19, 19, 0, False),
                  ('post_text', 252, None, 50331645, 50331645, 0, True),
                  ('post_class', 254, None, 3, 3, 0, False),
                  ('post_original', 8, None, 20, 20, 0, True),
                  ('vid_link', 253, None, 100, 100, 0, True),
                  ('img_link', 253, None, 100, 100, 0, True))


@mock.patch('api.apiutils.execute_get_one',
            return_value=(post_by_id_obj, post_by_id_des))
def test_get_post_by_id(get_one, client):
    response = client.get('/post/88')
    query = "SELECT * FROM `posts` WHERE id=%s"
    get_one.assert_called_with(query, '88')
    assert response.status_code == 200
    exp = {'id': 88, 'id_network': 1, 'id_user': 3, 'img_link': '',
           'post_class': 'o', 'post_date': 'Sun, 27 Jul 2014 12:15:02 GMT',
           'post_original': None, 'post_text': 'Hey Michiganders in Palo Alto!',
           'vid_link': ''}
    assert response.json == exp


reply_by_id_obj = (207, 88, 6, 1, datetime.datetime(2014, 7, 28, 20, 12, 51),
                   'Hey Ken, how is Palo Alto?')
reply_by_id_des = (('id', 8, None, 20, 20, 0, False),
                   ('id_parent', 8, None, 20, 20, 0, False),
                   ('id_user', 8, None, 20, 20, 0, False),
                   ('id_network', 8, None, 20, 20, 0, False),
                   ('reply_date', 7, None, 19, 19, 0, False),
                   ('reply_text', 252, None, 50331645, 50331645, 0, False))


@mock.patch('api.apiutils.execute_get_one',
            return_value=(reply_by_id_obj, reply_by_id_des))
def test_get_reply_by_id(get_one, client):
    response = client.get('/post/reply/207')
    query = "SELECT * FROM `post_replies` WHERE id=%s"
    get_one.assert_called_with(query, '207')
    assert response.status_code == 200
    exp = {'id': 207, 'id_network': 1, 'id_parent': 88, 'id_user': 6,
           'reply_date': 'Mon, 28 Jul 2014 20:12:51 GMT',
           'reply_text': 'Hey Ken, how is Palo Alto?'}
    assert response.json == exp


@mock.patch('api.apiutils.execute_get_one',
            return_value=((5,), (('reply_count', 8, None, 21, 21, 0, False),)))
def test_get_reply_count(get_one, client):
    response = client.get('post/88/reply_count')
    query = "SELECT count(*) \
             as reply_count \
             from post_replies \
             where id_parent=%s"
    get_one.assert_called_with(query, ('88',))
    assert response.status_code == 200
    exp = {'reply_count': 5}
    assert response.json == exp


get_replies_obj = ((424, 88, 2, 1, datetime.datetime(2018, 7, 5, 22, 41, 49),
                    "hey..... what's up? s dndndmdmxndndndndndndnddndndndndn"
                    "dndndndbdbdnndndndndndndndndndndndndnn<i>djdjdkdkdkdkdkd"
                    "mdmmdmdmdmdmdmdndbdbdbdbdbdnnddnndndndndndndndbdnndndndnd"
                    "ndndnndndndndndndndndnndndnd</i>ndndndndnnddnndndndkdkdnd"
                    "bdnndndndndndndndnndndndndndndndnndndnd\n"),
                   (238, 88, 71, 1, datetime.datetime(2014, 8, 20, 12, 21, 35),
                    'Harro :) '),
                   (209, 88, 3, 1,
                    datetime.datetime(2014, 7, 30, 18, 50, 29),
                    'This would be a good page to get together & coordinate '
                    'outings for when Michigan-based sports teams are in the '
                    'area (e.g. Pistons, Tigers, Red Wings, Lions, Spartans, '
                    'Wolverines).'),
                   (208, 88, 3, 1, datetime.datetime(2014, 7, 30, 18, 43, 20),
                    "@Andrew, it's not too bad at all ;)"),
                   (207, 88, 6, 1, datetime.datetime(2014, 7, 28, 20, 12, 51),
                    'Hey Ken, how is Palo Alto?'))
get_replies_des = (('id', 8, None, 20, 20, 0, False),
                   ('id_parent', 8, None, 20, 20, 0, False),
                   ('id_user', 8, None, 20, 20, 0, False),
                   ('id_network', 8, None, 20, 20, 0, False),
                   ('reply_date', 7, None, 19, 19, 0, False),
                   ('reply_text', 252, None, 50331645, 50331645, 0, False))


@mock.patch('api.apiutils.execute_get_many',
            return_value=(get_replies_obj, get_replies_des))
def test_get_replies(get_many, client):
    response = client.get('/post/88/replies')
    query = "SELECT post_replies.*                           " \
            "FROM posts                           " \
            "INNER JOIN post_replies                           " \
            "ON posts.id = post_replies.id_parent                           " \
            "WHERE posts.id=%sORDER BY id DESC"
    get_many.assert_called_with(query, ('88',), 100)
    assert response.status_code == 200
    exp = [{'id': 424, 'id_network': 1, 'id_parent': 88, 'id_user': 2,
            'reply_date': 'Thu, 05 Jul 2018 22:41:49 GMT',
            'reply_text': "hey..... what's up? s dndndmdmxndndndndndndnddndndnd"
                          "ndndndndndbdbdnndndndndndndndndndndndndnn<i>djdjdkdk"
                          "dkdkdkdmdmmdmdmdmdmdmdndbdbdbdbdbdnnddnndndndndndndn"
                          "dbdnndndndndndndnndndndndndndndndnndndnd</i>ndndndnd"
                          "nnddnndndndkdkdndbdnndndndndndndndnndndndndndndndnnd"
                          "ndnd\n"},
           {'id': 238, 'id_network': 1, 'id_parent': 88, 'id_user': 71,
            'reply_date': 'Wed, 20 Aug 2014 12:21:35 GMT',
            'reply_text': 'Harro :) '},
           {'id': 209, 'id_network': 1, 'id_parent': 88, 'id_user': 3,
            'reply_date': 'Wed, 30 Jul 2014 18:50:29 GMT',
            'reply_text': 'This would be a good page to get together & '
                          'coordinate outings for when Michigan-based sports '
                          'teams are in the area (e.g. Pistons, Tigers, Red '
                          'Wings, Lions, Spartans, Wolverines).'},
           {'id': 208, 'id_network': 1, 'id_parent': 88, 'id_user': 3,
            'reply_date': 'Wed, 30 Jul 2014 18:43:20 GMT',
            'reply_text': "@Andrew, it's not too bad at all ;)"},
           {'id': 207, 'id_network': 1, 'id_parent': 88, 'id_user': 6,
            'reply_date': 'Mon, 28 Jul 2014 20:12:51 GMT',
            'reply_text': 'Hey Ken, how is Palo Alto?'}]
    assert response.json == exp


new_post_def = {'id_network': 1,
                'post_text': 'New Post',
                'vid_link': 'videoLink',
                'img_link': 'imageLink'}
new_post_json = json.dumps(new_post_def)


@mock.patch('api.apiutils.execute_insert')
@mock.patch('api.blueprints.posts.controllers.get_curr_user_id', return_value=1)
@mock.patch('api.blueprints.accounts.controllers.auth.authenticate',
            return_value=True)
def test_create_post(auth, get_user_id, execute_insert, client):
    response = client.post('/post/new', data=new_post_json,
                           content_type='application/json')
    auth.assert_called_with(None, None)
    get_user_id.assert_called_with()
    query = 'INSERT INTO posts ' \
            '(id_user,id_network,post_text,vid_link,img_link)  values ' \
            '(%s, %s, %s, %s, %s);'
    args = (1, 1, 'New Post', 'videoLink', 'imageLink')
    execute_insert.assert_called_with(query, args)

    assert response.status_code == 200
    assert response.data.decode() == 'OK'
