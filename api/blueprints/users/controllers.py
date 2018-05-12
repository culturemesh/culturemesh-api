from flask import Blueprint, jsonify, request, json, make_response
from http import HTTPStatus
from api import require_apikey
from api.extensions import mysql
from api.apiutils import *
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
    user_id_cursor.close()
    if len(user_ids) == 0:
        return make_response(jsonify([]), HTTPStatus.OK)
    users_cursor = connection.cursor()
    users_cursor.execute("SELECT * FROM users WHERE id IN %s", (tuple(user_ids),))
    users_obj = convert_objects(users_cursor.fetchall(), users_cursor.description)
    users_cursor.close()
    return make_response(jsonify(users_obj), HTTPStatus.OK)


@users.route("/<user_id>", methods=["GET"])
@require_apikey
def get_user(user_id):
    return get_by_id("users", user_id)


@users.route("/<user_id>/networks", methods=["GET"])
@require_apikey
def get_user_networks(user_id):
    return get_paginated("SELECT networks.*, join_date \
                          FROM network_registration \
                          INNER JOIN networks \
                          ON networks.id = network_registration.id_network \
                          WHERE network_registration.id_user=%s",
                          selection_fields=[user_id],
                          args=request.args,
                          order_clause="ORDER BY id_network DESC",
                          order_index_format="join_date <= %s",
                          order_arg="max_registration_date")


@users.route("/<user_id>/posts", methods=["GET"])
@require_apikey
def get_user_posts(user_id):
    return get_paginated("SELECT * \
                          FROM posts \
                          WHERE id_user=%s",
                          selection_fields=[user_id],
                          args=request.args,
                          order_clause="ORDER BY id DESC",
                          order_index_format="id <= %s",
                          order_arg="max_id")


@users.route("/<user_id>/events", methods=["GET"])
@require_apikey
def get_user_events(user_id):
    # TODO: Test when there are events in existence.
    return get_paginated("SELECT events.* \
                          FROM event_registration \
                          INNER JOIN events \
                          ON events.id = event_registration.id_event \
                          WHERE event_registration.id_guest=%s AND event_registration.job=%s",
                          selection_fields=[user_id, request.args["role"]],
                          args=request.args,
                          order_clause="ORDER BY id_event DESC",
                          order_index_format="id <= %s",
                          order_arg="max_id")


@users.route("/<user_id>/addToEvent/<event_id>", methods=["POST"])
@require_apikey
def add_user_to_event(user_id, event_id):
    # TODO: Test when adding events is in place.
    connection = mysql.get_db()
    # First, check that event and user are valid
    if not event_exists(event_id):
        return make_response("Invalid Event Id", HTTPStatus.METHOD_NOT_ALLOWED)
    if not user_exists(user_id):
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
    if not user_exists(user_id):
        return make_response("Invalid User Id", HTTPStatus.METHOD_NOT_ALLOWED)
    if not network_exists(network_id):
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

