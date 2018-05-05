from flask import Blueprint, jsonify, request, json, make_response
from http import HTTPStatus
from api import require_apikey
from api.extensions import mysql
from pymysql.err import IntegrityError

users = Blueprint('user', __name__)

"""
Modified by Drew Gregory 04/26/18
Controller for all user endpoints. Check the Swagger spec for more information on each endpoint.
"""


@users.route("/ping")
@require_apikey
def test():
    return "pong"


@users.route("/users/", methods=["GET"])
@require_apikey
def users_query():
    if "near_location" not in request.args:
        return make_response("No near location", HTTPStatus.METHOD_NOT_ALLOWED)
    count = int(request.args.get("count", 100))
    connection = mysql.get_db()
    # Parse id's into collection
    near_ids = request.args["near_location"].split(",")
    network_cursor = connection.cursor()
    near_loc_query = "id_country_cur=%s AND id_region_cur=%s AND id_city_cur=%s"
    if "language" in request.args:
        near_ids.extend([str(request.args["language"])])
        network_cursor.execute("SELECT id FROM networks WHERE " + near_loc_query + " AND id_language_origin=%s",
                               tuple(near_ids))
    elif "from_location" in request.args:
        near_ids.extend(request.args["from_location"].split(","))
        network_cursor.execute("SELECT id FROM networks WHERE " + near_loc_query + " AND " +
                               near_loc_query.replace("cur", "origin"),
                               tuple(near_ids))
    else:
        return make_response("No language/from location", HTTPStatus.METHOD_NOT_ALLOWED)
    network_ids = network_cursor.fetchall()
    network_cursor.close()
    if len(network_ids) == 0:
        return make_response(jsonify([]), HTTPStatus.OK)
    # Now we need to get all the users subscribed to these networks.
    user_id_cursor = connection.cursor()
    sql_query_string = "SELECT id_user FROM network_registration WHERE id_network IN %s"
    sql_order_string = "ORDER BY id_user DESC"
    if "max_id" in request.args:
        sql_query_string += " AND id_user<=%s"
        user_id_cursor.execute(sql_query_string + sql_order_string, (network_ids, request.args["max_id"]))
    else:
        user_id_cursor.execute(sql_query_string + sql_order_string, (network_ids,))
    user_ids = user_id_cursor.fetchmany(count)
    if len(user_ids) == 0:
        return make_response(jsonify([]), HTTPStatus.OK)
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
    return make_response(jsonify(user), HTTPStatus.METHOD_NOT_ALLOWED if user is None else HTTPStatus.OK)


@users.route("/<user_id>/networks", methods=["GET"])
@require_apikey
def get_user_networks(user_id):
    connection = mysql.get_db()
    count = int(request.args.get("count", 100))
    reg_cursor = connection.cursor()
    mysql_string = "SELECT id_network FROM network_registration WHERE id_user=%s"
    sql_string_order = "ORDER BY id_network DESC"
    if "max_registration_date" in request.args:
        mysql_string += " AND DATE(join_date) < %s"
        reg_cursor.execute(mysql_string + sql_string_order, (user_id, request.args["max_registration_date"]))
    else:
        reg_cursor.execute(mysql_string + sql_string_order, (user_id,))
    network_ids = reg_cursor.fetchmany(count)
    reg_cursor.close()
    # SQL doesn't like empty tuples in IN
    if len(network_ids) == 0:
        return make_response(jsonify([]), HTTPStatus.OK)
    network_cursor = connection.cursor()
    network_cursor.execute('SELECT * FROM networks WHERE id IN %s', (network_ids,))
    network_arr = network_cursor.fetchall()
    # Now, we need to convert these tuples into objects with key-value pairs
    network_obj = convert_objects(network_arr, network_cursor.description)
    network_cursor.close()
    return make_response(jsonify(network_obj), HTTPStatus.OK)


@users.route("/<user_id>/posts", methods=["GET"])
@require_apikey
def get_user_posts(user_id):
    connection = mysql.get_db()
    request_count = int(request.args.get("count", 100))
    post_cursor = connection.cursor()
    # Create SQL statement based on whether max_id is set or not.
    mysql_string = "SELECT * FROM posts WHERE id_user=%s"
    sql_string_order = "ORDER BY id DESC"
    if "max_id" in request.args:
        mysql_string += "AND id<=%s"
        post_cursor.execute(mysql_string + sql_string_order, (user_id, request.args["max_id"]))
    else:
        post_cursor.execute(mysql_string + sql_string_order, (user_id,))
    posts = post_cursor.fetchmany(int(request_count))
    posts = convert_objects(posts, post_cursor.description)
    post_cursor.close()
    return make_response(jsonify(posts), HTTPStatus.OK)


@users.route("/<user_id>/events", methods=["GET"])
@require_apikey
def get_user_events(user_id):
    # TODO: Test when there are events in existence.
    connection = mysql.get_db()
    request_count = int(request.args.get("count", 100))
    event_registration_cursor = connection.cursor()
    sql_statement = "SELECT id_event FROM event_registration WHERE job=%s AND id_guest=%s"
    sql_string_order = "ORDER BY id_event DESC"
    if "max_id" in request.args:
        sql_statement += " AND id <= %s"
        event_registration_cursor.execute(sql_statement + sql_string_order, (request.args["role"], user_id, request.args["max_id"]))
    else:
        event_registration_cursor.execute(sql_statement + sql_string_order, (request.args["role"], user_id))
    event_ids = event_registration_cursor.fetchmany(request_count)
    event_registration_cursor.close()
    event_cursor = connection.cursor()
    if len(event_ids) == 0:
        return make_response(jsonify([]), HTTPStatus.OK)
    event_cursor.execute("SELECT * FROM events WHERE id IN %s", (tuple(event_ids),))
    events = convert_objects(event_cursor.fetchall(), event_cursor.description)
    event_cursor.close()
    return make_response(jsonify(events), HTTPStatus.OK)


@users.route("/<user_id>/addToEvent/<event_id>", methods=["POST"])
@require_apikey
def add_user_to_event(user_id, event_id):
    # TODO: Test when adding events is in place.
    connection = mysql.get_db()
    # First, check that event and user are valid
    if not valid_event(event_id):
        return make_response("Invalid Event Id", HTTPStatus.METHOD_NOT_ALLOWED)
    if not valid_user(user_id):
        return make_response("Invalid User Id", HTTPStatus.METHOD_NOT_ALLOWED)
    # Cool. Let's add that user.
    event_registration_cursor = connection.cursor()
    event_registration_cursor.execute("INSERT INTO event_registration VALUES (%s,%s,CURRENT_TIMESTAMP,host)",
                                      (user_id, event_id))
    connection.commit()
    return make_response("OK", HTTPStatus.OK)


@users.route("/<user_id>/addToNetwork/<network_id>", methods=["POST"])
@require_apikey
def add_user_to_network(user_id, network_id):
    # First, check that input is valid.
    if not valid_user(user_id):
        return make_response("Invalid User Id", HTTPStatus.METHOD_NOT_ALLOWED)
    if not valid_network(network_id):
        return make_response("Invalid Network Id", HTTPStatus.METHOD_NOT_ALLOWED)
    connection = mysql.get_db()
    network_registration_cursor = connection.cursor()
    try:
        network_registration_cursor.execute("INSERT INTO network_registration VALUES (%s, %s, CURRENT_TIMESTAMP)",
                                        (str(user_id), str(network_id)))
    except IntegrityError:
        connection.commit()
        return make_response("User already subscribed", HTTPStatus.METHOD_NOT_ALLOWED)
    connection.commit()
    return make_response("OK", HTTPStatus.OK)


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
