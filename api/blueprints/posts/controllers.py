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
    connection = mysql.get_db()
    posts_cursor = connection.cursor()

    posts_cursor.execute('SELECT * '
                         'FROM posts '
                         'WHERE id=%s', (post_id,))

    response = make_response_from_single_tuple(posts_cursor)
    posts_cursor.close()
    return response
