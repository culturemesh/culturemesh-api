from test.unit import client
from api import credentials
import mock
import datetime


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
    response = client.get('/post/88',
                          query_string={"key": credentials.api["key"]})
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
    response = client.get('/post/reply/207',
                          query_string={"key": credentials.api["key"]})
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
    response = client.get('post/88/reply_count',
                         query_string={'key': credentials.api['key']})
    query = "SELECT count(*) \
             as reply_count \
             from post_replies \
             where id_parent=%s"
    get_one.assert_called_with(query, ('88',))
    assert response.status_code == 200
    exp = {'reply_count': 5}
    assert response.json == exp
