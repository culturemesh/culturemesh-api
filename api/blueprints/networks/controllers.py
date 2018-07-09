from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

networks = Blueprint('network', __name__)

@networks.route("/ping")
@require_apikey
def test():
    return "pong"


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
        if response.json == jsonify([]):
            return make_response(jsonify({"param": "oooh I can do stuff with this check."}))
        return response
    elif "language" in request.args:
        near_ids.append(request.args["language"])
        return get_paginated(mysql_string_start + "AND language_origin=%s",
                             selection_fields=near_ids,
                             args=request.args,
                             order_clause="ORDER BY id DESC",
                             order_index_format="id <= %s",
                             order_arg="max_id")
    else:
        return make_response("No location/language query parameter", HTTPStatus.METHOD_NOT_ALLOWED)



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
