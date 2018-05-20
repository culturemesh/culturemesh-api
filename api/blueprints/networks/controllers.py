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

@networks.route("/new_network", methods=["POST"])
@require_apikey
def make_new_network():
    content = request.get_json()
    query = "INSERT INTO network \
             (city_cur, id_city_cur, \
              region_cur, id_region_cur, \
              country_cur, id_country_cur, \
              city_origin, id_city_origin, \
              region_origin, id_region_origin, \
              country_origin, id_country_origin, \
              language_origin, id_language_origin, \
              network_class) \
             values \
             (%s, %s, \
              %s, %s, \
              %s, %s, \
              %s, %s, \
              %s, %s, \
              %s, %s, \
              %s, %s, \
              %s);"

    args = (content['city_cur'], content['id_city_cur'],
            content['region_cur'], content['id_region_cur'],
            content['country_cur'], content['id_country_cur'],
            content['city_origin'], content['id_city_origin'],
            content['region_origin'], content['id_region_origin'],
            content['country_origin'], content['id_country_origin'],
            content['language_origin'], content['id_language_origin'],
            content['network_class'])

    execute_insert(query, args)
    return make_response("OK", HTTPStatus.OK)
