from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from api.extensions import mysql
from json.decoder import JSONDecodeError
import time
import datetime
users = Blueprint('user', __name__)

"""
Modified by Drew Gregory 04/26/18
Controller for all user endpoints. Check the Swagger spec for more information on each endpoint.
"""


@users.route("/ping")
@require_apikey
def test():
    return "pong"


@users.route("/users")
@require_apikey
def users_query():
    # Allegedly, we need to run get_data() first
    request.get_data()
    try:
        request_filter = json.loads(request.data)
    except JSONDecodeError:
        return make_response("Error: malformed request body", 405)

    connection = mysql.get_db()
    network_ids = []
    for near_loc in request_filter['near_location']:
        near_query_string = "id_city_cur=%d AND id_region_cur=%d AND id_city_cur=%d", (near_loc.city_id,
                                                                                       near_loc.region_id,
                                                                                       near_loc.country_id)
        for from_loc in request_filter['from_location']:
            # Query networks with that near and from_location
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id FROM networks WHERE %s AND id_city_origin=%d AND id_region_origin=%d AND id_country_origin=%d",
                (near_query_string, from_loc.city_id, from_loc.region_id, from_loc.country_id))
            network_ids.append(cursor.fetchall())
            cursor.commit()
            cursor.close()

        for lang in request_filter['language']:
            # Query networks with that near location and language
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM networks WHERE %s AND language_origin=%s", (near_query_string, lang))
            network_ids.append(cursor.fetchall())
            cursor.commit()
            cursor.close()
    # Now we need to get all the users subscribed to these networks.
    user_id_cursor = connection.cursor()
    user_id_cursor.execute("SELECT id_user FROM network_registration WHERE id_network IN %s", (tuple(network_ids),))
    user_ids = user_id_cursor.fetchall()
    users_cursor = connection.cursor()
    users_cursor.execute("SELECT * FROM users WHERE id IN %s", (tuple(user_ids),))
    users_res = users_cursor.fetchall()
    
    return jsonify(users_res)


@users.route("/<user_id>", methods=["GET"])
@require_apikey
def get_user(user_id):
    connection = mysql.get_db()
    user_cursor = connection.cursor()
    user_cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = user_cursor.fetchone()
    if user is not None:
        user = convert_objects([user], user_cursor.description)[0]
    user_cursor.close()
    return make_response(jsonify(user), 405 if user is None else 200)


@users.route("/<user_id>/networks", methods=["GET"])
@require_apikey
def get_user_networks(user_id):
    connection = mysql.get_db()
    count = int(request.args.get("count", 100))
    reg_cursor = connection.cursor()
    mysql_string = "SELECT id_network FROM network_registration WHERE id_user=%s"
    if "max_registration_date" in request.args:
        mysql_string += " AND DATE(join_date) < %s"
        reg_cursor.execute(mysql_string, (user_id, request.args["max_registration_date"]))
    else:
        reg_cursor.execute(mysql_string, (user_id,))
    network_ids = reg_cursor.fetchmany(count)
    reg_cursor.close()
    # SQL doesn't like empty tuples in IN
    if len(network_ids) == 0:
        return make_response(jsonify([]), 200)
    network_cursor = connection.cursor()
    network_cursor.execute('SELECT * FROM networks WHERE id IN %s', (network_ids,))
    network_arr = network_cursor.fetchall()
    # Now, we need to convert these tuples into objects with key-value pairs
    network_obj = convert_objects(network_arr, network_cursor.description)
    network_cursor.close()
    return make_response(jsonify(network_obj), 200)


@users.route("/<user_id>/posts", methods=["GET"])
@require_apikey
def get_user_posts(user_id):
    connection = mysql.get_db()
    request_count = int(request.args.get("count", 100))
    post_cursor = connection.cursor()
    # Create SQL statement based on whether max_id is set or not.
    mysql_string = "SELECT * FROM posts WHERE id_user=%s"
    if "max_id" in request.args:
        mysql_string += "AND id<=%s"
        post_cursor.execute(mysql_string, (user_id, request.args["max_id"]))
    else:
        post_cursor.execute(mysql_string, (user_id,))
    posts = post_cursor.fetchmany(int(request_count))
    posts = convert_objects(posts, post_cursor.description)
    post_cursor.close()
    return make_response(jsonify(posts), 200)


