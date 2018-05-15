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
    # Validate that we have valid input data (we need a near_location.
    if "location_cur" not in request.args:
        return make_response("No location_cur specified", HTTPStatus.METHOD_NOT_ALLOWED)
    near_ids = request.args["location_cur"].split(",")
    # All requests will start with the same query and query for location_cur.
    mysql_string_start = "SELECT * \
                          FROM networks \
                          WHERE id_country_cur=%s AND id_region_cur=%s AND id_city_cur=%s"
    # Need to check if querying a location or language network. That changes our queries.
    if "location_origin" in request.args:
        return get_paginated(mysql_string_start + "AND id_country_origin=%s AND id_region_origin=%s \
                             AND id_country_origin=%s",
                             selection_fields=near_ids.extend(request.args["location_origin"].split(",")),
                             args=request.args,
                             order_clause="ORDER BY id DESC",
                             order_index_format="id <= %s",
                             order_arg="max_id")
    elif "language_origin" in request.args:
        return get_paginated(mysql_string_start + "AND language_origin=%s",
                             selection_fields=near_ids.append(request.args["language_origin"]),
                             args=request.args,
                             order_clause="ORDER BY id DESC",
                             order_index_format="id <= %s",
                             order_arg="max_id")
    else:
        make_response("No location/language_origin query parameter", HTTPStatus.METHOD_NOT_ALLOWED)



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
