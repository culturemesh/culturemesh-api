from flask import Blueprint, jsonify, request, redirect, url_for
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

networks = Blueprint('network', __name__)

@networks.route("/ping")
@require_apikey
def test():
    return "pong"


def make_new_network_request(req):
    """
    This will transform a GET /networks query to a POST /new network query by including necessary request.args.
    :param req: The request object that we can update.
    :return: The updated request object.
    """
    conn = mysql.get_db()
    near_ids = request.args['near_location'].split()
    index = 0
    for singular, plural in zip(['city','region','country'],['cities','regions','countries']):
        request.args['id_' + singular + '_cur'] = near_ids[index]
        request.args[singular + '_cur'] = get_area_name(conn, 'name', plural, near_ids[index])
        index += 1
    index = 0
    if "from_location" in request.args:
        from_ids = request.args['from_location'].split()
        for singular, plural in zip(['city', 'region', 'country'], ['cities', 'regions', 'countries']):
            request.args['id_' + singular + '_origin'] = from_ids[index]
            request.args[singular + '_origin'] = get_area_name(conn, 'name', plural, from_ids[index])
            index += 1
        if near_ids[0] != -1:
            request.args['network_class'] = 'cc'
        elif near_ids[1] != -1:
            request.args['network_class'] = 'rc'
        else:
            request.args['network_class'] = 'co'
    elif "language" in request.args:
        request.args['id_language_origin'] = request.args['language']
        request.args['language_origin'] = get_area_name(conn, 'id', 'languages', request.args['language'])
        request.args['network_class'] = '_l'
    return request


def get_area_name(db_connection, column_name, table_name, id):
    """
    Fetches name from DB table given id. I also use this for languages.
    :param db_connection: Database connection (use mysql.get_db())
    :param column_name: used for column identifier
    :param table_name:
    :param id: id, -1 if supposed to be "null"
    :return: name of area.
    """
    if id == -1:
        return "null"
    cursor = db_connection.get_cursor()
    cursor.execute("SELECT 'name' FROM " + table_name + " WHERE id=%s", id)
    cursor.close()
    return cursor.fetchone()[0]


@networks.route("/networks", methods=["GET"])
@require_apikey
def get_networks():
    # Validate that we have valid input data (we need a near_location).
    if "near_location" not in request.args:
        return make_response("No near_location specified", HTTPStatus.METHOD_NOT_ALLOWED)
    near_ids = request.args["near_location"].split(",")
    # All requests will start with the same query and query for near_location.
    mysql_string_start = "SELECT * \
                          FROM networks \
                          WHERE id_country_cur=%s AND id_region_cur=%s AND id_city_cur=%s"
    # Need to check if querying a location or language network. That changes our queries.
    if "from_location" in request.args:
        near_ids.extend(request.args["from_location"].split(","))
        response = get_paginated(mysql_string_start + "AND id_country_origin=%s AND id_region_origin=%s \
                             AND id_city_origin=%s",
                             selection_fields=near_ids,
                             args=request.args,
                             order_clause="ORDER BY id DESC",
                             order_index_format="id <= %s",
                             order_arg="max_id")
    elif "language" in request.args:
        near_ids.append(request.args["language"])
        response = get_paginated(mysql_string_start + "AND language_origin=%s",
                             selection_fields=near_ids,
                             args=request.args,
                             order_clause="ORDER BY id DESC",
                             order_index_format="id <= %s",
                             order_arg="max_id")
    else:
        return make_response("No location/language query parameter", HTTPStatus.METHOD_NOT_ALLOWED)
    if response.get_json() == jsonify([]):
        # The network doesn't exist. So, let's make it!
        try:
            make_new_network_request(request.args)
            make_new_network()
            return get_networks()
        except (AttributeError, ValueError, IndexError) as e:
            return make_response("Invalid network parameters. Could not make a new network.",
                                 HTTPStatus.METHOD_NOT_ALLOWED)
    else:
        return response


@networks.route("/<network_id>", methods=["GET"])
@require_apikey
def get_network(network_id):
    return get_by_id("networks", network_id)


@networks.route("/<network_id>/posts", methods=["GET"])
@require_apikey
def get_network_posts(network_id):
    return get_paginated("SELECT * \
                         FROM posts \
                         WHERE id_network=%s",
                         selection_fields=[network_id],
                         args=request.args,
                         order_clause="ORDER BY id DESC",
                         order_index_format="id <= %s",
                         order_arg="max_id")


@networks.route("/<network_id>/post_count", methods=["GET"])
@require_apikey
def get_network_post_count(network_id):
    query = "SELECT count(*) \
             as post_count \
             from posts \
             where id_network=%s"
    return execute_single_tuple_query(query, (network_id,))


@networks.route("/<network_id>/events", methods=["GET"])
@require_apikey
def get_network_events(network_id):
    return get_paginated("SELECT * \
                          FROM events \
                          WHERE id_network=%s",
                          selection_fields=[network_id],
                          args=request.args,
                          order_clause="ORDER BY id DESC",
                          order_index_format="id <= %s",
                          order_arg="max_id")


@networks.route("/<network_id>/users", methods=["GET"])
@require_apikey
def get_network_users(network_id):
    return get_paginated("SELECT users.*, join_date \
                          FROM network_registration \
                          INNER JOIN users \
                          ON users.id = network_registration.id_user \
                          WHERE id_network=%s",
                          selection_fields=[network_id],
                          args=request.args,
                          order_clause="ORDER BY join_date DESC",
                          order_index_format="join_date <= %s",
                          order_arg="max_registration_date")


@networks.route("/<network_id>/user_count", methods=["GET"])
@require_apikey
def get_network_user_count(network_id):
    query = "SELECT count(*) \
             as user_count \
             from network_registration \
             where id_network=%s"
    return execute_single_tuple_query(query, (network_id,))


@networks.route("/new", methods=["POST"])
@require_apikey
def make_new_network():
    content_fields = ['city_cur', 'id_city_cur', \
                'region_cur', 'id_region_cur', \
                'country_cur', 'id_country_cur', \
                'city_origin', 'id_city_origin', \
                'region_origin', 'id_region_origin', \
                'country_origin', 'id_country_origin', \
                'language_origin', 'id_language_origin', \
                'network_class']
    return execute_post_by_table(request, content_fields, "networks")