@users.route("/<user_id>/events", methods=["GET"])
@require_apikey
def get_user_events(user_id):
    # TODO: Test when there are events in existence.
    connection = mysql.get_db()
    request_count = int(request.args.get("count", 100))
    event_registration_cursor = connection.cursor()
    sql_statement = "SELECT id_event FROM event_registration WHERE job=%s AND id_guest=%s"
    if "max_id" in request.args:
        sql_statement += " AND id <= %s"
        event_registration_cursor.execute(sql_statement, (request.args["role"], user_id, request.args["max_id"]))
    else:
        event_registration_cursor.execute(sql_statement, (request.args["role"], user_id))
    event_ids = event_registration_cursor.fetchmany(request_count)
    event_registration_cursor.close()
    event_cursor = connection.cursor()
    if len(event_ids) == 0:
        return make_response(jsonify([]), 200)
    event_cursor.execute("SELECT * FROM events WHERE id IN %s", (tuple(event_ids),))
    events = convert_objects(event_cursor.fetchall(), event_cursor.description)
    event_cursor.close()
    return make_response(jsonify(events), 200)


@users.route("/<user_id>/addToEvent/<event_id>", methods=["POST"])
@require_apikey
def add_user_to_event(user_id, event_id):
    # TODO: Test when adding events is in place.
    connection = mysql.get_db()
    # First, check that event and user are valid
    if not valid_event(event_id):
        return make_response("Invalid Event Id", 405)
    if not valid_user(user_id):
        return make_response("Invalid User Id", 405)
    # Cool. Let's add that user.
    event_registration_cursor = connection.cursor()
    event_registration_cursor.execute("INSERT INTO event_registration VALUES (%s,%s,CURRENT_TIMESTAMP,host)",
                                      (user_id, event_id))
    event_registration_cursor.commit()
    event_registration_cursor.close()
    return make_response("OK", 200)


@users.route("/<user_id>/addToNetwork/<network_id>", methods=["POST"])
@require_apikey
def add_user_to_network(user_id, network_id):
    # First, check that input is valid.
    if not valid_user(user_id):
        return make_response("Invalid User Id", 405)
    if not valid_network(network_id):
        return make_response("Invalid Network Id", 405)
    connection = mysql.get_db()
    network_registration_cursor = connection.cursor()
    # "IF NOT EXISTS "
    #                                        "(SELECT * FROM network_registration WHERE id_user=%s AND id_network=%s)"
    network_registration_cursor.execute(" INSERT INTO network_registration VALUES (%s, %s, CURRENT_TIMESTAMP)",
                                        (str(user_id), str(network_id)))
    connection.commit()
    return make_response("OK for network " % network_id, 200)


def convert_objects(tuple_arr, description):
    """A DB cursor returns an array of tuples, without attribute names. This function converts these tuples into objects
    with key-value pairs.
    :param tuple_arr:  An array of tuples
    :param description: The cursor's description, which allows you to
    :return: An array of objects with attribute names according to key-value pairs"""
    obj_arr = []
    for tuple_obj in tuple_arr:
        obj_arr.append({description[index][0]: column for index, column in enumerate(tuple_obj)})
    return obj_arr


def valid_event(event_id):
    """
    This function is used to validate endpoint input. This function checks if the passed event id is a valid event id
    (there is a corresponding event with that id.)
    :param event_id: the event id.
    :return: true if valid, false if no event found.
    """
    connection = mysql.get_db()
    event_registration_check_cursor = connection.cursor()
    event_registration_check_cursor.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    possible_event = event_registration_check_cursor.fetchone()
    event_registration_check_cursor.close()
    return possible_event is not None


def valid_user(user_id):
    """
     This function is used to validate endpoint input. This function checks if the passed user id is a valid user id
    (there is a corresponding user with that id.)
    :param user_id:
    :return: true if valid, false if no user found.
    """
    connection = mysql.get_db()
    user_check = connection.cursor()
    user_check.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    possible_user = user_check.fetchone()
    user_check.close()
    return possible_user is not None


def valid_network(network_id):
    """
    This function is used to validate endpoint input. This function checks if the passed network id is a valid
    network id (there is a corresponding network with that id.)
    :param network_id:
    :return: true if valid, false if no network found.
    """
    connection = mysql.get_db()
    network_check = connection.cursor()
    network_check.execute("SELECT * FROM networks WHERE id=%s", (network_id,))
    possible_network = network_check.fetchone()
    network_check.close()
    return possible_network is not None
