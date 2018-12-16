from test.unit import client
from api import credentials
import json
import mock
from hashlib import md5


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