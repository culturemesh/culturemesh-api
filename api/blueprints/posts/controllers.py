from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

posts = Blueprint('post', __name__)

@posts.route("/ping")
@require_apikey
def test():
    return "pong"

@posts.route("/<post_id>", methods=["GET"])
@require_apikey
def get_post(post_id):
    return get_by_id("posts", post_id)


@posts.route("/<post_id>/replies", methods=["GET"])
@require_apikey
def get_post_replies(post_id):
    return get_paginated("SELECT post_replies.* \
                          FROM posts \
                          INNER JOIN post_replies \
                          ON posts.id = post_replies.id_parent \
                          WHERE posts.id=%s",
                          selection_fields=[post_id],
                          args=request.args,
                          order_clause="ORDER BY id DESC",
                          order_index_format="post_replies.id <= %s",
                          order_arg="max_id")

@posts.route("/new", methods=["POST"])
@require_apikey
def make_new_post():
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
