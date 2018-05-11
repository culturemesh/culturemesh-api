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
